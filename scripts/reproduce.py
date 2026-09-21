"""One command from a clone to every table in the paper.

Running this end to end costs about 107 machine-hours on the hardware recorded
in results/paper/environment.json, so it is staged: each stage writes one file
per job and a job whose output exists is skipped.  Stopping and restarting is
safe, and `--dry-run` prints the plan without doing anything.

    python scripts/reproduce.py --dry-run          # what would run
    python scripts/reproduce.py --stage analysis   # tables only, minutes
    python scripts/reproduce.py                    # everything

`analysis` needs the score captures; `capture` produces them and is the part
that needs a GPU.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STAGES = {
    # name: (what it does, driver stages)
    "separability": ("label-separability audit that defines the hold-out groups", None),
    "capture": ("train every detector once per dataset, seed and rotation (GPU)",
                "capture,rotation,sensitivity,temporal,ablation_loss,latency"),
    "alerting": ("alert-quality sweeps over the cached scores (CPU)",
                 "resolution,window,window_draws,operator,budget,shift_gate,mondrian,"
                 "mondrian_covariate,panel_barrier,temporal_draws"),
    "analysis": ("frontier aggregation and every paper table", "frontier,tables"),
}


def run(command: list[str], dry_run: bool) -> int:
    print("$ " + " ".join(command), flush=True)
    if dry_run:
        return 0
    return subprocess.run(command, cwd=ROOT, check=False).returncode


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--stage", choices=sorted(STAGES), action="append",
                        help="repeatable; default is every stage in order")
    parser.add_argument("--datasets", default=None, help="comma separated; default is the paper's four")
    parser.add_argument("--seeds", default=None, help="comma separated; default is the paper's five")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    stages = args.stage or ["separability", "capture", "alerting", "analysis"]

    print(f"PACT reproduction: {', '.join(stages)}")
    for stage in stages:
        description, driver_stages = STAGES[stage]
        print(f"\n== {stage}: {description}")
        if stage == "separability":
            code = run([sys.executable, "-m", "experiments.open_set.separability"], args.dry_run)
        else:
            command = [sys.executable, "-m", "experiments.open_set.run_full_experiment",
                       "--stages", driver_stages]
            if args.datasets:
                command += ["--datasets", args.datasets]
            if args.seeds:
                command += ["--seeds", args.seeds]
            code = run(command, args.dry_run)
        if code != 0:
            print(f"stage {stage} exited with {code}; rerun the same command to continue")
            raise SystemExit(code)

    run([sys.executable, "-m", "experiments.open_set.environment"], args.dry_run)
    print("\nTables: results/paper/paper_tables.md   Environment: results/paper/environment.json")


if __name__ == "__main__":
    main()
