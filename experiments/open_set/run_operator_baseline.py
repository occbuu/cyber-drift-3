"""What an operator already does, measured against what PACT offers (R2).

Every alerting comparison in this study so far has been between multiple-testing
procedures.  A security operator does not run Benjamini-Hochberg: they put a
threshold at a false-positive budget read off the calibration scores -- "alert
on the top 0.1% of traffic" -- and live with whatever that produces.  A paper
claiming a deployment contribution has to beat, or at least price itself
against, that.

The comparison is made at matched alert volume, because volume is what costs an
analyst's time.  For each stream the percentile policy is run at several
budgets, and the conformal procedures are run at their own q; the table then
reports, for every arm, how many flows per thousand reach the operator, what
share of them are real, what share of the attacks present was caught, and --
the part only the conformal arms can fill in -- whether any of that came with a
promise that holds for the calibration sample in hand.
"""

from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

from .fdr import benjamini_hochberg, conformal_pvalues
from .resolution import training_conditional_pvalues
from .run_window import draw_stream


ROOT = Path(__file__).resolve().parents[2]
SCORES = ROOT / "results" / "scores"
PERCENTILES = (0.05, 0.01, 0.001)


def decide(scores, calibration, arm, q, delta, levels, percentile):
    if arm == "percentile":
        return scores > np.quantile(calibration, 1.0 - percentile)
    if arm == "marginal_bh":
        return benjamini_hochberg(conformal_pvalues(calibration, scores), q)
    return benjamini_hochberg(
        training_conditional_pvalues(calibration, scores, delta, levels), q
    )


def sweep(args: argparse.Namespace) -> dict[str, object]:
    arrays = np.load(SCORES / f"{args.tag}.npz")
    metadata = json.loads((SCORES / f"{args.tag}.json").read_text(encoding="utf-8"))
    calibration_all = arrays[f"{args.method}__calibration_scores"].astype(np.float64)
    test = arrays[f"{args.method}__test_scores"].astype(np.float64)
    unknown_mask = arrays["test_is_unknown"]
    known, unknown = test[~unknown_mask], test[unknown_mask]

    arms = [("percentile", p) for p in PERCENTILES]
    arms += [("marginal_bh", None), ("pact_conditional", None)]

    rows = []
    for size in args.calibration_sizes:
        size = min(size, len(calibration_all))
        for draw in range(args.calibration_draws):
            rng = np.random.default_rng(args.seed + 7919 * draw + size)
            calibration = (calibration_all if size == len(calibration_all)
                           else calibration_all[rng.choice(len(calibration_all), size, replace=False)])
            for prevalence in args.prevalences:
                cells = defaultdict(list)
                for _ in range(args.streams):
                    stream_rng = np.random.default_rng(args.seed + draw + 17)
                    scores, is_unknown = draw_stream(
                        known, unknown, args.stream_size, prevalence, stream_rng
                    )
                    windows = len(scores) // args.window_size
                    for arm, percentile in arms:
                        alerts = hits = attacks = 0
                        for index in range(windows):
                            chunk = slice(index * args.window_size, (index + 1) * args.window_size)
                            rejected = decide(scores[chunk], calibration, arm, args.q,
                                              args.delta, args.corrected_levels, percentile)
                            alerts += int(rejected.sum())
                            hits += int((rejected & is_unknown[chunk]).sum())
                            attacks += int(is_unknown[chunk].sum())
                        cells[(arm, percentile)].append({
                            "fdp": (alerts - hits) / alerts if alerts else 0.0,
                            "power": hits / attacks if attacks else 0.0,
                            "alerts_per_1000": 1000.0 * alerts / (windows * args.window_size),
                        })
                for (arm, percentile), trials in cells.items():
                    fdps = np.array([t["fdp"] for t in trials])
                    rows.append({
                        "dataset": metadata["dataset"], "seed": metadata.get("seed"),
                        "calibration_size": size, "calibration_draw": draw,
                        "prevalence": prevalence, "q": args.q,
                        "arm": arm, "percentile": percentile,
                        "claims_fdr": arm != "percentile",
                        "mean_fdp": float(fdps.mean()),
                        "streams_over_q": float(np.mean(fdps > args.q)),
                        "power": float(np.mean([t["power"] for t in trials])),
                        "alerts_per_1000": float(np.mean([t["alerts_per_1000"] for t in trials])),
                    })
            print(f"[operator] n={size} draw={draw} done", flush=True)
    return {"protocol": "operator_percentile_vs_conformal", "tag": args.tag,
            "method": args.method, "dataset": metadata["dataset"],
            "seed": metadata.get("seed"), "q": args.q, "delta": args.delta,
            "corrected_levels": args.corrected_levels, "rows": rows}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--method", default="hedl")
    parser.add_argument("--calibration-sizes", default="12000")
    parser.add_argument("--calibration-draws", type=int, default=5)
    parser.add_argument("--prevalences", default="0.01,0.001")
    parser.add_argument("--stream-size", type=int, default=40000)
    parser.add_argument("--streams", type=int, default=20)
    parser.add_argument("--window-size", type=int, default=2000)
    parser.add_argument("--q", type=float, default=0.1)
    parser.add_argument("--delta", type=float, default=0.1)
    parser.add_argument("--corrected-levels", type=int, default=5)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.calibration_sizes = tuple(int(v) for v in args.calibration_sizes.split(","))
    args.prevalences = tuple(float(v) for v in args.prevalences.split(","))

    started = time.perf_counter()
    payload = sweep(args)
    payload["elapsed_seconds"] = time.perf_counter() - started
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {args.output} ({len(payload['rows'])} rows)")


if __name__ == "__main__":
    main()
