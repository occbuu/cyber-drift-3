"""Time-ordered partitions: calibrate on the past, alert on the future (R1).

Every stream in this study so far was drawn by resampling test scores
independently.  That construction *guarantees* the exchangeability conformal
prediction needs, which makes it the wrong evidence for a deployment claim: the
experiment cannot fail in the way a deployment fails.  A network changes over
the week; the calibration sample an operator has is always older than the
traffic being scored.

This builder rebuilds a rotation along that axis.  The NetFlow v3 captures carry
``FLOW_START_MILLISECONDS``, so flows can be ordered in time: the earliest
``early_fraction`` of the capture window supplies training and calibration, the
remainder supplies the test split, and the held-out attack family is removed
from the early period exactly as in the frozen rotations.  Nothing else changes
-- same feature schema, same v7 scaling, same caps -- so the temporal numbers
sit next to the random-split numbers and the difference is the time axis alone.

Two passes over the raw file: the first reads the timestamp and label columns to
find the split point and the per-family counts, the second samples to the caps.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from .data import NETFLOW_FILES, V7_ROOT, load_rotation


TIME_COLUMN = "FLOW_START_MILLISECONDS"


def _families(series: pd.Series) -> pd.Series:
    """Raw label to v7 family name.

    The captures spell the same family several ways -- "DDOS attack-HOIC",
    "FTP-BruteForce", "Brute Force -Web" -- so every run of spaces and hyphens
    collapses to a single underscore, which is the v7 convention.
    """
    return (series.astype(str).str.strip().str.lower()
            .str.replace(r"[\s\-]+", "_", regex=True).str.strip("_"))


def scan_time_and_labels(path: Path, chunk_size: int) -> tuple[np.ndarray, pd.Series]:
    starts, families = [], []
    for chunk in pd.read_csv(path, usecols=[TIME_COLUMN, "Attack"], chunksize=chunk_size):
        starts.append(chunk[TIME_COLUMN].to_numpy(dtype=np.int64))
        families.append(_families(chunk["Attack"]))
        print(f"  [scan] {sum(len(s) for s in starts):,} rows", flush=True)
    return np.concatenate(starts), pd.concat(families, ignore_index=True)


def keep_probabilities(counts: dict[str, int], cap: int) -> dict[str, float]:
    """Equal per-family target, capped by what the period actually holds."""
    if not counts:
        return {}
    target = max(1, cap // len(counts))
    return {family: min(1.0, target / max(1, count)) for family, count in counts.items()}


def build(args: argparse.Namespace) -> dict[str, object]:
    path = NETFLOW_FILES[args.dataset]
    reference = load_rotation(args.dataset, args.reference_scenario)
    feature_names = list(reference.feature_names)
    raw_columns = [name.upper() for name in feature_names]
    manifest_path = V7_ROOT / "manifests" / f"{args.dataset}_v7.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    rotation = manifest["rq1"]["rotations"][args.reference_scenario]
    unknown_families = list(rotation["unknown_classes"])

    print(f"[temporal] scanning {path}", flush=True)
    starts, families = scan_time_and_labels(path, args.chunk_size)

    # These testbeds stage their attacks: each family tends to occupy its own
    # stretch of the capture.  A single chronological cut therefore does not
    # merely introduce drift, it changes the label space -- which is itself worth
    # recording, and is why the per-family mode exists.
    spans = {}
    for family in sorted(set(families)):
        member = families.to_numpy() == family
        spans[family] = {"rows": int(member.sum()),
                         "first": int(starts[member].min()),
                         "last": int(starts[member].max())}
    if args.mode == "chronological":
        split_at = float(np.quantile(starts, args.early_fraction))
        early_mask = starts <= split_at
        family_split = {}
    else:
        # Per-family cut: every family keeps its earliest `early_fraction` for
        # training and calibration, so the label space is preserved and the only
        # difference between calibration and test is when the flow happened.
        family_split = {family: float(np.quantile(starts[families.to_numpy() == family],
                                                  args.early_fraction))
                        for family in spans}
        cutoffs = families.map(family_split).to_numpy(dtype=np.float64)
        early_mask = starts <= cutoffs
        split_at = float(np.median(list(family_split.values())))
    print(f"[temporal] {len(starts):,} flows; split at {split_at:.0f} "
          f"({early_mask.mean():.1%} early)", flush=True)

    early_counts = families[early_mask].value_counts().to_dict()
    late_counts = families[~early_mask].value_counts().to_dict()
    for family in unknown_families:
        early_counts.pop(family, None)
    known_families = tuple(sorted(early_counts))
    manifest_families = set(rotation["known_classes"]) | set(unknown_families)
    unmatched = sorted(set(spans) - manifest_families)
    if unmatched:
        print(f"[temporal] WARNING raw families absent from the manifest: {unmatched}", flush=True)
    missing = sorted(manifest_families - set(spans))
    if missing:
        print(f"[temporal] WARNING manifest families absent from the raw file: {missing}", flush=True)
    if not set(unknown_families).intersection(late_counts):
        raise ValueError(
            f"The held-out family {unknown_families} does not appear in the late period; "
            f"raw families seen: {sorted(spans)[:12]}"
        )

    early_probability = keep_probabilities(early_counts, args.train_cap + args.calibration_cap)
    # Families that appear only after the split are dropped from the test split:
    # they are neither known (never trained) nor the designated zero-day, and
    # keeping them would silently change what "known traffic" means.  How many
    # there are is itself reported -- it measures how staged the capture is.
    late_only = sorted(set(late_counts) - set(known_families) - set(unknown_families))
    if late_only:
        print(f"[temporal] families present only after the split, dropped from test: {late_only}",
              flush=True)
    late_probability = keep_probabilities(
        {f: c for f, c in late_counts.items() if f in known_families or f in unknown_families},
        args.test_cap,
    )

    transform = json.loads(
        (V7_ROOT / "partitions" / args.dataset / "rq1" / args.reference_scenario
         / "transform.json").read_text(encoding="utf-8")
    )
    offsets = np.array([transform["features"][n]["offset"] for n in feature_names], dtype=np.float64)
    scales = np.array([transform["features"][n]["scale"] for n in feature_names], dtype=np.float64)

    rng = np.random.default_rng(args.seed)
    kept: dict[str, list] = {"early_x": [], "early_family": [], "early_time": [],
                             "late_x": [], "late_family": [], "late_time": []}
    offset_rows = 0
    for chunk in pd.read_csv(path, usecols=[*raw_columns, TIME_COLUMN, "Attack"],
                             chunksize=args.chunk_size):
        chunk_families = _families(chunk["Attack"]).to_numpy()
        chunk_time = chunk[TIME_COLUMN].to_numpy(dtype=np.int64)
        values = chunk[raw_columns].replace([np.inf, -np.inf], np.nan).fillna(0.0).to_numpy(np.float64)
        if args.mode == "chronological":
            is_early = chunk_time <= split_at
        else:
            cutoff = np.array([family_split.get(f, split_at) for f in chunk_families])
            is_early = chunk_time <= cutoff
        draw = rng.random(len(chunk))
        early_keep = np.array([early_probability.get(f, 0.0) for f in chunk_families])
        late_keep = np.array([late_probability.get(f, 0.0) for f in chunk_families])
        take_early = is_early & (draw < early_keep)
        take_late = (~is_early) & (draw < late_keep)
        for prefix, mask in (("early", take_early), ("late", take_late)):
            if mask.any():
                kept[f"{prefix}_x"].append(values[mask])
                kept[f"{prefix}_family"].append(chunk_families[mask])
                kept[f"{prefix}_time"].append(chunk_time[mask])
        offset_rows += len(chunk)
        print(f"  [sample] {offset_rows:,} rows scanned; "
              f"early {sum(len(a) for a in kept['early_x']):,} "
              f"late {sum(len(a) for a in kept['late_x']):,}", flush=True)

    early_x = np.concatenate(kept["early_x"])
    early_family = np.concatenate(kept["early_family"])
    early_time = np.concatenate(kept["early_time"])
    late_x = np.concatenate(kept["late_x"])
    late_family = np.concatenate(kept["late_family"])
    late_time = np.concatenate(kept["late_time"])

    # Train and calibration both come from the early period and are split within
    # each family.  A second time cut here would be more faithful still, but the
    # families are themselves staged inside the early window, so a time cut
    # leaves whole classes out of one side -- on nf_ton_iot_v3 it produced six
    # families in train and four in calibration.  What the protocol has to
    # preserve is that every calibration flow predates every test flow of its
    # family, and that holds by construction.
    train_index, calibration_index = [], []
    split_rng = np.random.default_rng(args.seed + 5)
    for family in np.unique(early_family):
        member = np.flatnonzero(early_family == family)
        split_rng.shuffle(member)
        cut = max(1, int(len(member) * args.train_fraction))
        train_index.append(member[:cut])
        calibration_index.append(member[cut:])
    train_index = np.concatenate(train_index)
    calibration_index = np.concatenate(calibration_index)
    splits = {
        "train": (early_x[train_index], early_family[train_index], early_time[train_index]),
        "calibration": (early_x[calibration_index], early_family[calibration_index],
                        early_time[calibration_index]),
        "test": (late_x, late_family, late_time),
    }

    label_map = {family: index for index, family in enumerate(known_families)}
    base = V7_ROOT / "partitions" / args.dataset / "rq1" / args.scenario
    base.mkdir(parents=True, exist_ok=True)
    written = {}
    for name, (x, family, times) in splits.items():
        scaled = ((x - offsets) / scales).astype(np.float32)
        labels = np.array([label_map.get(f, -1) for f in family], dtype=np.int64)
        source_ids = np.array(
            [hashlib.sha256(f"{args.scenario}|{t}|{row.tobytes().hex()}".encode()).hexdigest()
             for t, row in zip(times, x)], dtype=object
        ).astype(str)
        np.savez_compressed(
            base / f"{name}.npz", x=scaled, y=labels, families=family.astype(str),
            source_ids=source_ids, feature_names=np.array(feature_names, dtype=str),
            flow_start_milliseconds=times,
        )
        written[name] = {"rows": int(len(scaled)),
                         "families": {str(k): int(v) for k, v in
                                      zip(*np.unique(family, return_counts=True))},
                         "time_range": [int(times.min()), int(times.max())]}
        print(f"[temporal] wrote {name}: {len(scaled):,} rows", flush=True)
    (base / "transform.json").write_text(json.dumps(transform, indent=2), encoding="utf-8")

    manifest["rq1"]["rotations"][args.scenario] = {
        "train": f"../partitions/{args.dataset}/rq1/{args.scenario}/train.npz",
        "calibration": f"../partitions/{args.dataset}/rq1/{args.scenario}/calibration.npz",
        "test": f"../partitions/{args.dataset}/rq1/{args.scenario}/test.npz",
        "known_classes": list(known_families),
        "unknown_classes": unknown_families,
        "seeds": [13, 37, 73, 101, 137],
        "exploratory": False,
        "note": (f"Temporal split built {args.scenario} from {path.name}: earliest "
                 f"{args.early_fraction:.0%} of FLOW_START_MILLISECONDS supplies train and "
                 f"calibration, the rest supplies test. Held-out family removed from the "
                 f"early period only. Mode: {args.mode}."),
    }
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    report = {"dataset": args.dataset, "scenario": args.scenario,
              "mode": args.mode, "late_only_families": late_only, "family_time_spans": spans,
              "per_family_split_at": family_split,
              "reference_scenario": args.reference_scenario,
              "split_at_milliseconds": split_at, "early_fraction": args.early_fraction,
              "known_families": list(known_families), "unknown_families": unknown_families,
              "splits": written}
    (base / "temporal_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, choices=sorted(NETFLOW_FILES))
    parser.add_argument("--scenario", default="T1")
    parser.add_argument("--reference-scenario", default="Z1")
    parser.add_argument("--mode", default="per_family",
                        choices=("chronological", "per_family"))
    parser.add_argument("--early-fraction", type=float, default=0.6)
    parser.add_argument("--train-fraction", type=float, default=0.75)
    parser.add_argument("--train-cap", type=int, default=90000)
    parser.add_argument("--calibration-cap", type=int, default=30000)
    parser.add_argument("--test-cap", type=int, default=60000)
    parser.add_argument("--chunk-size", type=int, default=2_000_000)
    parser.add_argument("--seed", type=int, default=13)
    args = parser.parse_args()
    print(json.dumps(build(args), indent=2)[:2000])


if __name__ == "__main__":
    main()
