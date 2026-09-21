"""Record what produced the numbers: machine, versions, data, cost.

A table without this is a table nobody can check.  Everything here is read from
the machine and from the run state; nothing is typed by hand.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
PACKAGES = ("numpy", "scipy", "scikit-learn", "torch", "geoopt", "pandas", "pyyaml")


def _versions() -> dict[str, str]:
    from importlib import metadata

    versions = {"python": sys.version.split()[0]}
    for package in PACKAGES:
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            versions[package] = "absent"
    return versions


def _gpu() -> dict[str, object]:
    try:
        import torch

        if not torch.cuda.is_available():
            return {"cuda": False}
        return {"cuda": True, "device": torch.cuda.get_device_name(0),
                "capability": list(torch.cuda.get_device_capability(0)),
                "torch_cuda": torch.version.cuda}
    except Exception as error:  # pragma: no cover - environment dependent
        return {"cuda": "unknown", "error": repr(error)}


def _git() -> dict[str, str]:
    def run(*args: str) -> str:
        try:
            return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                                  text=True, check=False).stdout.strip()
        except OSError:
            return "unavailable"

    return {"commit": run("rev-parse", "HEAD"), "branch": run("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": bool(run("status", "--porcelain"))}


def _data_fingerprint() -> dict[str, object]:
    """Row counts and a content hash per partition split actually used."""
    fingerprint: dict[str, object] = {}
    for manifest in sorted((ROOT / "data" / "v7" / "partitions").glob("*")):
        if not manifest.is_dir():
            continue
        for rotation in sorted((manifest / "rq1").glob("*")):
            for split in ("train", "calibration", "test"):
                path = rotation / f"{split}.npz"
                if not path.exists():
                    continue
                archive = np.load(path, allow_pickle=False)
                digest = hashlib.sha256(np.ascontiguousarray(archive["x"]).tobytes()).hexdigest()[:16]
                fingerprint[f"{manifest.name}/{rotation.name}/{split}"] = {
                    "rows": int(len(archive["x"])), "features": int(archive["x"].shape[1]),
                    "sha256_16": digest,
                }
    return fingerprint


def _cost() -> dict[str, object]:
    """Wall-clock per stage, from the driver state files."""
    per_stage: dict[str, list[float]] = defaultdict(list)
    for state in sorted((ROOT / "results" / "run_logs").glob("*state*.json")):
        try:
            payload = json.loads(state.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for name, entry in payload.get("jobs", {}).items():
            if entry.get("ok"):
                per_stage[name.split("/")[0]].append(float(entry.get("seconds", 0.0)))
    return {stage: {"jobs": len(values), "hours": round(sum(values) / 3600.0, 2),
                    "median_minutes": round(float(np.median(values)) / 60.0, 1)}
            for stage, values in sorted(per_stage.items())}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/paper/environment.json"))
    args = parser.parse_args()
    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "platform": {"system": platform.system(), "release": platform.release(),
                     "machine": platform.machine(), "processor": platform.processor(),
                     "cpu_count": __import__("os").cpu_count()},
        "gpu": _gpu(),
        "versions": _versions(),
        "git": _git(),
        "cost_by_stage": _cost(),
        "data_fingerprint": _data_fingerprint(),
    }
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    total = sum(v["hours"] for v in report["cost_by_stage"].values())
    print(f"wrote {output}; {len(report['data_fingerprint'])} partition splits, "
          f"{total:.1f} GPU/CPU hours recorded")


if __name__ == "__main__":
    main()
