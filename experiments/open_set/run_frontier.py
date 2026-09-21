"""Where a detector stops being usable, and what that costs to find out.

AUROC answers "does the score rank attacks above known traffic", which every
detector in this study does well.  A deployment asks a different question:
"at the prevalence on my network, can anything built on this score fill an
alert queue that is mostly real?"  The answer is not monotone in AUROC across
datasets, and the gap between the two questions is where a detector that looks
finished turns out not to be.

This runner measures three things off a captured score file.

*The usability frontier.*  For each prevalence, the power a clairvoyant rule
would reach while holding the realised false fraction of the queue at or below
``q``.  It reads the labels, so no procedure can beat it; when it is zero, no
amount of calibration, conformal machinery or multiple-testing cleverness will
produce a usable queue, and the only remaining lever is the detector itself.

*The prevalence floor.*  The rarest prevalence at which that frontier still
clears a useful power level -- one number per detector, in the units an
operator already thinks in.

*The far tail.*  True-positive rate at false-alarm rates of 1e-2 down to 1e-5,
which is the region a low-prevalence alerting policy actually reads and the
region AUROC averages away.

*The failure shape.*  Two detectors can both be unusable at 1% prevalence for
completely different reasons, and the difference decides whether a result is
reportable.  One works when the false-alert budget is generous and collapses as
it shrinks -- that is the phenomenon this study is about, and an implementation
too broken to produce it would not reach a high ceiling anywhere.  The other is
already at zero where 55 false alerts out of 500 attacks are affordable, which
no budget argument explains and which an adapter fault explains just as well.
:func:`classify_failure_shape` separates them, so the second kind can be
reported without a claim attached.

*The seed spread.*  The ceiling is a property of the trained model, not of the
method: replication measured swings from 0.000 to 1.000 across training seeds of
one method on one dataset.  A point estimate is therefore not reportable, and
:func:`aggregate_over_seeds` collapses the per-capture rows into one row per
(dataset, method) carrying the range and the stability ratio.  Tables should be
built from that section, not from the per-capture one.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

from .run_resolution import clairvoyant_power


ROOT = Path(__file__).resolve().parents[2]
SCORES = ROOT / "results" / "scores"
RESULTS = ROOT / "results" / "frontier"


def far_tail_operating_points(
    known_scores: np.ndarray,
    unknown_scores: np.ndarray,
    false_alarm_rates: tuple[float, ...],
) -> dict[str, float]:
    """TPR at fixed false-alarm rates, with the resolution caveat attached.

    A false-alarm rate of ``1e-5`` cannot be read off ``m`` known flows unless
    ``m`` is comfortably above ``1e5``; the accompanying ``resolvable`` flag
    says whether the number underneath it is a measurement or an artefact of
    running out of sample.
    """
    report: dict[str, float] = {}
    for rate in false_alarm_rates:
        threshold = float(np.quantile(known_scores, 1.0 - rate))
        report[f"tpr_at_far_{rate:g}"] = float(np.mean(unknown_scores > threshold))
        report[f"resolvable_far_{rate:g}"] = float(len(known_scores) * rate >= 10.0)
    return report


def affordable_false_alerts(window_size: int, prevalence: float, q: float) -> int:
    """False alerts a queue may contain while staying inside the budget.

    The quantity that actually varies across a prevalence sweep.  With ``a``
    attacks in the window and a budget ``q``, a queue of ``a + f`` alerts keeps
    ``f / (a + f) <= q``, so ``f <= a q / (1 - q)``.  At 25% prevalence that is
    55 flows and a handful of known outliers is absorbed; at 1% it is 2 and a
    single one caps the queue.
    """
    attacks = max(1, int(round(window_size * prevalence)))
    return int(attacks * q / (1.0 - q))


def classify_failure_shape(
    curve: list[dict[str, float]], target_prevalence: float, useful_power: float
) -> str:
    """Name the failure so an unattributable one is not reported as a finding."""
    if not curve:
        return "unknown"
    best = max(row["clairvoyant_power"] for row in row_at_or_above(curve, target_prevalence))
    at_target = next(
        (row["clairvoyant_power"] for row in curve
         if abs(row["prevalence"] - target_prevalence) < 1e-12),
        0.0,
    )
    if at_target >= useful_power:
        return "usable_at_target"
    if best >= useful_power:
        # Works where the budget is generous, collapses as it tightens.
        return "budget_limited"
    return "uninformative_top"


def row_at_or_above(curve: list[dict[str, float]], prevalence: float) -> list[dict[str, float]]:
    return [row for row in curve if row["prevalence"] >= prevalence] or list(curve)


def frontier(
    known_scores: np.ndarray,
    unknown_scores: np.ndarray,
    prevalences: tuple[float, ...],
    q: float,
    window_size: int,
    repeats: int,
    seed: int,
    useful_power: float,
) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    curve: list[dict[str, float]] = []
    for prevalence in prevalences:
        unknown_count = max(1, min(window_size - 1, int(round(window_size * prevalence))))
        known_count = window_size - unknown_count
        powers = np.empty(repeats)
        for trial in range(repeats):
            scores = np.concatenate(
                [
                    rng.choice(known_scores, known_count, replace=known_count > len(known_scores)),
                    rng.choice(unknown_scores, unknown_count, replace=unknown_count > len(unknown_scores)),
                ]
            )
            is_unknown = np.concatenate(
                [np.zeros(known_count, dtype=bool), np.ones(unknown_count, dtype=bool)]
            )
            powers[trial] = clairvoyant_power(scores, is_unknown, q)["power"]
        curve.append(
            {
                "prevalence": float(prevalence),
                "attacks_per_window": float(unknown_count),
                "clairvoyant_power": float(powers.mean()),
                "clairvoyant_power_p10": float(np.quantile(powers, 0.1)),
                "windows_with_any_find": float(np.mean(powers > 0.0)),
            }
        )
    usable = [row for row in curve if row["clairvoyant_power"] >= useful_power]
    return {
        "useful_power_threshold": useful_power,
        "prevalence_floor": float(min(row["prevalence"] for row in usable)) if usable else None,
        "curve": curve,
    }


def _capture_identity(tag: str, metadata: dict) -> tuple[str, str]:
    """Split a capture tag into the thing that should vary and the thing that should not."""
    seed = str(metadata.get("seed", "unknown"))
    base = tag[: -len(f"_s{seed}")] if tag.endswith(f"_s{seed}") else tag
    return base, seed


def aggregate_over_seeds(scores: dict[str, dict]) -> dict[str, dict]:
    """One row per (dataset, method), carrying the spread across training seeds.

    ``stability_ratio`` is max/min of the ceiling at the target prevalence over
    the seeds, computed only where the minimum is above a floor -- a swing from
    0.000 to 1.000 has no meaningful ratio and is flagged by
    ``reverses_across_seeds`` instead, which is the more alarming condition
    anyway.
    """
    grouped: dict[tuple[str, str, str], list[dict]] = {}
    for entry in scores.values():
        key = (entry["dataset"], entry.get("scenario", "Z1"), entry["method"])
        grouped.setdefault(key, []).append(entry)

    aggregated: dict[str, dict] = {}
    for (dataset, scenario, method), entries in sorted(grouped.items()):
        prevalences = [row["prevalence"] for row in entries[0]["curve"]]
        per_prevalence = {}
        for index, prevalence in enumerate(prevalences):
            values = [entry["curve"][index]["clairvoyant_power"] for entry in entries]
            threshold = entries[0]["useful_power_threshold"]
            per_prevalence[str(prevalence)] = {
                "mean": float(np.mean(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "values": [float(value) for value in values],
                "usable_on_all_seeds": bool(all(value >= threshold for value in values)),
                "usable_on_no_seed": bool(all(value < threshold for value in values)),
                "stability_ratio": (
                    float(np.max(values) / np.min(values)) if np.min(values) > 0.005 else None
                ),
                "reverses_across_seeds": bool(
                    any(value >= threshold for value in values)
                    and any(value < threshold for value in values)
                ),
            }
        aurocs = [entry["unknown_auroc"] for entry in entries]
        shapes = sorted({entry["failure_shape"] for entry in entries})
        aggregated[f"{dataset}::{scenario}::{method}"] = {
            "dataset": dataset,
            "scenario": scenario,
            "method": method,
            "seeds": sorted(entry["seed"] for entry in entries),
            "seed_count": len(entries),
            "unknown_auroc_mean": float(np.mean(aurocs)),
            "unknown_auroc_range": [float(np.min(aurocs)), float(np.max(aurocs))],
            "failure_shapes_observed": shapes,
            "failure_shape_is_stable": len(shapes) == 1,
            "ceiling": per_prevalence,
        }
    return aggregated


def aggregate_over_rotations(by_scenario: dict[str, dict]) -> dict[str, dict]:
    """Does the choice of held-out attack family move the ceiling as much as the seed?

    Replication found the ceiling swinging by up to 16x across training seeds of
    one method on one rotation, which leaves an obvious open question: is the
    rotation -- which family is treated as the zero-day -- a comparable source of
    variation?  For every (dataset, method) this compares the spread of the
    per-rotation means with the largest spread across seeds inside any single
    rotation.  A rotation spread well above the seed spread means the held-out
    family matters and must be reported as its own axis; one well below means Z1
    was representative.
    """
    grouped: dict[tuple[str, str], list[dict]] = {}
    for row in by_scenario.values():
        grouped.setdefault((row["dataset"], row["method"]), []).append(row)

    report: dict[str, dict] = {}
    for (dataset, method), rows in sorted(grouped.items()):
        if len(rows) < 2:
            continue
        prevalences = list(rows[0]["ceiling"])
        per_prevalence = {}
        for prevalence in prevalences:
            means = {row["scenario"]: row["ceiling"][prevalence]["mean"] for row in rows}
            seed_spreads = [
                row["ceiling"][prevalence]["max"] - row["ceiling"][prevalence]["min"]
                for row in rows
            ]
            rotation_spread = float(max(means.values()) - min(means.values()))
            largest_seed_spread = float(max(seed_spreads))
            per_prevalence[prevalence] = {
                "mean_by_rotation": {k: float(v) for k, v in sorted(means.items())},
                "rotation_spread": rotation_spread,
                "largest_seed_spread_within_a_rotation": largest_seed_spread,
                "rotation_dominates_seed": bool(rotation_spread > largest_seed_spread),
            }
        report[f"{dataset}::{method}"] = {
            "dataset": dataset,
            "method": method,
            "rotations": sorted(row["scenario"] for row in rows),
            "ceiling": per_prevalence,
        }
    return report


def run(args: argparse.Namespace) -> dict[str, object]:
    report: dict[str, object] = {
        "protocol": "detector_usability_frontier",
        "q": args.q,
        "window_size": args.window_size,
        "repeats": args.repeats,
        "prevalences": list(args.prevalences),
        "scores": {},
    }
    missing: list[str] = []
    for tag in args.tags:
        # A capture that has not run yet must not kill the analysis: the full
        # experiment is resumable, so this runner is expected to be invoked
        # while part of the matrix is still outstanding.
        if not (SCORES / f"{tag}.npz").exists():
            missing.append(tag)
            continue
        arrays = np.load(SCORES / f"{tag}.npz")
        metadata = json.loads((SCORES / f"{tag}.json").read_text(encoding="utf-8"))
        present = [
            name for name in args.methods if f"{name}__test_scores" in arrays.files
        ] or [args.method]
        for method in present:
            _score_one(report, arrays, metadata, tag, method, args)
    if missing:
        print(f"[frontier] skipped {len(missing)} capture(s) not yet available", flush=True)
    report["captures_missing"] = missing
    report["by_dataset_and_method"] = aggregate_over_seeds(report["scores"])
    report["across_rotations"] = aggregate_over_rotations(report["by_dataset_and_method"])
    return report


def _score_one(report, arrays, metadata, tag, method, args) -> None:
    test_scores = arrays[f"{method}__test_scores"]
    is_unknown = arrays["test_is_unknown"]
    known_scores = test_scores[~is_unknown]
    unknown_scores = test_scores[is_unknown]
    key = tag if method == "hedl" and len(args.methods) <= 1 else f"{tag}::{method}"
    curve_report = frontier(
        known_scores,
        unknown_scores,
        args.prevalences,
        args.q,
        args.window_size,
        args.repeats,
        args.seed,
        args.useful_power,
    )
    base, seed = _capture_identity(tag, metadata)
    report["scores"][key] = {
        "dataset": metadata["dataset"],
        "scenario": str(metadata.get("scenario", "Z1")),
        "method": method,
        "capture": base,
        "seed": seed,
        "score_tail_extension": bool(metadata.get("tail_extension", False)),
        "unknown_auroc": float(roc_auc_score(is_unknown, test_scores)),
        "known_test_flows": int(len(known_scores)),
        "distinct_test_scores": int(len(np.unique(test_scores))),
        "test_scores_at_maximum": int(np.sum(test_scores >= test_scores.max() - 1e-12)),
        "far_tail": far_tail_operating_points(
            known_scores, unknown_scores, args.false_alarm_rates
        ),
        "affordable_false_alerts": {
            str(prevalence): affordable_false_alerts(args.window_size, prevalence, args.q)
            for prevalence in args.prevalences
        },
        "failure_shape": classify_failure_shape(
            curve_report["curve"], args.target_prevalence, args.useful_power
        ),
        **curve_report,
    }
    print(
        f"[frontier] {key}: auroc={report['scores'][key]['unknown_auroc']:.4f} "
        f"floor={report['scores'][key]['prevalence_floor']} "
        f"shape={report['scores'][key]['failure_shape']}",
        flush=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tags", default="cicids2017_Z1_s13,cicids2017_Z1_s13_tail")
    parser.add_argument("--method", default="hedl")
    parser.add_argument("--methods", default="hedl")
    parser.add_argument("--target-prevalence", type=float, default=0.01)
    parser.add_argument("--q", type=float, default=0.1)
    parser.add_argument("--window-size", type=int, default=2000)
    parser.add_argument("--repeats", type=int, default=300)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--useful-power", type=float, default=0.1)
    parser.add_argument("--prevalences", default="0.25,0.1,0.05,0.02,0.01,0.005,0.002,0.001")
    parser.add_argument("--false-alarm-rates", default="0.01,0.001,0.0001,0.00001")
    parser.add_argument("--output", type=Path, default=RESULTS / "usability_frontier.json")
    args = parser.parse_args()
    args.tags = tuple(v.strip() for v in args.tags.split(","))
    args.methods = tuple(v.strip() for v in args.methods.split(",") if v.strip())
    args.prevalences = tuple(float(v) for v in args.prevalences.split(","))
    args.false_alarm_rates = tuple(float(v) for v in args.false_alarm_rates.split(","))

    started = time.perf_counter()
    payload = run(args)
    payload["elapsed_seconds"] = time.perf_counter() - started
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"wrote {args.output} in {payload['elapsed_seconds']:.1f}s")


if __name__ == "__main__":
    main()
