"""Deployment latency of H-EDL, with and without the tail-lifted scorer.

The tail lift was previously scored on the NumPy reference path only, so its
cost at deployment was unknown.  This trains H-EDL once, fits the scorer both
ways on the same encoder, and times the device-resident path
(``run.deploy_hedl``) on the test split: encoder, predicted class and zero-day
score, one host transfer per batch.  It also checks that the device scorer
reproduces the NumPy scores, since a fast scorer that disagrees with the
fitted one would be measuring a different detector.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
from scipy.stats import spearmanr

from .conformal import COMPONENT_NAMES, ConformalFusionScorer
from .data import cap_open_set_data, encode_known_labels, load_rotation
from .fdr import stratified_calibration_split
from .models import DEFAULT_PROFILE
from .run import deploy_hedl, infer_hedl, seed_everything, train_hedl


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="cicids2017")
    parser.add_argument("--scenario", default="Z1")
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--inference-batch-sizes", default="256,1024,4096")
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--tuning-fraction", type=float, default=0.2)
    parser.add_argument("--tail-anchor-exceedances", type=int, default=250)
    parser.add_argument("--tail-confidence", type=float, default=0.9)
    parser.add_argument("--max-rows", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    seed_everything(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    data, _ = encode_known_labels(
        cap_open_set_data(load_rotation(args.dataset, args.scenario), args.max_rows, args.seed)
    )
    train = data.train.y >= 0
    calibration = data.calibration.y >= 0
    cal_x, cal_y = data.calibration.x[calibration], data.calibration.y[calibration]
    tuning, _ = stratified_calibration_split(cal_y, args.tuning_fraction, args.seed + 101)

    started = time.perf_counter()
    model = train_hedl(data.train.x[train], data.train.y[train], len(data.known_families), device,
                       args.epochs, args.batch_size, DEFAULT_PROFILE, 0.0)
    training_seconds = time.perf_counter() - started
    _, train_outputs, _ = infer_hedl(model, data.train.x[train], device, args.batch_size)
    _, tuning_outputs, _ = infer_hedl(model, cal_x[tuning], device, args.batch_size)
    _, test_outputs, _ = infer_hedl(model, data.test.x, device, args.batch_size)

    report: dict[str, object] = {
        "dataset": args.dataset, "scenario": args.scenario, "seed": args.seed,
        "device": str(device),
        "gpu": torch.cuda.get_device_name(device) if device.type == "cuda" else None,
        "test_flows": int(len(data.test.x)), "training_seconds": training_seconds, "variants": {},
    }
    for variant, tails in (("floored", False), ("tail_lifted", True)):
        scorer = ConformalFusionScorer(
            components=COMPONENT_NAMES, tail_extension=tails,
            tail_anchor_exceedances=args.tail_anchor_exceedances,
            tail_confidence=args.tail_confidence,
        ).fit(train_outputs, data.train.y[train], tuning_outputs, cal_y[tuning])
        reference = scorer.score(test_outputs)
        deployed = scorer.to_torch(device)
        timings = {}
        device_scores = None
        for batch in (int(v) for v in args.inference_batch_sizes.split(",")):
            deploy_hedl(model, deployed, data.test.x[: 4 * batch], device, batch)  # warm-up
            seconds = []
            for _ in range(args.repeats):
                _, device_scores, elapsed = deploy_hedl(model, deployed, data.test.x, device, batch)
                seconds.append(elapsed)
            timings[str(batch)] = {
                "ms_per_flow_median": 1000.0 * float(np.median(seconds)) / len(data.test.x),
                "flows_per_second_median": len(data.test.x) / float(np.median(seconds)),
            }
        rho = float(spearmanr(reference, device_scores).statistic)
        relative = np.abs(device_scores - reference) / np.maximum(np.abs(reference), 1e-9)
        report["variants"][variant] = {
            "timings": timings,
            "device_vs_reference_spearman": rho,
            "device_vs_reference_max_relative_error": float(relative.max()),
            "device_vs_reference_p99_relative_error": float(np.quantile(relative, 0.99)),
            "diagnostics": scorer.diagnostics(),
        }
        print(f"[latency] {variant}: {timings} spearman={rho:.6f}", flush=True)

    floored = report["variants"]["floored"]["timings"]
    lifted = report["variants"]["tail_lifted"]["timings"]
    report["tail_lift_overhead"] = {
        batch: lifted[batch]["ms_per_flow_median"] / floored[batch]["ms_per_flow_median"]
        for batch in floored
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["tail_lift_overhead"], indent=2))


if __name__ == "__main__":
    main()
