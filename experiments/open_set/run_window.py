"""Where the alert-window size should sit, and what shrinking it costs.

Proposition 10 says a single attack becomes alertable once ``r_min = 1``, which
happens when ``n >= m ln(1/delta) / q`` -- so unlike the barrier itself, this
condition depends on the window.  A deployment that cannot buy calibration can
therefore batch less traffic per decision instead.

That reads like a free lunch and is not one, for a reason the per-window
measurements used elsewhere in this study cannot see.  Benjamini-Hochberg
controls the false-discovery rate *of a window*.  An operator works a queue, and
the queue is the union of a day's windows.  Controlling FDR separately in each
of ``K`` windows is a weaker statement than controlling it over their union, and
in the limit ``m -> 1`` the procedure degenerates to testing each flow at level
``q`` -- a 10% false-alarm rate, which at an attack prevalence of ``10^-3`` is
precisely the failure this project is about.

So this runner measures the stream, not the window.  A stream of
``stream_size`` flows is drawn at the requested prevalence **without forcing a
minimum attack count** -- the per-window attack counts are then naturally
Binomial, which also removes the rounding artefact that inflates prevalence in
small windows -- partitioned into windows of size ``m``, and each window decided
independently.  What is reported is the *aggregate* over the stream: the false
fraction of everything the operator was asked to look at, and the share of all
attacks in the stream that reached them.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np

from .fdr import (
    benjamini_hochberg,
    benjamini_yekutieli,
    conformal_evalues,
    conformal_pvalues,
    e_benjamini_hochberg,
    storey_benjamini_hochberg,
)
from .resolution import (
    minimum_rejections,
    training_conditional_floor,
    training_conditional_pvalues,
)
from .tail import TailExtendedCalibration


ROOT = Path(__file__).resolve().parents[2]
SCORES = ROOT / "results" / "scores"
RESULTS = ROOT / "results" / "window"

PROCEDURES = (
    "distribution_free",
    "training_conditional",
    "benjamini_yekutieli",
    "storey_bh",
    "e_bh",
    "tail_conditional",
)


def draw_stream(
    known_pool: np.ndarray,
    unknown_pool: np.ndarray,
    stream_size: int,
    prevalence: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """A stream at the requested prevalence, with the attack count left random.

    Every other sweep in this study forces at least one attack into each window,
    which is right when the question is "can BH react to an attack that is
    present" and wrong here: at ``m = 500`` and ``pi = 10^-3`` that forcing
    doubles the realised prevalence and would manufacture exactly the advantage
    for small windows that this runner exists to test.
    """
    attacks = int(rng.binomial(stream_size, prevalence))
    attacks = min(attacks, stream_size)
    knowns = stream_size - attacks
    scores = np.concatenate(
        [
            rng.choice(known_pool, knowns, replace=knowns > len(known_pool)),
            rng.choice(unknown_pool, attacks, replace=attacks > len(unknown_pool)),
        ]
    )
    is_unknown = np.concatenate(
        [np.zeros(knowns, dtype=bool), np.ones(attacks, dtype=bool)]
    )
    order = rng.permutation(stream_size)
    return scores[order], is_unknown[order]


def decide_stream(
    scores: np.ndarray,
    is_unknown: np.ndarray,
    calibration: np.ndarray,
    window_size: int,
    q: float,
    procedure: str,
    delta: float,
    tail: TailExtendedCalibration | None = None,
    corrected_levels: int = 1,
) -> dict[str, float]:
    """Partition the stream into windows, decide each, aggregate over the union."""
    total = len(scores)
    windows = max(1, total // window_size)
    alerts = 0
    true_alerts = 0
    window_fdps: list[float] = []
    for index in range(windows):
        chunk = slice(index * window_size, (index + 1) * window_size)
        window_scores = scores[chunk]
        window_unknown = is_unknown[chunk]
        if procedure == "training_conditional":
            rejected = benjamini_hochberg(
                training_conditional_pvalues(
                    calibration, window_scores, delta, corrected_levels
                ),
                q,
            )
        elif procedure == "benjamini_yekutieli":
            rejected = benjamini_yekutieli(conformal_pvalues(calibration, window_scores), q)
        elif procedure == "storey_bh":
            rejected = storey_benjamini_hochberg(
                conformal_pvalues(calibration, window_scores), q
            )
        elif procedure == "tail_conditional":
            # Conditional validity bought from a tail model instead of from a
            # single order statistic.  The Beta bound has to pay for the
            # variance of one calibration point; a peaks-over-threshold fit
            # pools several hundred exceedances, so its upper confidence bound
            # at the same delta can be tighter where BH actually stops.
            rejected = benjamini_hochberg(tail.pvalues(window_scores), q)
        elif procedure == "e_bh":
            rejected = e_benjamini_hochberg(
                conformal_evalues(calibration, window_scores, top_k=1), q
            )
        else:
            rejected = benjamini_hochberg(conformal_pvalues(calibration, window_scores), q)
        count = int(rejected.sum())
        hits = int((rejected & window_unknown).sum())
        alerts += count
        true_alerts += hits
        if count:
            window_fdps.append((count - hits) / count)
    attacks = int(is_unknown[: windows * window_size].sum())
    return {
        "windows": float(windows),
        "alerts": float(alerts),
        "true_alerts": float(true_alerts),
        "attacks": float(attacks),
        "aggregate_fdp": float((alerts - true_alerts) / alerts) if alerts else 0.0,
        "aggregate_power": float(true_alerts / attacks) if attacks else 0.0,
        "mean_window_fdp": float(np.mean(window_fdps)) if window_fdps else 0.0,
        "windows_that_fired": float(len(window_fdps)),
        "alerts_per_1000_flows": float(1000.0 * alerts / (windows * window_size)),
    }


def sweep(args: argparse.Namespace) -> dict[str, object]:
    arrays = np.load(SCORES / f"{args.tag}.npz")
    metadata = json.loads((SCORES / f"{args.tag}.json").read_text(encoding="utf-8"))
    calibration_scores = arrays[f"{args.method}__calibration_scores"]
    test_scores = arrays[f"{args.method}__test_scores"]
    is_unknown = arrays["test_is_unknown"]

    rng = np.random.default_rng(args.seed)
    known_scores = test_scores[~is_unknown]
    unknown_scores = test_scores[is_unknown]

    rows: list[dict[str, object]] = []
    for size in args.calibration_sizes:
        size = min(size, len(calibration_scores))
        for draw in range(args.calibration_draws):
            draw_rng = np.random.default_rng(args.seed + 7919 * draw + size)
            calibration = (
                calibration_scores
                if size == len(calibration_scores)
                else calibration_scores[
                    draw_rng.choice(len(calibration_scores), size, replace=False)
                ]
            )
            for prevalence in args.prevalences:
                for window_size in args.window_sizes:
                    for procedure in args.procedures:
                        tail = None
                        if procedure == "tail_conditional":
                            tail = TailExtendedCalibration(
                                anchor_exceedances=min(
                                    args.tail_anchor_exceedances, max(10, size // 4)
                                ),
                                confidence=1.0 - args.delta,
                            ).fit(calibration)
                        trials = []
                        stream_rng = np.random.default_rng(args.seed + draw)
                        for _ in range(args.streams):
                            scores, unknown = draw_stream(
                                known_scores,
                                unknown_scores,
                                args.stream_size,
                                prevalence,
                                stream_rng,
                            )
                            trials.append(
                                decide_stream(
                                    scores,
                                    unknown,
                                    calibration,
                                    window_size,
                                    args.q,
                                    procedure,
                                    args.delta,
                                    tail,
                                    args.corrected_levels,
                                )
                            )
                        aggregate = {
                            key: float(np.mean([trial[key] for trial in trials]))
                            for key in trials[0]
                        }
                        fdps = np.array([trial["aggregate_fdp"] for trial in trials])
                        floor = (
                            training_conditional_floor(size, args.delta)
                            if procedure == "training_conditional"
                            else 1.0 / (size + 1.0)
                        )
                        rows.append(
                            {
                                **aggregate,
                                "calibration_size": size,
                                "calibration_draw": draw,
                                "prevalence": prevalence,
                                "window_size": window_size,
                                "procedure": procedure,
                                "q": args.q,
                                "pvalue_floor": float(floor),
                                "minimum_rejections": float(
                                    math.ceil(floor * window_size / args.q)
                                ),
                                "streams_over_budget": float(np.mean(fdps > args.q)),
                                "aggregate_fdp_max": float(fdps.max()),
                            }
                        )
            print(f"[window] n={size} draw={draw} done", flush=True)

    return {
        "protocol": "alert_window_size_sweep",
        "scores_tag": args.tag,
        "method": args.method,
        "dataset": metadata["dataset"],
        "seed": metadata.get("seed"),
        "stream_size": args.stream_size,
        "streams_per_cell": args.streams,
        "calibration_draws": args.calibration_draws,
        "delta": args.delta,
        "corrected_levels": args.corrected_levels,
        "q": args.q,
        "note": (
            "Attack counts are Binomial, not forced, so small windows get no "
            "artificial prevalence boost."
        ),
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default="nf_cse_cic_ids2018_v3_Z1_s13_tail")
    parser.add_argument("--method", default="hedl")
    parser.add_argument("--stream-size", type=int, default=40000)
    parser.add_argument("--streams", type=int, default=20)
    parser.add_argument("--calibration-draws", type=int, default=5)
    parser.add_argument("--calibration-sizes", default="12000,23932")
    parser.add_argument("--window-sizes", default="100,250,500,1000,2000,4000")
    parser.add_argument("--prevalences", default="0.01,0.001")
    parser.add_argument("--procedures", default=",".join(PROCEDURES))
    parser.add_argument("--q", type=float, default=0.1)
    parser.add_argument("--delta", type=float, default=0.1)
    parser.add_argument("--tail-anchor-exceedances", type=int, default=250)
    # BH interrogates its line at one level per rejection, so the Beta bound's
    # pointwise confidence has to be split across the levels it will be read at.
    parser.add_argument("--corrected-levels", type=int, default=1)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    args.calibration_sizes = tuple(int(v) for v in args.calibration_sizes.split(","))
    args.window_sizes = tuple(int(v) for v in args.window_sizes.split(","))
    args.prevalences = tuple(float(v) for v in args.prevalences.split(","))
    args.procedures = tuple(v.strip() for v in args.procedures.split(","))

    started = time.perf_counter()
    payload = sweep(args)
    payload["elapsed_seconds"] = time.perf_counter() - started
    output = args.output or RESULTS / f"{args.tag}_{args.method}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"wrote {output} in {payload['elapsed_seconds']:.1f}s ({len(payload['rows'])} rows)")


if __name__ == "__main__":
    main()
