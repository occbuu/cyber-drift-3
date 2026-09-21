"""RQ4: does the exchangeability gate catch the shifts that break the guarantee?

A certificate is only worth quoting if it is withdrawn when the traffic it was
issued for is gone.  The shift used here is the one a deployment meets first
and cannot label away: the *mix* of known traffic changes -- a new service, a
busier subnet, one attack campaign dominating the week -- while every flow is
still a real flow from a known family.  It is generated from cached scores
only, by re-weighting the held-out known test flows towards one known class
with magnitude ``s``:

    target mix = (1 - s) * calibration mix + s * point mass on class c

``s = 0`` is exchangeable traffic and measures false refusal.  For every other
condition the realised stream-level FDR of the uncertified procedure decides
whether the guarantee actually broke, and the gate is scored against that
ground truth rather than against the magnitude:

* detection rate: the gate refuses, among conditions where the uncertified
  procedure exceeds q;
* false refusal: the gate refuses on exchangeable traffic;
* false alarms per 1000 flows with and without the gate, where a refused
  certificate falls back to PACT's fixed per-window alarm budget.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from .fdr import benjamini_hochberg
from .pact import AlertBudget, PactAlerting, exchangeability_audit
from .resolution import training_conditional_pvalues


ROOT = Path(__file__).resolve().parents[2]
SCORES = ROOT / "results" / "scores"


def target_weights(test_labels: np.ndarray, calibration_mix: dict[int, float], focus: int, magnitude: float) -> np.ndarray:
    """Per-flow sampling weights that realise the shifted class mix."""
    weights = np.zeros(len(test_labels), dtype=np.float64)
    for label, share in calibration_mix.items():
        members = test_labels == label
        if not members.any():
            continue
        mass = (1.0 - magnitude) * share + (magnitude if label == focus else 0.0)
        weights[members] = mass / members.sum()
    total = weights.sum()
    return weights / total if total > 0 else weights


def stream_outcome(known, unknown, calibration, weights, rng, args, gated):
    """Aggregate FDP, power and false alarms over one stream of windows."""
    alerts = true_alerts = attacks = 0
    windows = args.stream_size // args.window_size
    for _ in range(windows):
        count = int(rng.binomial(args.window_size, args.prevalence))
        scores = np.concatenate([
            known[rng.choice(len(known), args.window_size - count, p=weights)],
            rng.choice(unknown, count),
        ])
        is_unknown = np.r_[np.zeros(args.window_size - count, bool), np.ones(count, bool)]
        if gated is not None:
            rejected = gated.alert(scores).rejected
        else:
            rejected = benjamini_hochberg(
                training_conditional_pvalues(calibration, scores, args.delta, 1), args.q
            )
        alerts += int(rejected.sum())
        true_alerts += int((rejected & is_unknown).sum())
        attacks += count
    false_alerts = alerts - true_alerts
    return {
        "fdp": false_alerts / alerts if alerts else 0.0,
        "power": true_alerts / attacks if attacks else 0.0,
        "false_alarms_per_1000": 1000.0 * false_alerts / (windows * args.window_size),
    }


def run_capture(tag: str, method: str, args: argparse.Namespace) -> list[dict[str, object]]:
    arrays = np.load(SCORES / f"{tag}.npz")
    metadata = json.loads((SCORES / f"{tag}.json").read_text(encoding="utf-8"))
    calibration = arrays[f"{method}__calibration_scores"].astype(np.float64)
    calibration_labels = arrays["calibration_labels"]
    test_scores = arrays[f"{method}__test_scores"].astype(np.float64)
    test_labels = arrays["test_labels"]
    is_unknown = arrays["test_is_unknown"]
    known, known_labels = test_scores[~is_unknown], test_labels[~is_unknown]
    unknown = test_scores[is_unknown]

    classes, counts = np.unique(calibration_labels, return_counts=True)
    calibration_mix = {int(c): float(n / counts.sum()) for c, n in zip(classes, counts)}
    present = [c for c in calibration_mix if (known_labels == c).sum() >= args.min_class_flows]
    # The classes whose own known scores sit highest are the shifts that can
    # actually hurt; a shift towards a low-scoring class only makes BH safer.
    by_upper_tail = sorted(
        present, key=lambda c: -float(np.quantile(known[known_labels == c], 0.99))
    )
    focus_classes = by_upper_tail[: args.focus_classes]

    budget = AlertBudget(q=args.q, prevalence=args.prevalence, window_size=args.window_size,
                         delta=args.delta)
    rows = []
    for focus in focus_classes:
        for magnitude in args.magnitudes:
            weights = target_weights(known_labels, calibration_mix, focus, magnitude)
            for repeat in range(args.repeats):
                rng = np.random.default_rng(args.seed + 1009 * repeat + int(1000 * magnitude) + 17 * focus)
                audit_sample = known[rng.choice(len(known), args.audit_size, p=weights)]
                audit = exchangeability_audit(
                    calibration, audit_sample, args.audit_alpha,
                    threshold=args.audit_threshold, permutations=args.audit_permutations,
                    seed=args.seed + repeat,
                )
                gated = PactAlerting(budget=budget, guarantee="conditional",
                                     audit_threshold=args.audit_threshold,
                                     audit_permutations=args.audit_permutations,
                                     ).fit(calibration, audit_sample)
                plain = stream_outcome(known, unknown, calibration, weights, rng, args, None)
                with_gate = stream_outcome(known, unknown, calibration, weights, rng, args, gated)
                rows.append({
                    "dataset": metadata["dataset"],
                    "seed": metadata.get("seed"),
                    "method": method,
                    "focus_class": int(focus),
                    "focus_family": metadata["known_families"][int(focus)],
                    "magnitude": float(magnitude),
                    "repeat": repeat,
                    "gate_fired": bool(audit["superuniform_audit_rejected"]),
                    "certificate_state": gated.certificate.state,
                    "violation": float(audit["superuniform_violation"]),
                    "bound": float(audit["superuniform_dkw_bound"]),
                    "guarantee_broken": bool(plain["fdp"] > args.q),
                    "ungated_fdp": plain["fdp"],
                    "ungated_power": plain["power"],
                    "ungated_false_alarms_per_1000": plain["false_alarms_per_1000"],
                    "gated_fdp": with_gate["fdp"],
                    "gated_false_alarms_per_1000": with_gate["false_alarms_per_1000"],
                })
    return rows


def summarise(rows: list[dict[str, object]], q: float) -> dict[str, object]:
    # Ground truth is per condition, not per stream: one stream's FDP exceeds q
    # on exchangeable traffic too, simply because FDR is an expectation.  A
    # condition "breaks the guarantee" when the mean FDP over its repeats does.
    conditions: dict[tuple, list[dict[str, object]]] = {}
    for r in rows:
        key = (r["dataset"], r["seed"], r["method"], r["focus_class"], r["magnitude"])
        conditions.setdefault(key, []).append(r)
    for members in conditions.values():
        broken_here = float(np.mean([m["ungated_fdp"] for m in members])) > q
        for m in members:
            m["condition_broken"] = broken_here
    # s = 0 counts as exchangeable only where the guarantee held; a dataset whose
    # calibration split already fails the audit should be refused at s = 0.
    exchangeable = [r for r in rows if r["magnitude"] == 0.0 and not r["condition_broken"]]
    broken = [r for r in rows if r["condition_broken"]]
    intact = [r for r in rows if r["magnitude"] > 0.0 and not r["condition_broken"]]
    mean = lambda xs: float(np.mean(xs)) if xs else float("nan")
    by_magnitude = {}
    for magnitude in sorted({r["magnitude"] for r in rows}):
        sel = [r for r in rows if r["magnitude"] == magnitude]
        by_magnitude[str(magnitude)] = {
            "conditions": len(sel),
            "gate_fire_rate": mean([r["gate_fired"] for r in sel]),
            "guarantee_broken_rate": mean([r["condition_broken"] for r in sel]),
            "ungated_fdp": mean([r["ungated_fdp"] for r in sel]),
            "ungated_false_alarms_per_1000": mean([r["ungated_false_alarms_per_1000"] for r in sel]),
            "gated_false_alarms_per_1000": mean([r["gated_false_alarms_per_1000"] for r in sel]),
        }
    detection = mean([r["gate_fired"] for r in broken])
    false_refusal = mean([r["gate_fired"] for r in exchangeable])
    return {
        "q": q,
        "conditions": len(rows),
        "guarantee_broken_conditions": len(broken),
        "detection_rate_where_broken": detection,
        "fire_rate_where_intact": mean([r["gate_fired"] for r in intact]),
        "false_refusal_on_exchangeable": false_refusal,
        "gate_passes": bool(broken and detection >= 0.9 and false_refusal <= 0.1),
        "by_magnitude": by_magnitude,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--methods", default="hedl")
    parser.add_argument("--magnitudes", default="0,0.1,0.25,0.5,0.75,1")
    parser.add_argument("--focus-classes", type=int, default=3)
    parser.add_argument("--min-class-flows", type=int, default=200)
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--audit-size", type=int, default=2000)
    parser.add_argument("--audit-alpha", type=float, default=0.05)
    parser.add_argument("--audit-threshold", default="dkw", choices=("dkw", "permutation"))
    parser.add_argument("--audit-permutations", type=int, default=200)
    parser.add_argument("--stream-size", type=int, default=40000)
    parser.add_argument("--window-size", type=int, default=2000)
    parser.add_argument("--prevalence", type=float, default=0.01)
    parser.add_argument("--q", type=float, default=0.1)
    parser.add_argument("--delta", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.magnitudes = tuple(float(v) for v in args.magnitudes.split(","))

    started = time.perf_counter()
    rows = []
    for method in (m.strip() for m in args.methods.split(",") if m.strip()):
        rows.extend(run_capture(args.tag, method, args))
        print(f"[shift_gate] {args.tag} {method}: {len(rows)} rows", flush=True)
    payload = {
        "protocol": "label_mix_shift_gate",
        "tag": args.tag,
        "config": {k: (list(v) if isinstance(v, tuple) else (str(v) if isinstance(v, Path) else v))
                   for k, v in vars(args).items()},
        "summary": summarise(rows, args.q),
        "rows": rows,
        "elapsed_seconds": time.perf_counter() - started,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))


if __name__ == "__main__":
    main()
