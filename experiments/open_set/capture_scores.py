"""Train once, score once, write the scores to disk.

Every question this study asks about alert quality -- how power depends on the
calibration budget, where the resolution barrier bites, what a parametric tail
buys, which constraint is binding -- is a function of three vectors: the
calibration scores, the test scores and which test flows are unknown.  None of
it needs the network again.  Separating the expensive step from the analysis
keeps the sweeps honest as well as fast: every configuration in a sweep reads
exactly the same scores, so a difference between two rows cannot be a different
training run in disguise.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import roc_auc_score

from .conformal import COMPONENT_NAMES
from .data import (
    cap_open_set_data,
    encode_known_labels,
    hold_out_groups,
    load_holdout_groups,
    load_rotation,
)
from .fdr import stratified_calibration_split
from .metrics import evaluate_open_set
from .models import DEFAULT_PROFILE, PROFILES
from .run import seed_everything
from .run_fdr import _score_method, _unique_source_indices


ROOT = Path(__file__).resolve().parents[2]
SCORES = ROOT / "results" / "scores"


def capture(args: argparse.Namespace) -> dict[str, object]:
    seed_everything(args.seed)
    rotation = load_rotation(args.dataset, args.scenario)
    if args.holdout_groups:
        rotation = hold_out_groups(
            rotation, load_holdout_groups(args.dataset, args.holdout_threshold)
        )
    raw = cap_open_set_data(rotation, args.max_rows, args.seed)
    data, _ = encode_known_labels(raw)
    train_mask = data.train.y >= 0
    calibration_mask = data.calibration.y >= 0
    calibration_x = data.calibration.x[calibration_mask]
    calibration_y = data.calibration.y[calibration_mask]
    calibration_source_ids = data.calibration.source_ids[calibration_mask]
    test_x = data.test.x
    test_y = data.test.y
    if args.deduplicate_source_ids:
        keep = _unique_source_indices(calibration_source_ids)
        calibration_x, calibration_y = calibration_x[keep], calibration_y[keep]
        keep = _unique_source_indices(data.test.source_ids)
        test_x, test_y = test_x[keep], test_y[keep]

    # The scorer is tuned on one half and calibrated on the other: the fusion
    # weights must be fixed before the p-value denominators are observed, or
    # the calibration scores stop being exchangeable with the test knowns.
    tuning_indices, calibration_indices = stratified_calibration_split(
        calibration_y, args.tuning_fraction, args.seed + 101
    )
    is_unknown = test_y < 0
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    methods: dict[str, object] = {}
    arrays: dict[str, np.ndarray] = {
        "test_is_unknown": is_unknown,
        "calibration_labels": calibration_y[calibration_indices],
        "test_labels": test_y,
    }
    for method in args.methods:
        started = time.perf_counter()
        seed_everything(args.seed)
        (
            calibration_scores,
            test_scores,
            calibration_predictions,
            test_predictions,
            diagnostics,
        ) = _score_method(
            method,
            data.train.x[train_mask],
            data.train.y[train_mask],
            calibration_x[tuning_indices],
            calibration_y[tuning_indices],
            calibration_x[calibration_indices],
            test_x,
            len(data.known_families),
            device,
            args.epochs,
            args.inference_batch_size,
            args.seed,
            args.profile,
            args.scorer_components,
            args.curvature,
            args.tail_extension,
            args.tail_anchor_exceedances,
            args.tail_confidence,
            args.evidential_weight,
            args.margin_weight,
        )
        arrays[f"{method}__calibration_scores"] = calibration_scores
        arrays[f"{method}__test_scores"] = test_scores
        arrays[f"{method}__calibration_predictions"] = calibration_predictions
        arrays[f"{method}__test_predictions"] = test_predictions
        open_set = evaluate_open_set(test_y, test_predictions, test_scores)
        methods[method] = {
            "diagnostics": diagnostics,
            "open_set": open_set,
            "unknown_auroc": float(roc_auc_score(is_unknown, test_scores)),
            "distinct_calibration_scores": int(len(np.unique(calibration_scores))),
            "distinct_test_scores": int(len(np.unique(test_scores))),
            "test_scores_at_maximum": int(np.sum(test_scores >= test_scores.max() - 1e-12)),
            "seconds": float(time.perf_counter() - started),
        }
        print(
            f"[capture] {method}: auroc={methods[method]['unknown_auroc']:.4f} "
            f"in {methods[method]['seconds']:.1f}s",
            flush=True,
        )

    return {
        "dataset": args.dataset,
        "scenario": args.scenario,
        "seed": args.seed,
        "epochs": args.epochs,
        "profile": args.profile,
        "curvature": args.curvature,
        "tuning_fraction": args.tuning_fraction,
        "tail_extension": bool(args.tail_extension),
        "tail_anchor_exceedances": int(args.tail_anchor_exceedances),
        "tail_confidence": float(args.tail_confidence),
        "deduplicate_source_ids": bool(args.deduplicate_source_ids),
        "holdout_groups": bool(args.holdout_groups),
        "evidential_weight": float(args.evidential_weight),
        "margin_weight": float(args.margin_weight),
        "holdout_threshold": args.holdout_threshold,
        "device": str(device),
        "known_families": list(data.known_families),
        "unknown_families": list(data.unknown_families),
        "tuning_size": int(len(tuning_indices)),
        "calibration_size": int(len(calibration_indices)),
        "test_known": int((~is_unknown).sum()),
        "test_unknown": int(is_unknown.sum()),
        "methods": methods,
    }, arrays


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="cicids2017")
    parser.add_argument("--scenario", default="Z1")
    parser.add_argument("--methods", default="hedl")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--profile", choices=sorted(PROFILES), default=DEFAULT_PROFILE)
    parser.add_argument("--curvature", type=float, default=0.0)
    parser.add_argument("--scorer-components", default=",".join(COMPONENT_NAMES))
    parser.add_argument("--tuning-fraction", type=float, default=0.2)
    parser.add_argument("--inference-batch-size", type=int, default=256)
    parser.add_argument("--max-rows", type=int)
    parser.add_argument(
        "--deduplicate-source-ids", action=argparse.BooleanOptionalAction, default=True
    )
    parser.add_argument(
        "--tail-extension", action=argparse.BooleanOptionalAction, default=False
    )
    # Hold out whole inseparable family groups (experiments.open_set.separability).
    parser.add_argument(
        "--holdout-groups", action=argparse.BooleanOptionalAction, default=True
    )
    # Sensitivity only: read the groups the audit recorded at another threshold.
    parser.add_argument("--holdout-threshold", type=float, default=None)
    # Loss-term ablation: 0 removes the Dirichlet evidential term, leaving the
    # prototype cross-entropy and the margin, so the name can be checked against
    # what the term actually buys.
    parser.add_argument("--evidential-weight", type=float, default=1.0)
    parser.add_argument("--margin-weight", type=float, default=1.0)
    parser.add_argument("--tail-anchor-exceedances", type=int, default=250)
    parser.add_argument("--tail-confidence", type=float, default=0.0)
    parser.add_argument("--tag", default=None)
    args = parser.parse_args()
    args.methods = tuple(name.strip() for name in args.methods.split(",") if name.strip())
    args.scorer_components = tuple(
        name.strip() for name in args.scorer_components.split(",") if name.strip()
    )

    metadata, arrays = capture(args)
    tag = args.tag or f"{args.dataset}_{args.scenario}_seed{args.seed}"
    SCORES.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(SCORES / f"{tag}.npz", **arrays)
    (SCORES / f"{tag}.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps({"scores": str(SCORES / f"{tag}.npz"), **{
        "calibration_size": metadata["calibration_size"],
        "test_known": metadata["test_known"],
        "test_unknown": metadata["test_unknown"],
    }}, indent=2))


if __name__ == "__main__":
    main()
