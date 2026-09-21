"""How to spend a labelling budget at a new deployment site.

A team standing up a detector on a network it has never seen can afford to have
some traffic looked at.  The question this runner answers is what to ask for.
Two things are on the menu and they cost very different amounts:

*family labels* -- "this flow is a port scan" -- which need an analyst who can
name the behaviour, and which the reference geometry consumes a handful of per
class;

*verified-known status* -- "this flow is not an attack" -- which needs only a
negative judgement, is far cheaper per flow, and which the conformal
calibration consumes by the thousand, at a rate the sizing rule in
:mod:`resolution` states exactly.

The earlier design in this repository split its budget evenly across four
roles, two of each kind.  The sweep below prices that choice against the
alternatives by training the source encoder once and then re-spending the same
budget many ways on the cached features, so that two allocations differing by
one number are not also differing by a training run.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

from .anchor_transport import (
    DEFAULT_REFERENCE_POLICIES,
    ReferencePolicy,
    allocate_target_budget,
    fit_reference_scorer,
    select_reference_policy,
)
from .conformal import ConformalFusionScorer
from .data import source_fitted_cross_domain, source_fitted_leave_one_domain_out
from .metrics import evaluate_open_set
from .models import DEFAULT_PROFILE, PROFILES
from .pact import AlertBudget, PactAlerting
from .run import infer_hedl, seed_everything, train_hedl


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results" / "budget"
CASES = {
    "unsw_to_ton": lambda rows: source_fitted_cross_domain(
        "nf_unsw_nb15_v3", "nf_ton_iot_v3", max_rows=rows
    ),
    "ton_to_unsw": lambda rows: source_fitted_cross_domain(
        "nf_ton_iot_v3", "nf_unsw_nb15_v3", max_rows=rows
    ),
    "loeo_unsw": lambda rows: source_fitted_leave_one_domain_out(
        ["nf_ton_iot_v3", "nf_bot_iot_v3", "nf_cse_cic_ids2018_v3"],
        "nf_unsw_nb15_v3",
        max_rows=rows,
    ),
}


def _evaluate(
    name: str,
    labels: np.ndarray,
    predictions: np.ndarray,
    test_scores: np.ndarray,
    calibration_scores: np.ndarray,
    audit_scores: np.ndarray,
    budget: AlertBudget,
    diagnostics: dict[str, object],
    seconds: float,
) -> dict[str, object]:
    metrics = evaluate_open_set(labels, predictions, test_scores)
    alerting = PactAlerting(budget=budget, guarantee="conditional").fit(
        calibration_scores, audit_scores if len(audit_scores) else None
    )
    decision = alerting.alert(test_scores)
    is_unknown = labels < 0
    alerts = int(decision.rejected.sum())
    true_alerts = int((decision.rejected & is_unknown).sum())
    return {
        "method": name,
        "metrics": metrics,
        "adaptation_seconds": seconds,
        "certificate": alerting.certificate.report(),
        "sizing_advice": alerting.sizing_advice(),
        "alerting": {
            **decision.summary(),
            "realised_false_discovery_proportion": float(
                (alerts - true_alerts) / alerts
            ) if alerts else 0.0,
            "realised_power": float(true_alerts / max(1, int(is_unknown.sum()))),
        },
        "diagnostics": diagnostics,
    }


def run(args: argparse.Namespace) -> dict[str, object]:
    source_x, source_y, source_cal_x, source_cal_y, target_x, target_y, shared = CASES[
        args.case
    ](args.max_rows)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    num_classes = int(len(np.unique(source_y)))

    seed_everything(args.seed)
    training_started = time.perf_counter()
    model = train_hedl(
        source_x, source_y, num_classes, device, args.epochs, args.batch_size,
        args.profile, args.curvature,
    )
    training_seconds = time.perf_counter() - training_started
    _, source_outputs, _ = infer_hedl(model, source_x, device, args.batch_size)
    _, source_cal_outputs, _ = infer_hedl(model, source_cal_x, device, args.batch_size)
    target_predictions, target_outputs, _ = infer_hedl(
        model, target_x, device, args.batch_size
    )
    source_features = source_outputs["tangent"]
    source_cal_features = source_cal_outputs["tangent"]
    target_features = target_outputs["tangent"]

    alert_budget = AlertBudget(
        q=args.q, prevalence=args.prevalence, window_size=args.alert_window
    )

    # The no-budget reference point: everything calibrated on the source.
    source_scorer = ConformalFusionScorer().fit(
        {"tangent": source_features}, source_y,
        {"tangent": source_cal_features}, source_cal_y,
    )
    known_target_rows = np.flatnonzero(target_y >= 0)

    rows: list[dict[str, object]] = []
    for total_budget in args.budgets:
        for family_shots in args.family_shots:
            family_cost = 2 * family_shots * len(np.unique(target_y[target_y >= 0]))
            verified = total_budget - family_cost
            if verified < args.minimum_verified:
                continue
            split = allocate_target_budget(target_y, family_shots, verified, args.seed)
            test_labels = target_y[split.test]
            calibration_features = target_features[split.calibration]
            audit_features = target_features[split.audit]
            common = dict(
                labels=test_labels,
                budget=alert_budget,
            )

            source_scores = source_scorer.score({"tangent": target_features[split.test]})
            rows.append(
                {
                    "total_budget": total_budget,
                    "family_shots_per_class": family_shots,
                    "family_labelled_flows": int(len(split.family_labelled())),
                    "verified_known_flows": int(len(split.verified_known())),
                    "calibration_flows": int(len(split.calibration)),
                    **_evaluate(
                        "source_only",
                        predictions=target_predictions[split.test],
                        test_scores=source_scores,
                        calibration_scores=source_scorer.score(
                            {"tangent": source_cal_features}
                        ),
                        audit_scores=source_scorer.score({"tangent": audit_features}),
                        diagnostics={"reference_policy": "source"},
                        seconds=0.0,
                        **common,
                    ),
                }
            )

            # Recalibration only: the source reference, the target calibration.
            recalibrated = ConformalFusionScorer().fit(
                {"tangent": source_features}, source_y,
                {"tangent": source_cal_features}, source_cal_y,
            )
            started = time.perf_counter()
            recalibrated.set_calibration(calibration_features)
            recalibration_seconds = time.perf_counter() - started
            rows.append(
                {
                    "total_budget": total_budget,
                    "family_shots_per_class": family_shots,
                    "family_labelled_flows": int(len(split.family_labelled())),
                    "verified_known_flows": int(len(split.verified_known())),
                    "calibration_flows": int(len(split.calibration)),
                    **_evaluate(
                        "recalibration_only",
                        predictions=target_predictions[split.test],
                        test_scores=recalibrated.score(
                            {"tangent": target_features[split.test]}
                        ),
                        calibration_scores=recalibrated.score(
                            {"tangent": calibration_features}
                        ),
                        audit_scores=recalibrated.score({"tangent": audit_features}),
                        diagnostics={"reference_policy": "source"},
                        seconds=recalibration_seconds,
                        **common,
                    ),
                }
            )

            for policy_name in args.policies:
                started = time.perf_counter()
                if policy_name == "selected":
                    selected = select_reference_policy(
                        source_features, source_y,
                        target_features[split.geometry], target_y[split.geometry],
                        target_features[split.selection], target_y[split.selection],
                    )
                else:
                    policy = next(
                        p for p in DEFAULT_REFERENCE_POLICIES if p.name == policy_name
                    )
                    selected = select_reference_policy(
                        source_features, source_y,
                        target_features[split.geometry], target_y[split.geometry],
                        target_features[split.selection], target_y[split.selection],
                        policies=(policy,),
                    )
                scorer = fit_reference_scorer(
                    selected,
                    target_features[split.selection],
                    target_y[split.selection],
                    calibration_features,
                )
                seconds = time.perf_counter() - started
                rows.append(
                    {
                        "total_budget": total_budget,
                        "family_shots_per_class": family_shots,
                        "family_labelled_flows": int(len(split.family_labelled())),
                        "verified_known_flows": int(len(split.verified_known())),
                        "calibration_flows": int(len(split.calibration)),
                        **_evaluate(
                            policy_name,
                            predictions=selected.geometry.predict(
                                target_features[split.test]
                            ),
                            test_scores=scorer.score(
                                {"tangent": target_features[split.test]}
                            ),
                            calibration_scores=scorer.score(
                                {"tangent": calibration_features}
                            ),
                            audit_scores=scorer.score({"tangent": audit_features}),
                            diagnostics=selected.diagnostics(),
                            seconds=seconds,
                            **common,
                        ),
                    }
                )
            print(
                f"[budget] B={total_budget} k={family_shots} verified={verified} done",
                flush=True,
            )

    return {
        "protocol": "target_label_budget_allocation",
        "case": args.case,
        "seed": args.seed,
        "device": str(device),
        "epochs": args.epochs,
        "max_rows": args.max_rows,
        "profile": args.profile,
        "curvature": args.curvature,
        "shared_families": list(shared),
        "source_classes": num_classes,
        "target_known_rows": int(len(known_target_rows)),
        "target_unknown_rows": int(int((target_y < 0).sum())),
        "source_training_seconds": training_seconds,
        "alert_budget": {
            "q": args.q,
            "prevalence": args.prevalence,
            "window_size": args.alert_window,
        },
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=sorted(CASES), default="unsw_to_ton")
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--max-rows", type=int, default=20000)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--profile", choices=sorted(PROFILES), default=DEFAULT_PROFILE)
    parser.add_argument("--curvature", type=float, default=0.0)
    parser.add_argument("--budgets", default="60,120,300,1000,3000")
    parser.add_argument("--family-shots", default="2,5,10,20")
    parser.add_argument("--policies", default="anchors_only,aligned_tenth,selected")
    parser.add_argument("--minimum-verified", type=int, default=20)
    parser.add_argument("--q", type=float, default=0.1)
    parser.add_argument("--prevalence", type=float, default=0.01)
    parser.add_argument("--alert-window", type=int, default=2000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    args.budgets = tuple(int(v) for v in args.budgets.split(","))
    args.family_shots = tuple(int(v) for v in args.family_shots.split(","))
    args.policies = tuple(v.strip() for v in args.policies.split(","))

    started = time.perf_counter()
    payload = run(args)
    payload["elapsed_seconds"] = time.perf_counter() - started
    output = args.output or RESULTS / f"{args.case}_seed{args.seed}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"wrote {output} in {payload['elapsed_seconds']:.1f}s ({len(payload['rows'])} rows)")


if __name__ == "__main__":
    main()
