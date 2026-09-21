from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

from sklearn.metrics import roc_auc_score

from .conformal import COMPONENT_NAMES
from .data import cap_open_set_data, encode_known_labels, load_rotation
from .direct_baselines import DIRECT_BASELINE_METHODS, run_direct_baseline
from .fdr import (
    evaluate_fdr_curve,
    evaluate_fixed_far_curve,
    mondrian_group_diagnostics,
    null_pvalue_diagnostics,
    stratified_calibration_split,
)
from .models import DEFAULT_PROFILE, PROFILES
from .run import fit_and_infer_hedl, seed_everything


DEFAULT_METHODS = ("hedl", "closr", "efc", "renoir_dml", "ais_nids", "usfad")
DEFAULT_PREVALENCES = (0.5, 0.25, 0.1, 0.05, 0.01, 0.001)
DEFAULT_Q_LEVELS = (0.05, 0.1, 0.2)

def _preferred_key(values: tuple[float, ...], preferred: float) -> str:
    value = preferred if preferred in values else values[0]
    return str(value)

def _deployment_assessment(
    diagnostics: dict[str, object],
    curve: dict[str, object],
    prevalences: tuple[float, ...],
    q_levels: tuple[float, ...],
) -> dict[str, object]:
    prevalence = min(prevalences)
    prevalence_key = str(prevalence)
    q_key = _preferred_key(q_levels, 0.1)
    metrics = curve["procedures"]["bh"][prevalence_key][q_key]
    blockers = []
    if diagnostics["superuniform_audit_rejected"]:
        blockers.append("held_out_known_superuniformity_rejected")
    if metrics["empirical_fdr_ci95_high"] > float(q_key):
        blockers.append("empirical_fdr_upper_ci_exceeds_nominal_q")
    if metrics["mean_power"] <= 0.0:
        blockers.append("zero_unknown_detection_power")
    if metrics["probability_any_alert"] < 0.5:
        blockers.append("mostly_abstains")
    return {
        "status": "not_deployable" if blockers else "candidate_requires_external_validation",
        "prevalence": prevalence,
        "q": float(q_key),
        "blockers": blockers,
        "empirical_fdr": metrics["empirical_fdr"],
        "empirical_fdr_ci95_high": metrics["empirical_fdr_ci95_high"],
        "mean_power": metrics["mean_power"],
        "mean_alerts": metrics["mean_alerts"],
        "probability_any_alert": metrics["probability_any_alert"],
    }


def _comma_values(text: str, cast) -> tuple:
    return tuple(cast(item.strip()) for item in text.split(",") if item.strip())


def _effective_batch_size(
    requested: int,
    is_unknown: np.ndarray,
    prevalences: tuple[float, ...],
) -> int:
    known = int((~is_unknown).sum())
    unknown = int(is_unknown.sum())
    feasible = requested
    for prevalence in prevalences:
        feasible = min(feasible, int(known / (1.0 - prevalence)), int(unknown / prevalence))
    while feasible >= 2:
        if all(
            round(feasible * prevalence) <= unknown
            and feasible - round(feasible * prevalence) <= known
            for prevalence in prevalences
        ):
            return feasible
        feasible -= 1
    raise ValueError("The test split cannot form a mixed known/unknown deployment batch")


def _unique_source_indices(source_ids: np.ndarray) -> np.ndarray:
    """Keep one representative per source id for a dependence sensitivity run."""
    _, indices = np.unique(np.asarray(source_ids).astype(str), return_index=True)
    return np.sort(indices)


def _score_method(
    method: str,
    train_x: np.ndarray,
    train_y: np.ndarray,
    tuning_x: np.ndarray,
    tuning_y: np.ndarray,
    fdr_calibration_x: np.ndarray,
    test_x: np.ndarray,
    num_classes: int,
    device: torch.device,
    epochs: int,
    inference_batch_size: int,
    seed: int,
    profile: str,
    scorer_components: tuple[str, ...],
    curvature: float,
    tail_extension: bool = False,
    tail_anchor_exceedances: int = 250,
    tail_confidence: float = 0.0,
    evidential_weight: float = 1.0,
    margin_weight: float = 1.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict[str, float | str]]:
    combined_x = np.concatenate([fdr_calibration_x, test_x], axis=0)
    split = len(fdr_calibration_x)
    if method == "hedl":
        _, _, combined_predictions, combined_scores, inference_seconds, diagnostics = fit_and_infer_hedl(
            train_x,
            train_y,
            tuning_x,
            tuning_y,
            combined_x,
            num_classes,
            device,
            epochs,
            inference_batch_size,
            profile,
            scorer_components,
            curvature,
            tail_extension,
            tail_anchor_exceedances,
            tail_confidence,
            evidential_weight,
            margin_weight,
        )
        diagnostics = {f"scorer_{key}": value for key, value in diagnostics.items()}
    elif method in DIRECT_BASELINE_METHODS:
        output = run_direct_baseline(
            method=method,
            train_x=train_x,
            train_y=train_y,
            calibration_x=tuning_x,
            calibration_y=tuning_y,
            test_x=combined_x,
            num_classes=num_classes,
            device=device,
            epochs=epochs,
            batch_size=inference_batch_size,
            seed=seed,
        )
        combined_scores = output.test_scores
        combined_predictions = output.test_predictions
        inference_seconds = output.inference_seconds
        diagnostics = {
            key if key.startswith("adapter_") else f"adapter_{key}": value
            for key, value in output.diagnostics.items()
        }
    else:
        raise ValueError(f"Unsupported method {method!r}")
    diagnostics.update(
        inference_seconds=float(inference_seconds),
        milliseconds_per_scored_flow=float(1000.0 * inference_seconds / len(combined_x)),
    )
    return (
        combined_scores[:split],
        combined_scores[split:],
        combined_predictions[:split],
        combined_predictions[split:],
        diagnostics,
    )


def run_experiment(args: argparse.Namespace) -> dict[str, object]:
    seed_everything(args.seed)
    raw = cap_open_set_data(load_rotation(args.dataset, args.scenario), args.max_rows, args.seed)
    data, _ = encode_known_labels(raw)
    train_mask = data.train.y >= 0
    calibration_mask = data.calibration.y >= 0
    calibration_x = data.calibration.x[calibration_mask]
    calibration_y = data.calibration.y[calibration_mask]
    calibration_source_ids = data.calibration.source_ids[calibration_mask]
    test_x = data.test.x
    test_y = data.test.y
    if args.deduplicate_source_ids:
        calibration_unique = _unique_source_indices(calibration_source_ids)
        calibration_x = calibration_x[calibration_unique]
        calibration_y = calibration_y[calibration_unique]
        calibration_source_ids = calibration_source_ids[calibration_unique]
        test_unique = _unique_source_indices(data.test.source_ids)
        test_x = test_x[test_unique]
        test_y = test_y[test_unique]
    tuning_indices, fdr_indices = stratified_calibration_split(
        calibration_y, args.tuning_fraction, args.seed + 101
    )
    tuning_x = calibration_x[tuning_indices]
    tuning_y = calibration_y[tuning_indices]
    fdr_calibration_x = calibration_x[fdr_indices]
    is_unknown = test_y < 0
    batch_size = _effective_batch_size(args.alert_batch_size, is_unknown, args.prevalences)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    methods: dict[str, object] = {}
    for method in args.methods:
        method_started = time.perf_counter()
        print(f"[fdr] scoring {method}...", file=sys.stderr, flush=True)
        seed_everything(args.seed)
        calibration_scores, test_scores, calibration_predictions, test_predictions, diagnostics = _score_method(
            method,
            data.train.x[train_mask],
            data.train.y[train_mask],
            tuning_x,
            tuning_y,
            fdr_calibration_x,
            test_x,
            len(data.known_families),
            device,
            args.epochs,
            args.inference_batch_size,
            args.seed,
            args.profile,
            args.scorer_components,
            args.curvature,
        )
        diagnostics["test_unknown_auroc"] = float(roc_auc_score(is_unknown, test_scores))
        marginal_diagnostics = null_pvalue_diagnostics(
            calibration_scores,
            test_scores[~is_unknown],
            audit_alpha=args.validity_audit_alpha,
        )
        mondrian_diagnostics = null_pvalue_diagnostics(
            calibration_scores,
            test_scores[~is_unknown],
            calibration_groups=calibration_predictions,
            known_test_groups=test_predictions[~is_unknown],
            minimum_group_size=args.minimum_group_size,
            audit_alpha=args.validity_audit_alpha,
        )
        mondrian_fdr = evaluate_fdr_curve(
            calibration_scores,
            test_scores,
            is_unknown,
            args.prevalences,
            args.q_levels,
            batch_size,
            args.repeats,
            args.seed + 1000,
            args.procedures,
            calibration_groups=calibration_predictions,
            test_groups=test_predictions,
            minimum_group_size=args.minimum_group_size,
        )
        marginal_fdr = evaluate_fdr_curve(
            calibration_scores,
            test_scores,
            is_unknown,
            args.prevalences,
            args.q_levels,
            batch_size,
            args.repeats,
            args.seed + 1000,
            args.procedures,
        )
        methods[method] = {
            "diagnostics": diagnostics,
            "null_pvalue_diagnostics": {
                "marginal": marginal_diagnostics,
                "mondrian": mondrian_diagnostics,
            },
            "mondrian_group_diagnostics": mondrian_group_diagnostics(
                calibration_predictions,
                test_predictions,
                args.minimum_group_size,
            ),
            "fdr": marginal_fdr,
            "fdr_mondrian_sensitivity": mondrian_fdr,
            "deployment_assessment": {
                "marginal": _deployment_assessment(
                    marginal_diagnostics, marginal_fdr, args.prevalences, args.q_levels
                ),
                "mondrian": _deployment_assessment(
                    mondrian_diagnostics, mondrian_fdr, args.prevalences, args.q_levels
                ),
            },
            "fixed_far": evaluate_fixed_far_curve(
                calibration_scores,
                test_scores,
                is_unknown,
                args.prevalences,
                batch_size,
                args.repeats,
                args.seed + 2000,
                args.false_alarm_budget,
            ),
        }
        print(
            f"[fdr] finished {method} in {time.perf_counter() - method_started:.1f}s",
            file=sys.stderr,
            flush=True,
        )
    return {
        "protocol": "nested_split_conformal_fdr",
        "dataset": args.dataset,
        "scenario": args.scenario,
        "seed": args.seed,
        "epochs": args.epochs,
        "device": str(device),
        "methods_requested": list(args.methods),
        "prevalences": list(args.prevalences),
        "q_levels": list(args.q_levels),
        "procedures": list(args.procedures),
        "fdr_calibration": "marginal_primary_with_predicted_class_mondrian_sensitivity",
        "validity_audit_alpha": args.validity_audit_alpha,
        "minimum_group_size": args.minimum_group_size,
        "alert_batch_size_requested": args.alert_batch_size,
        "alert_batch_size_effective": batch_size,
        "repeats": args.repeats,
        "tuning_calibration_size": len(tuning_indices),
        "fdr_calibration_size": len(fdr_indices),
        "test_known": int((~is_unknown).sum()),
        "test_unknown": int(is_unknown.sum()),
        "deduplicate_source_ids": bool(args.deduplicate_source_ids),
        "unique_calibration_source_ids": int(len(np.unique(calibration_source_ids))),
        "methods": methods,
    }


def _write_csv(payload: dict[str, object], path: Path) -> None:
    rows: list[dict[str, object]] = []
    for method, method_result in payload["methods"].items():
        calibrations = (("marginal", "fdr"), ("mondrian", "fdr_mondrian_sensitivity"))
        for calibration, result_key in calibrations:
            for procedure, prevalence_results in method_result[result_key]["procedures"].items():
                for prevalence, q_results in prevalence_results.items():
                    for q, metrics in q_results.items():
                        rows.append(
                            {
                                "method": method,
                                "policy": f"{procedure}_{calibration}",
                                "prevalence": prevalence,
                                "q_or_far": q,
                                **metrics,
                            }
                        )
        for prevalence, metrics in method_result["fixed_far"]["prevalence"].items():
            rows.append(
                {
                    "method": method,
                    "policy": "fixed_far",
                    "prevalence": prevalence,
                    "q_or_far": method_result["fixed_far"]["false_alarm_budget"],
                    **metrics,
                }
            )
    fieldnames = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(payload: dict[str, object], path: Path) -> None:
    preferred_q = "0.1" if 0.1 in payload["q_levels"] else str(payload["q_levels"][0])
    lines = [
        "# Conformal FDR Prototype",
        "",
        f"- Dataset: `{payload['dataset']}` / `{payload['scenario']}`",
        f"- Alert window: {payload['alert_batch_size_effective']} flows",
        f"- Repeated batches: {payload['repeats']}",
        f"- Tuning/FDR calibration: {payload['tuning_calibration_size']} / {payload['fdr_calibration_size']}",
        "- Every detector is conformalized with the same held-out calibration protocol.",
        "- Empirical FDR is the mean realised FDP; `P(any)` separates control from a trivial no-alert result.",
        "- Marginal conformal calibration is primary; predicted-class Mondrian is a sensitivity analysis.",
        "- A rejected held-out-known validity audit blocks any formal FDR claim.",
        "",
        f"## BH at q={preferred_q}",
        "",
        "| Method | Prevalence | Empirical FDR | Power | Mean alerts | P(any) | Min rejections at p_min |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for method, method_result in payload["methods"].items():
        bh = method_result["fdr"]["procedures"].get("bh", {})
        for prevalence in payload["prevalences"]:
            metrics = bh.get(str(prevalence), {}).get(preferred_q)
            if metrics is None:
                continue
            lines.append(
                f"| {method} | {prevalence:g} | {metrics['empirical_fdr']:.4f} | "
                f"{metrics['mean_power']:.4f} | {metrics['mean_alerts']:.2f} | "
                f"{metrics['probability_any_alert']:.3f} | "
                f"{metrics['minimum_bh_rejections_at_pmin']:.0f} |"
            )
    lines.extend(
        [
            "",
            "## Validity and Deployment Gate",
            "",
            "| Method | Calibration | Violation | DKW bound | Audit | Deployment status | Blockers |",
            "| --- | --- | ---: | ---: | --- | --- | --- |",
        ]
    )
    for method, method_result in payload["methods"].items():
        for calibration in ("marginal", "mondrian"):
            diagnostics = method_result["null_pvalue_diagnostics"][calibration]
            assessment = method_result["deployment_assessment"][calibration]
            lines.append(
                f"| {method} | {calibration} | {diagnostics['superuniform_violation']:.4f} | "
                f"{diagnostics['superuniform_dkw_bound']:.4f} | "
                f"{diagnostics['superuniform_audit_status']} | {assessment['status']} | "
                f"{', '.join(assessment['blockers']) or 'none'} |"
            )
    lines.extend(
        [
            "",
            "## Interpretation Guardrails",
            "",
            "- BH control relies on the exchangeability/PRDS conditions studied by Bates et al. (2023).",
            "- Network-flow dependence can violate those assumptions; BY is included as a conservative sensitivity analysis.",
            "- BY cannot repair invalid marginal p-values; inspect `null_pvalue_diagnostics` before interpreting FDR.",
            "- FDR is an expectation, not a guarantee that every realised batch has FDP below q.",
            "- Zero empirical FDR with near-zero `P(any)` is abstention, not useful detection.",
            "- The minimum attainable p-value is finite; batch size and calibration size can force zero power.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare batch FDR control for open-set NIDS scores")
    parser.add_argument("--dataset", default="ciciomt2024")
    parser.add_argument("--scenario", default="Z1")
    parser.add_argument("--methods", default=",".join(DEFAULT_METHODS))
    parser.add_argument("--prevalences", default=",".join(map(str, DEFAULT_PREVALENCES)))
    parser.add_argument("--q-levels", default=",".join(map(str, DEFAULT_Q_LEVELS)))
    parser.add_argument("--procedures", default="bh,by")
    parser.add_argument("--alert-batch-size", type=int, default=5000)
    parser.add_argument("--repeats", type=int, default=200)
    parser.add_argument("--false-alarm-budget", type=float, default=0.01)
    parser.add_argument("--tuning-fraction", type=float, default=0.5)
    parser.add_argument("--minimum-group-size", type=int, default=30)
    parser.add_argument("--validity-audit-alpha", type=float, default=0.05)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--inference-batch-size", type=int, default=256)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--max-rows", type=int)
    parser.add_argument(
        "--deduplicate-source-ids",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Keep one calibration/test flow per source_id as a dependence sensitivity analysis.",
    )
    parser.add_argument("--profile", choices=sorted(PROFILES), default=DEFAULT_PROFILE)
    parser.add_argument("--scorer-components", default=",".join(COMPONENT_NAMES))
    parser.add_argument("--curvature", type=float, default=0.0)
    parser.add_argument("--output", type=Path, default=Path("results/fdr/fdr_prototype.json"))
    args = parser.parse_args()
    args.methods = _comma_values(args.methods, str)
    args.prevalences = _comma_values(args.prevalences, float)
    args.q_levels = _comma_values(args.q_levels, float)
    args.procedures = _comma_values(args.procedures, str)
    args.scorer_components = _comma_values(args.scorer_components, str)
    unsupported = set(args.methods).difference({"hedl", *DIRECT_BASELINE_METHODS})
    if unsupported:
        parser.error(f"Unsupported methods: {sorted(unsupported)}")
    unknown_components = set(args.scorer_components).difference(COMPONENT_NAMES)
    if unknown_components or not args.scorer_components:
        parser.error(f"--scorer-components must be a non-empty subset of {list(COMPONENT_NAMES)}")

    started = time.perf_counter()
    payload = run_experiment(args)
    payload["elapsed_seconds"] = time.perf_counter() - started
    args.output.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(args.output)
    _write_csv(payload, args.output.with_suffix(".csv"))
    _write_markdown(payload, args.output.with_suffix(".md"))
    print(text)


if __name__ == "__main__":
    main()
