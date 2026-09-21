"""Measure the resolution barrier and what it takes to get past it.

Reads the scores written by :mod:`capture_scores` and sweeps the three things
an operator can actually choose -- how many verified-known flows to calibrate
on, what false-discovery budget to accept, and whether to extrapolate the tail
of the calibration distribution -- against the one thing they cannot, the
prevalence of attacks in the traffic.

Every row carries the prediction from :mod:`resolution` next to the measured
outcome, so the table is a test of the theory and not an illustration of it.
Three p-value constructions are compared at each operating point:

``distribution_free``   split-conformal, valid on average over calibration
                        draws, floored at 1/(n+1);
``training_conditional``  the Beta upper bound on the same tail mass, valid for
                        the calibration set in hand with confidence 1 - delta;
``tail_extended``       conformal below the anchor, generalised Pareto above it;
``oracle``              tail probabilities read off held-out known traffic, not
                        deployable, included as the ceiling that says whether a
                        failure is about calibration or about the detector.

Each calibration size is drawn several times.  That is not variance reduction:
the spread across draws is the measurement.  A marginal guarantee constrains
the average over the draws, so the only way to see whether a single deployment
is protected is to look at the draws one at a time.

The oracle reference and the flows that populate the alert windows come from
disjoint halves of the known test split, so the ceiling is not reading its own
answer sheet.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from .fdr import (
    apply_fdr_procedure,
    conformal_evalues,
    conformal_pvalues,
    e_benjamini_hochberg,
    harmonic_conformal_evalues,
    realised_error_rates,
    storey_benjamini_hochberg,
    storey_pi_zero,
)
from .resolution import (
    OperatingPoint,
    binding_constraint,
    conditional_barrier_calibration,
    escape_routes,
    oracle_pvalues,
    screening_invariance_report,
    training_conditional_floor,
    training_conditional_pvalues,
)
from .tail import TailExtendedCalibration


ROOT = Path(__file__).resolve().parents[2]
SCORES = ROOT / "results" / "scores"
RESULTS = ROOT / "results" / "resolution"

#: ``distribution_free`` is the Bates et al. (2023) split-conformal procedure.
#: It is named for its property rather than its authors only because the same
#: name has to cover the Beta-corrected variant sitting next to it; every table
#: in the paper labels it as Bates split-conformal BH.
PVALUE_MODES = (
    "distribution_free",
    "training_conditional",
    "tail_extended",
    "e_bh",
    "e_bh_harmonic",
    "storey_bh",
    "oracle",
    "clairvoyant",
)

#: Procedures that carry their own decision rule instead of feeding p-values to
#: ``apply_fdr_procedure``.
SELF_DECIDING_MODES = ("clairvoyant", "e_bh", "e_bh_harmonic", "storey_bh")


def clairvoyant_power(scores: np.ndarray, is_unknown: np.ndarray, q: float) -> dict[str, float]:
    """Most power any rule could have on this window while keeping FDP <= q.

    Reads the labels, takes flows in score order and stops at the deepest cut
    whose realised false fraction is still within budget.  No procedure that
    only sees scores can beat it, so it separates "this detector cannot rank
    the attacks high enough" from "the p-values could not express how high".
    Unlike the ``oracle`` mode this is a power ceiling *at* the FDR budget
    rather than a p-value construction, so its own FDP is within ``q`` by
    definition.
    """
    order = np.argsort(-scores, kind="stable")
    ranked_unknown = is_unknown[order]
    true_discoveries = np.cumsum(ranked_unknown)
    counts = np.arange(1, len(order) + 1)
    within_budget = np.flatnonzero((counts - true_discoveries) <= q * counts)
    if not len(within_budget):
        return {"alerts": 0.0, "power": 0.0, "false_discovery_proportion": 0.0}
    cut = int(within_budget[-1]) + 1
    found = int(true_discoveries[cut - 1])
    total = int(ranked_unknown.sum())
    return {
        "alerts": float(cut),
        "power": float(found / total) if total else 0.0,
        "false_discovery_proportion": float((cut - found) / cut),
        "true_discoveries": float(found),
        "false_discoveries": float(cut - found),
        "false_alarm_rate": float((cut - found) / max(1, len(order) - total)),
        "alert_rate": float(cut / len(order)),
    }


def _window_indices(
    known_pool: np.ndarray,
    unknown_pool: np.ndarray,
    window_size: int,
    prevalence: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Draw one alert window at the requested prevalence.

    The unknown count is rounded rather than floored so that a prevalence too
    low to place a single attack in the window still places one: the barrier is
    about whether BH can react to an attack that *is* present, and a window
    with no attack in it can only ever contribute false discoveries.
    """
    unknown_count = max(1, min(window_size - 1, int(round(window_size * prevalence))))
    known_count = window_size - unknown_count
    known = rng.choice(known_pool, known_count, replace=known_count > len(known_pool))
    unknown = rng.choice(unknown_pool, unknown_count, replace=unknown_count > len(unknown_pool))
    scores = np.concatenate([known, unknown])
    is_unknown = np.concatenate(
        [np.zeros(known_count, dtype=bool), np.ones(unknown_count, dtype=bool)]
    )
    order = rng.permutation(len(scores))
    return scores[order], is_unknown[order]


def _pvalue_function(
    mode: str,
    calibration_scores: np.ndarray,
    oracle_reference: np.ndarray,
    anchor_exceedances: int,
    tail_confidence: float,
    seed: int,
    delta: float = 0.1,
    corrected_levels: int = 1,
):
    if mode == "distribution_free":
        return lambda scores: conformal_pvalues(calibration_scores, scores), {}
    if mode == "training_conditional":
        diagnostics = {
            "conditional_delta": float(delta),
            "conditional_corrected_levels": float(corrected_levels),
            "conditional_floor": training_conditional_floor(
                len(calibration_scores), delta, corrected_levels
            ),
        }
        return (
            lambda scores: training_conditional_pvalues(
                calibration_scores, scores, delta, corrected_levels
            ),
            diagnostics,
        )
    if mode == "oracle":
        return lambda scores: oracle_pvalues(oracle_reference, scores), {}
    if mode in ("clairvoyant", "e_bh", "e_bh_harmonic", "storey_bh"):
        # Handled by the window loop: these carry their own decision rule.
        return (lambda scores: np.ones(len(scores)), {})
    if mode == "tail_extended":
        exceedances = min(anchor_exceedances, max(10, len(calibration_scores) // 4))
        tail = TailExtendedCalibration(
            anchor_exceedances=exceedances,
            confidence=tail_confidence,
            seed=seed,
        ).fit(calibration_scores)
        return tail.pvalues, tail.diagnostics()
    raise ValueError(f"Unknown p-value mode {mode!r}")


def evaluate_operating_point(
    calibration_scores: np.ndarray,
    known_window_pool: np.ndarray,
    unknown_pool: np.ndarray,
    oracle_reference: np.ndarray,
    window_size: int,
    prevalence: float,
    q: float,
    procedure: str,
    repeats: int,
    seed: int,
    mode: str,
    anchor_exceedances: int,
    tail_confidence: float,
    delta: float = 0.1,
    corrected_levels: int = 1,
    evalue_top_k: int = 1,
) -> dict[str, object]:
    pvalue_function, tail_diagnostics = _pvalue_function(
        mode,
        calibration_scores,
        oracle_reference,
        anchor_exceedances,
        tail_confidence,
        seed,
        delta,
        corrected_levels,
    )
    rng = np.random.default_rng(seed)
    trials: list[dict[str, float]] = []
    for _ in range(repeats):
        scores, is_unknown = _window_indices(
            known_window_pool, unknown_pool, window_size, prevalence, rng
        )
        if mode == "clairvoyant":
            trials.append(clairvoyant_power(scores, is_unknown, q))
            continue
        if mode == "e_bh":
            rejected = e_benjamini_hochberg(
                conformal_evalues(calibration_scores, scores, top_k=evalue_top_k), q
            )
        elif mode == "e_bh_harmonic":
            rejected = e_benjamini_hochberg(
                harmonic_conformal_evalues(calibration_scores, scores), q
            )
        elif mode == "storey_bh":
            rejected = storey_benjamini_hochberg(
                conformal_pvalues(calibration_scores, scores), q
            )
        else:
            rejected = apply_fdr_procedure(pvalue_function(scores), q, procedure)
        trials.append(realised_error_rates(rejected, is_unknown))
    fdp = np.array([trial["false_discovery_proportion"] for trial in trials])
    power = np.array([trial["power"] for trial in trials])
    alerts = np.array([trial["alerts"] for trial in trials])
    standard_error = float(fdp.std(ddof=1) / np.sqrt(len(fdp))) if len(fdp) > 1 else 0.0
    point = OperatingPoint(len(calibration_scores), window_size, q, prevalence)
    procedure_labels = {
        "distribution_free": "Bates split-conformal BH",
        "training_conditional": "training-conditional (Beta) conformal BH",
        "tail_extended": "GPD tail-extended conformal BH",
        "e_bh": "conformal e-values + e-BH (Wang-Ramdas)",
        "e_bh_harmonic": "harmonic conformal e-values + e-BH",
        "storey_bh": "Storey adaptive BH",
        "oracle": "plug-in oracle tail probabilities (not deployable)",
        "clairvoyant": "label-reading ceiling (not a procedure)",
    }
    summary: dict[str, object] = {
        "pvalue_mode": mode,
        "procedure": procedure,
        "procedure_label": procedure_labels[mode],
        "empirical_fdr": float(fdp.mean()),
        "empirical_fdr_se": standard_error,
        "empirical_fdr_ci95_high": float(min(1.0, fdp.mean() + 1.96 * standard_error)),
        "fdr_exceeds_q": bool(fdp.mean() > q),
        "mean_power": float(power.mean()),
        "mean_alerts": float(alerts.mean()),
        "probability_any_alert": float(np.mean(alerts > 0.0)),
        "predicted_resolution_feasible": point.resolution_feasible,
        "predicted_required_calibration": point.required_calibration,
        "predicted_floor_firing_fdp": point.report()["floor_firing_fdp"],
    }
    summary.update(tail_diagnostics)
    return summary


def run(args: argparse.Namespace) -> dict[str, object]:
    arrays = np.load(SCORES / f"{args.tag}.npz")
    metadata = json.loads((SCORES / f"{args.tag}.json").read_text(encoding="utf-8"))
    calibration_scores = arrays[f"{args.method}__calibration_scores"]
    test_scores = arrays[f"{args.method}__test_scores"]
    is_unknown = arrays["test_is_unknown"]

    rng = np.random.default_rng(args.seed)
    known_scores = test_scores[~is_unknown]
    unknown_scores = test_scores[is_unknown]
    # Disjoint halves: one defines the oracle tail, the other populates windows.
    shuffled = rng.permutation(len(known_scores))
    half = len(shuffled) // 2
    oracle_reference = known_scores[shuffled[:half]]
    known_window_pool = known_scores[shuffled[half:]]

    sizes = sorted({min(size, len(calibration_scores)) for size in args.calibration_sizes})

    rows: list[dict[str, object]] = []
    validity: list[dict[str, object]] = []
    for size in sizes:
        # A full-size "draw" has nothing left to vary, so it is evaluated once.
        draws = 1 if size == len(calibration_scores) else args.calibration_draws
        for draw in range(draws):
            draw_rng = np.random.default_rng(args.seed + 7919 * draw + size)
            subsample = (
                calibration_scores
                if size == len(calibration_scores)
                else calibration_scores[
                    draw_rng.choice(len(calibration_scores), size, replace=False)
                ]
            )
            for mode in args.pvalue_modes:
                if mode == "tail_extended" and size < 4 * args.tail_anchor_exceedances // 3:
                    # A tail fit needs a body to sit on; skip rather than report
                    # an empirical quantile with extra steps.
                    continue
                if mode == "tail_extended":
                    tail = TailExtendedCalibration(
                        anchor_exceedances=min(args.tail_anchor_exceedances, max(10, size // 4)),
                        confidence=args.tail_confidence,
                        seed=args.seed + draw,
                    ).fit(subsample)
                    validity.append(
                        {
                            "calibration_size": size,
                            "draw": draw,
                            "mode": mode,
                            **tail.audit(known_window_pool),
                        }
                    )
                for prevalence in args.prevalences:
                    for q in args.q_levels:
                        for procedure in args.procedures:
                            row = evaluate_operating_point(
                                subsample,
                                known_window_pool,
                                unknown_scores,
                                oracle_reference,
                                args.window_size,
                                prevalence,
                                q,
                                procedure,
                                args.repeats,
                                args.seed + draw,
                                mode,
                                args.tail_anchor_exceedances,
                                args.tail_confidence,
                                args.delta,
                                args.corrected_levels,
                                args.evalue_top_k,
                            )
                            row.update(
                                calibration_size=size,
                                calibration_draw=draw,
                                prevalence=prevalence,
                                q=q,
                            )
                            rows.append(row)

    # Attribute every zero-power cell to the resource that caused it, using the
    # oracle evaluated on the same windows.
    ceiling = {
        (r["calibration_size"], r["calibration_draw"], r["prevalence"], r["q"], r["procedure"]):
            r["mean_power"]
        for r in rows
        if r["pvalue_mode"] == "oracle"
    }
    for row in rows:
        key = (
            row["calibration_size"],
            row["calibration_draw"],
            row["prevalence"],
            row["q"],
            row["procedure"],
        )
        point = OperatingPoint(
            int(row["calibration_size"]),
            args.window_size,
            float(row["q"]),
            float(row["prevalence"]),
        )
        row["oracle_power"] = float(ceiling.get(key, float("nan")))
        row["binding_constraint"] = binding_constraint(
            float(row["mean_power"]), row["oracle_power"], point
        )

    reference_point = OperatingPoint(
        len(calibration_scores), args.window_size, args.q_levels[0], args.prevalences[-1]
    )
    return {
        "protocol": "resolution_barrier_sweep",
        "scores_tag": args.tag,
        "method": args.method,
        "score_capture": {
            key: metadata[key]
            for key in ("dataset", "scenario", "seed", "epochs", "profile", "curvature")
            if key in metadata
        },
        "score_tail_extension": bool(metadata.get("tail_extension", False)),
        "unknown_auroc": metadata["methods"][args.method]["unknown_auroc"],
        "full_calibration_size": int(len(calibration_scores)),
        "oracle_reference_size": int(len(oracle_reference)),
        "known_window_pool_size": int(len(known_window_pool)),
        "unknown_pool_size": int(len(unknown_scores)),
        "window_size": args.window_size,
        "repeats": args.repeats,
        "calibration_draws": args.calibration_draws,
        "delta": args.delta,
        "corrected_levels": args.corrected_levels,
        "evalue_top_k": args.evalue_top_k,
        "conformal_evalue_ceiling": float(len(calibration_scores) + 1),
        "tail_anchor_exceedances": args.tail_anchor_exceedances,
        "tail_confidence": args.tail_confidence,
        "screening_invariance": screening_invariance_report(
            len(calibration_scores), args.window_size, args.q_levels[0], 0.01
        ),
        "barriers": [
            {
                "q": q,
                "prevalence": prevalence,
                "marginal_required_calibration": OperatingPoint(
                    1, args.window_size, q, prevalence
                ).required_calibration,
                "conditional_required_calibration": conditional_barrier_calibration(
                    q, prevalence, args.delta, args.corrected_levels
                ),
            }
            for q in args.q_levels
            for prevalence in args.prevalences
        ],
        "escape_routes_at_hardest_point": escape_routes(reference_point),
        "tail_validity_audits": validity,
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default="cicids2017_Z1_s13")
    parser.add_argument("--method", default="hedl")
    parser.add_argument("--window-size", type=int, default=2000)
    parser.add_argument("--repeats", type=int, default=400)
    parser.add_argument("--calibration-draws", type=int, default=8)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--calibration-sizes", default="200,1000,3000,12592")
    parser.add_argument("--prevalences", default="0.1,0.01,0.001")
    parser.add_argument("--q-levels", default="0.1")
    parser.add_argument("--procedures", default="bh")
    parser.add_argument("--pvalue-modes", default=",".join(PVALUE_MODES))
    parser.add_argument("--delta", type=float, default=0.1)
    parser.add_argument("--corrected-levels", type=int, default=1)
    # top_k = 1 is the e-value with the largest attainable ceiling, i.e. the
    # most favourable member of the family for the competing procedure.
    parser.add_argument("--evalue-top-k", type=int, default=1)
    parser.add_argument("--tail-anchor-exceedances", type=int, default=250)
    parser.add_argument("--tail-confidence", type=float, default=0.9)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    args.calibration_sizes = tuple(int(v) for v in args.calibration_sizes.split(","))
    args.prevalences = tuple(float(v) for v in args.prevalences.split(","))
    args.q_levels = tuple(float(v) for v in args.q_levels.split(","))
    args.procedures = tuple(v.strip() for v in args.procedures.split(","))
    args.pvalue_modes = tuple(v.strip() for v in args.pvalue_modes.split(","))

    started = time.perf_counter()
    payload = run(args)
    payload["elapsed_seconds"] = time.perf_counter() - started
    output = args.output or RESULTS / f"{args.tag}_{args.method}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"wrote {output} in {payload['elapsed_seconds']:.1f}s ({len(payload['rows'])} rows)")


if __name__ == "__main__":
    main()
