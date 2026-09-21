"""Is the audit miscalibrated, or is the traffic really not exchangeable?

The label-mix experiment measures how often the gate refuses traffic that was
*meant* to be exchangeable: the capture's own known test flows, unshifted.  That
rate sits above the nominal level, and there are two candidate explanations.
Either the threshold is wrong -- it is asymptotic, and conformal p-values that
share a calibration sample are dependent -- or the premise is wrong, and a
capture's calibration split is not exchangeable with its own held-out known test
flows.

This runner separates them.  Drawing the audit sample from the calibration pool
itself is a null that is exchangeable *by construction*: if the gate fires at
the nominal rate there, the test is calibrated and the excess measured against
test traffic is a property of the data.  Both thresholds are evaluated on both
nulls, so neither explanation is assumed.

    python -m experiments.open_set.run_audit_null --output results/audit_null.json
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from .pact import exchangeability_audit
from .run_shift_gate import target_weights


ROOT = Path(__file__).resolve().parents[2]
SCORES = ROOT / "results" / "scores"


def capture_rates(tag: str, method: str, args: argparse.Namespace) -> list[dict[str, object]]:
    arrays = np.load(SCORES / f"{tag}.npz")
    metadata = json.loads((SCORES / f"{tag}.json").read_text(encoding="utf-8"))
    calibration = arrays[f"{method}__calibration_scores"].astype(np.float64)
    calibration_labels = arrays["calibration_labels"]
    test_scores = arrays[f"{method}__test_scores"].astype(np.float64)
    is_unknown = arrays["test_is_unknown"]
    known_test = test_scores[~is_unknown]
    known_labels = arrays["test_labels"][~is_unknown]
    # The label-mix experiment draws its s = 0 sample at the calibration class
    # mix, so the comparison here has to draw it the same way.
    classes, counts = np.unique(calibration_labels, return_counts=True)
    mix = {int(c): float(n / counts.sum()) for c, n in zip(classes, counts)}
    weights = target_weights(known_labels, mix, int(classes[0]), 0.0)

    rows = []
    for rule in ("dkw", "permutation"):
        for source in ("calibration", "test"):
            fired = 0
            for repeat in range(args.repeats):
                rng = np.random.default_rng(args.seed + 7919 * repeat)
                if source == "calibration":
                    # Exchangeable by construction: one pool, split at random.
                    order = rng.permutation(len(calibration))
                    sample = calibration[order[: args.audit_size]]
                    reference = calibration[order[args.audit_size:]]
                else:
                    sample = known_test[rng.choice(len(known_test), args.audit_size, p=weights)]
                    reference = calibration
                audit = exchangeability_audit(
                    reference, sample, args.audit_alpha,
                    threshold=rule, permutations=args.audit_permutations, seed=repeat,
                )
                fired += bool(audit["superuniform_audit_rejected"])
            rows.append({
                "dataset": metadata["dataset"], "seed": metadata.get("seed"),
                "method": method, "threshold": rule, "audit_source": source,
                "repeats": args.repeats, "fire_rate": fired / args.repeats,
            })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tags", default="")
    parser.add_argument("--methods", default="hedl")
    parser.add_argument("--repeats", type=int, default=100)
    parser.add_argument("--audit-size", type=int, default=2000)
    parser.add_argument("--audit-alpha", type=float, default=0.05)
    parser.add_argument("--audit-permutations", type=int, default=200)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    if not tags:
        tags = sorted(p.stem for p in (ROOT / "results" / "shift_gate").glob("*.json"))
    started = time.perf_counter()
    rows = []
    for tag in tags:
        for method in (m.strip() for m in args.methods.split(",") if m.strip()):
            rows.extend(capture_rates(tag, method, args))
        print(f"[audit_null] {tag}: {len(rows)} rows", flush=True)

    summary = {}
    for rule in ("dkw", "permutation"):
        for source in ("calibration", "test"):
            sel = [r["fire_rate"] for r in rows
                   if r["threshold"] == rule and r["audit_source"] == source]
            summary[f"{rule}::{source}"] = {
                "captures": len(sel), "mean_fire_rate": float(np.mean(sel)) if sel else float("nan"),
            }
    payload = {"protocol": "audit_null", "config": {k: (str(v) if isinstance(v, Path) else v)
                                                    for k, v in vars(args).items()},
               "summary": summary, "rows": rows,
               "elapsed_seconds": time.perf_counter() - started}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
