"""Full experiment driver: resumable, interruptible, and safe to kill.

The full matrix is roughly fifteen hours of training on one GPU, which is not a
session anyone wants to babysit.  So the unit of work here is one job with one
output file, and a job whose output already exists is skipped.  Killing the
process at any moment loses at most the job in flight; starting it again picks
up where it stopped.

``--max-minutes`` stops cleanly after a deadline rather than mid-job, so a run
can be boxed into whatever time is actually available.  ``--plan`` prints what
is left without doing anything, and ``--status`` summarises progress by stage.

Stages, in dependency order:

``capture``     train once per (dataset, seed, batch) and write scores.  This is
                where essentially all the time goes.
``frontier``    usability frontier and failure shape, seed-aggregated.
``resolution``  barrier, contamination floor, per-draw keepability.
``window``      stream-level aggregate across alert-window sizes and budgets.
``budget``      target label-budget allocation under shift.
``rotation``    Z2/Z3 panel captures on the same datasets, seed-first, after all
                Z1 analysis -- the held-out-family axis of the supporting table.

Everything after ``capture`` reads cached scores and takes minutes, so an
interrupted run that has finished its captures still yields every table.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "experiments" / "open_set" / "rq_matrix.yaml"
STATE = ROOT / "results" / "run_logs" / "full_run_state.json"

PANEL_BATCHES = {
    "A": "hedl,closr,efc,renoir_dml",
    "B": "ori,docpp,ais_nids,usfad",
}
SHORT = {
    "nf_cse_cic_ids2018_v3": "cse2018",
    "nf_ton_iot_v3": "toniot",
    "cicids2017": "cicids2017",
    "ciciomt2024": "ciciomt2024",
    "insdn": "insdn",
}
TRANSFER_CASES = ("unsw_to_ton", "ton_to_unsw", "loeo_unsw")


@dataclass
class Job:
    stage: str
    name: str
    output: Path
    command: list[str]
    # Rough cost order so a short session spends its time where value accrues
    # fastest rather than on the single most expensive capture.
    cost: int = 1
    needs: list[Path] = field(default_factory=list)
    # Aggregation jobs read whatever captures exist, so their output is stale as
    # soon as one more capture lands.  They cost seconds; always redo them.
    refresh: bool = False

    def produced_output(self) -> bool:
        """Did the job leave a usable artefact, regardless of scheduling policy?"""
        if not self.output.exists():
            return False
        if self.output.suffix == ".json":
            try:
                json.loads(self.output.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return False
        return True

    def done(self) -> bool:
        # Refresh jobs are never "done": they re-aggregate whatever captures
        # exist now, which is not what they aggregated last time.
        return False if self.refresh else self.produced_output()

    def ready(self) -> bool:
        return all(path.exists() for path in self.needs)


def _python(module: str, *args: str) -> list[str]:
    return [sys.executable, "-m", f"experiments.open_set.{module}", *args]


def _twins(rotation: dict, groups: list[list[str]]) -> frozenset[str]:
    """Known families a rotation must also hold out under ``groups``."""
    unknown = set(rotation["unknown_classes"])
    return frozenset(
        family for group in groups if unknown.intersection(group)
        for family in group if family in rotation["known_classes"]
    )


def build_jobs(matrix: dict, seeds: list[int], datasets: list[str]) -> list[Job]:
    scores = ROOT / "results" / "scores"
    jobs: list[Job] = []

    # -- capture ---------------------------------------------------------------
    # Cheapest datasets first: an interrupted session then still leaves whole
    # datasets finished rather than several half-finished ones.
    cost = {"cicids2017": 1, "insdn": 1, "ciciomt2024": 3, "nf_ton_iot_v3": 4,
            "nf_cse_cic_ids2018_v3": 5}
    for dataset in datasets:
        for seed in seeds:
            for batch, methods in PANEL_BATCHES.items():
                tag = f"{SHORT[dataset]}_panel{batch}_s{seed}"
                jobs.append(Job(
                    "capture", tag, scores / f"{tag}.npz",
                    _python("capture_scores", "--dataset", dataset, "--scenario", "Z1",
                            "--methods", methods, "--epochs", "30", "--seed", str(seed),
                            "--tuning-fraction", "0.2", "--no-tail-extension", "--tag", tag),
                    cost=cost.get(dataset, 3),
                ))
            # H-EDL only, tail-lifted: the RQ3 ablation arm.
            tag = f"{SHORT[dataset]}_tail_s{seed}"
            jobs.append(Job(
                "capture", tag, scores / f"{tag}.npz",
                _python("capture_scores", "--dataset", dataset, "--scenario", "Z1",
                        "--methods", "hedl", "--epochs", "30", "--seed", str(seed),
                        "--tuning-fraction", "0.2", "--tail-extension",
                        "--tail-confidence", "0.9", "--tag", tag),
                cost=cost.get(dataset, 3),
            ))

    # -- resolution and window, per dataset x seed -----------------------------
    for dataset in datasets:
        for seed in seeds:
            tag = f"{SHORT[dataset]}_panelA_s{seed}"
            src = scores / f"{tag}.npz"
            out = ROOT / "results" / "resolution" / f"full_{tag}.json"
            jobs.append(Job(
                "resolution", tag, out,
                _python("run_resolution", "--tag", tag, "--method", "hedl",
                        "--repeats", "400", "--calibration-draws", "8",
                        "--calibration-sizes", "1000,4000,12000,23025,41873",
                        "--prevalences", "0.25,0.1,0.05,0.01,0.001",
                        "--q-levels", "0.05,0.1,0.2",
                        "--pvalue-modes",
                        "distribution_free,training_conditional,e_bh,clairvoyant",
                        "--output", str(out.relative_to(ROOT))),
                needs=[src],
            ))
            for q in ("0.1", "0.2"):
                out = ROOT / "results" / "window" / f"full_{tag}_q{q.replace('.','')}.json"
                jobs.append(Job(
                    "window", f"{tag}_q{q}", out,
                    _python("run_window", "--tag", tag, "--method", "hedl",
                            "--stream-size", "40000", "--streams", "20",
                            "--calibration-draws", "5",
                            "--calibration-sizes", "4000,12000,23932",
                            "--window-sizes", "250,500,1000,2000,4000",
                            "--prevalences", "0.01,0.001", "--q", q,
                            "--procedures",
                            "distribution_free,training_conditional,storey_bh,"
                            "benjamini_yekutieli,e_bh",
                            "--output", str(out.relative_to(ROOT))),
                    needs=[src],
                ))

    # -- window_draws: the calibration-draw claim, at a size every dataset can
    # subsample.  The original window stage reads the *whole* calibration set at
    # its largest size, so its five "draws" share one calibration sample and
    # differ only in the stream; that measures stream noise, not the
    # draw-to-draw variation RQ2 is about.  Here every size is strictly below
    # the smallest calibration set in the panel (12,592), so each draw is a real
    # subsample, and 12,000 is the same n on all four datasets.  L = 5 splits
    # delta across the operator's per-window alert budget.
    for dataset in datasets:
        for seed in seeds:
            tag = f"{SHORT[dataset]}_panelA_s{seed}"
            src = scores / f"{tag}.npz"
            for q in ("0.1", "0.2"):
                # L = 100 is the configuration PACT ships: the Beta bound is
                # pointwise, so delta must be split across every threshold BH can
                # read, and the alert cap makes that number finite.  L = 1 and
                # L = 5 stay in the sweep as the uncovered configurations whose
                # exceedances motivate the correction.
                for levels, procedures in (
                    ("1", "distribution_free,training_conditional,storey_bh,"
                          "benjamini_yekutieli,e_bh"),
                    ("5", "training_conditional"),
                    ("100", "training_conditional"),
                ):
                    name = f"{tag}_q{q}_L{levels}"
                    out = (ROOT / "results" / "window_draws"
                           / f"full_{tag}_q{q.replace('.', '')}_L{levels}.json")
                    jobs.append(Job(
                        "window_draws", name, out,
                        _python("run_window", "--tag", tag, "--method", "hedl",
                                "--stream-size", "40000", "--streams", "20",
                                "--calibration-draws", "5",
                                "--calibration-sizes", "4000,8000,12000",
                                "--window-sizes", "1000,2000,4000",
                                "--prevalences", "0.01,0.001", "--q", q,
                                "--corrected-levels", levels,
                                "--procedures", procedures,
                                "--output", str(out.relative_to(ROOT))),
                        needs=[src],
                    ))

    # -- temporal (R1): calibrate on the past, alert on the future --------------
    # Only datasets whose manifest carries a T1 rotation (built by
    # experiments.open_set.build_temporal from FLOW_START_MILLISECONDS).
    for dataset in datasets:
        manifest_path = ROOT / "data" / "v7" / "manifests" / f"{dataset}_v7.yaml"
        if not manifest_path.exists():
            continue
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        # T2 is the per-family temporal split.  T1 (a single chronological cut)
        # is kept in the manifest as evidence that these testbeds stage their
        # attacks -- it leaves the late period with almost no known families --
        # but it is not scheduled.
        if "T2" not in manifest.get("rq1", {}).get("rotations", {}):
            continue
        for seed in seeds[:3]:
            for batch, methods in PANEL_BATCHES.items():
                tag = f"{SHORT[dataset]}_T2_panel{batch}_s{seed}"
                jobs.append(Job(
                    "temporal", tag, scores / f"{tag}.npz",
                    _python("capture_scores", "--dataset", dataset, "--scenario", "T2",
                            "--methods", methods, "--epochs", "30", "--seed", str(seed),
                            "--tuning-fraction", "0.2", "--no-tail-extension", "--tag", tag),
                    cost=cost.get(dataset, 3),
                ))
            tag = f"{SHORT[dataset]}_T2_panelA_s{seed}"
            src = scores / f"{tag}.npz"
            for q in ("0.1", "0.2"):
                for levels, procedures in (
                    ("1", "distribution_free,training_conditional,storey_bh,"
                          "benjamini_yekutieli,e_bh"),
                    ("5", "training_conditional"),
                    # The shipped configuration has to be shown failing here too,
                    # or the temporal result would compare the wrong arms.
                    ("100", "training_conditional"),
                ):
                    out = (ROOT / "results" / "window_draws"
                           / f"full_{tag}_q{q.replace('.', '')}_L{levels}.json")
                    jobs.append(Job(
                        "temporal_draws", f"{tag}_q{q}_L{levels}", out,
                        _python("run_window", "--tag", tag, "--method", "hedl",
                                "--stream-size", "40000", "--streams", "20",
                                "--calibration-draws", "5",
                                "--calibration-sizes", "4000,8000,12000",
                                "--window-sizes", "1000,2000,4000",
                                "--prevalences", "0.01,0.001", "--q", q,
                                "--corrected-levels", levels,
                                "--procedures", procedures,
                                "--output", str(out.relative_to(ROOT))),
                        needs=[src],
                    ))
            out = ROOT / "results" / "operator" / f"{tag}_q01.json"
            jobs.append(Job(
                "temporal_draws", f"{tag}_operator", out,
                _python("run_operator_baseline", "--tag", tag, "--method", "hedl",
                        "--calibration-sizes", "12000", "--calibration-draws", "5",
                        "--prevalences", "0.01,0.001", "--q", "0.1",
                        "--corrected-levels", "5",
                        "--output", str(out.relative_to(ROOT))),
                needs=[src],
            ))

    # -- Mondrian by covariate: the arm the RQ3 gate actually names --------------
    # Prop. 11 pays off only where the grouping variable concentrates attacks, so
    # the variable has to come from the traffic rather than from the detector.
    # Scheduled per dataset by what its feature schema carries.
    covariate_groupings = {
        "cicids2017": ("port_class",),
        "nf_cse_cic_ids2018_v3": ("port_class", "protocol"),
        "nf_ton_iot_v3": ("port_class", "protocol"),
        "ciciomt2024": ("protocol",),
    }
    for dataset in datasets:
        for grouping in covariate_groupings.get(dataset, ()):
            for seed in seeds:
                tag = f"{SHORT[dataset]}_panelA_s{seed}"
                src = scores / f"{tag}.npz"
                out = ROOT / "results" / "mondrian" / f"{tag}_{grouping}.json"
                jobs.append(Job(
                    "mondrian_covariate", f"{tag}_{grouping}", out,
                    _python("run_mondrian", "--tag", tag, "--methods", "hedl",
                            "--grouping", grouping, "--windows", "400",
                            "--output", str(out.relative_to(ROOT))),
                    cost=cost.get(dataset, 3), needs=[src],
                ))

    # -- loss ablation: does the evidential term earn its place in the name? ----
    # Run where the encoder demonstrably matters: on cicids2017 and cse2018 the
    # score saturates near 1.0 and no term can be told from another.
    for dataset in ("nf_ton_iot_v3", "ciciomt2024"):
        if dataset not in datasets:
            continue
        # All five seeds: this ablation decides whether a term stays in the
        # method's name, so it should not rest on three runs.
        for seed in seeds:
            tag = f"{SHORT[dataset]}_noevid_s{seed}"
            jobs.append(Job(
                "ablation_loss", tag, scores / f"{tag}.npz",
                _python("capture_scores", "--dataset", dataset, "--scenario", "Z1",
                        "--methods", "hedl", "--epochs", "30", "--seed", str(seed),
                        "--tuning-fraction", "0.2", "--no-tail-extension",
                        "--evidential-weight", "0", "--tag", tag),
                cost=cost.get(dataset, 3),
            ))

    # -- operator baseline (R2): the percentile threshold a SOC already runs ----
    for dataset in datasets:
        for seed in seeds:
            tag = f"{SHORT[dataset]}_panelA_s{seed}"
            src = scores / f"{tag}.npz"
            for q in ("0.1", "0.2"):
                out = (ROOT / "results" / "operator"
                       / f"{tag}_q{q.replace('.', '')}.json")
                jobs.append(Job(
                    "operator", f"{tag}_q{q}", out,
                    _python("run_operator_baseline", "--tag", tag, "--method", "hedl",
                            "--calibration-sizes", "12000", "--calibration-draws", "5",
                            "--prevalences", "0.01,0.001", "--stream-size", "40000",
                            "--streams", "20", "--window-size", "2000", "--q", q,
                            "--corrected-levels", "5",
                            "--output", str(out.relative_to(ROOT))),
                    needs=[src],
                ))

    # -- budget (RQ4) ----------------------------------------------------------
    for case in TRANSFER_CASES:
        for seed in seeds:
            out = ROOT / "results" / "budget" / f"{case}_seed{seed}.json"
            jobs.append(Job(
                "budget", f"{case}_s{seed}", out,
                _python("run_budget", "--case", case, "--seed", str(seed),
                        "--budgets", "60,120,300,1000,3000",
                        "--family-shots", "2,5,10,20",
                        "--policies", "anchors_only,aligned_tenth,aligned_full,selected",
                        "--output", str(out.relative_to(ROOT))),
                cost=2,
            ))

    # -- rotation (Z2, Z3 panel captures on the same datasets) -------------------
    # The supporting detector table is the eight-method panel on these datasets
    # rather than the ten-dataset LOAO sweep, so the held-out-family axis has to
    # come from the other rotations of the same datasets.  Ordered seed-first:
    # stopping at any point leaves every rotation covered for the seeds reached,
    # instead of some rotations with five seeds and others with none.
    for seed_index, seed in enumerate(seeds):
        for dataset in datasets:
            manifest = yaml.safe_load(
                (ROOT / "data" / "v7" / "manifests" / f"{dataset}_v7.yaml").read_text(
                    encoding="utf-8"
                )
            )
            for scenario in sorted(manifest["rq1"]["rotations"]):
                # Z rotations only.  The T rotations are the time-ordered splits
                # built by build_temporal; the temporal stage schedules T2 with
                # its own seed budget, and T1 is kept as evidence of staging
                # rather than run.
                if scenario == "Z1" or not scenario.startswith("Z"):
                    continue
                for batch, methods in PANEL_BATCHES.items():
                    tag = f"{SHORT[dataset]}_{scenario}_panel{batch}_s{seed}"
                    jobs.append(Job(
                        "rotation", tag, scores / f"{tag}.npz",
                        _python("capture_scores", "--dataset", dataset,
                                "--scenario", scenario, "--methods", methods,
                                "--epochs", "30", "--seed", str(seed),
                                "--tuning-fraction", "0.2", "--no-tail-extension",
                                "--tag", tag),
                        cost=seed_index * 10 + cost.get(dataset, 3),
                    ))

    # -- sensitivity (hold-out groups at the audit's other thresholds) -----------
    # Only rotations whose held-out set actually changes at that threshold get
    # a job; everywhere else the registered captures already are the answer.
    from .separability import SENSITIVITY_THRESHOLDS
    for seed_index, seed in enumerate(seeds):
        for dataset in datasets:
            audit_path = ROOT / "data" / "v7" / "separability" / f"{dataset}.json"
            if not audit_path.exists():
                continue
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
            manifest = yaml.safe_load(
                (ROOT / "data" / "v7" / "manifests" / f"{dataset}_v7.yaml").read_text(encoding="utf-8")
            )
            for scenario, rotation in sorted(manifest["rq1"]["rotations"].items()):
                registered = _twins(rotation, audit["groups"])
                for threshold in SENSITIVITY_THRESHOLDS:
                    if _twins(rotation, audit["sensitivity"][str(threshold)]) == registered:
                        continue
                    for batch, methods in PANEL_BATCHES.items():
                        tag = (f"{SHORT[dataset]}_{scenario}t{int(round(threshold * 100))}"
                               f"_panel{batch}_s{seed}")
                        jobs.append(Job(
                            "sensitivity", tag, scores / f"{tag}.npz",
                            _python("capture_scores", "--dataset", dataset,
                                    "--scenario", scenario, "--methods", methods,
                                    "--epochs", "30", "--seed", str(seed),
                                    "--tuning-fraction", "0.2", "--no-tail-extension",
                                    "--holdout-threshold", str(threshold), "--tag", tag),
                            cost=seed_index * 10 + cost.get(dataset, 3),
                        ))

    # -- latency (device path, floored vs tail-lifted scorer) --------------------
    for dataset in ("cicids2017", "nf_cse_cic_ids2018_v3"):
        if dataset not in datasets:
            continue
        out = ROOT / "results" / "latency" / f"pact_{SHORT[dataset]}_s13.json"
        jobs.append(Job(
            "latency", f"latency_{SHORT[dataset]}", out,
            _python("run_latency", "--dataset", dataset, "--seed", "13",
                    "--output", str(out.relative_to(ROOT))),
            cost=cost.get(dataset, 3),
        ))

    # -- CPU analyses over cached scores --------------------------------------
    panel_methods = {batch: methods.split(",") for batch, methods in PANEL_BATCHES.items()}
    for dataset in datasets:
        for seed in seeds:
            for batch, methods in panel_methods.items():
                tag = f"{SHORT[dataset]}_panel{batch}_s{seed}"
                src = scores / f"{tag}.npz"
                for method in methods:
                    out = ROOT / "results" / "resolution" / "panel" / f"full_{tag}_{method}.json"
                    jobs.append(Job(
                        "panel_barrier", f"{tag}_{method}", out,
                        _python("run_resolution", "--tag", tag, "--method", method,
                                "--repeats", "400", "--calibration-draws", "4",
                                "--calibration-sizes", "4000,12000,23025,41873",
                                "--prevalences", "0.01,0.001", "--q-levels", "0.1",
                                "--pvalue-modes",
                                "distribution_free,training_conditional,e_bh,clairvoyant",
                                "--output", str(out.relative_to(ROOT))),
                        cost=cost.get(dataset, 3), needs=[src],
                    ))
            tag = f"{SHORT[dataset]}_panelA_s{seed}"
            src = scores / f"{tag}.npz"
            out = ROOT / "results" / "shift_gate" / f"{tag}.json"
            jobs.append(Job(
                "shift_gate", tag, out,
                _python("run_shift_gate", "--tag", tag, "--methods", "hedl,closr",
                        "--output", str(out.relative_to(ROOT))),
                cost=cost.get(dataset, 3), needs=[src],
            ))
            out = ROOT / "results" / "mondrian" / f"{tag}.json"
            jobs.append(Job(
                "mondrian", tag, out,
                _python("run_mondrian", "--tag", tag, "--methods", "hedl",
                        "--output", str(out.relative_to(ROOT))),
                cost=cost.get(dataset, 3), needs=[src],
            ))

    # -- frontier (one pass over everything that exists, every rotation) --------
    panel_tags = [
        j.name for j in jobs if j.stage in ("capture", "rotation") and "_panel" in j.name
    ]
    jobs.append(Job(
        "frontier", "panel_frontier",
        ROOT / "results" / "frontier" / "full_panel_frontier.json",
        _python("run_frontier", "--tags", ",".join(panel_tags),
                "--methods", "hedl,closr,efc,renoir_dml,ori,docpp,ais_nids,usfad",
                "--prevalences", "0.25,0.1,0.05,0.02,0.01,0.005,0.001",
                "--target-prevalence", "0.01", "--repeats", "300",
                "--output", "results/frontier/full_panel_frontier.json"),
        refresh=True,
    ))

    # -- tables (paper tables from whatever exists; seconds) ---------------------
    jobs.append(Job(
        "tables", "paper_tables", ROOT / "results" / "paper" / "paper_tables.json",
        _python("paper_tables", "--output-dir", "results/paper"),
        refresh=True,
    ))

    return jobs


def load_state(path: Path = STATE) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return {"runs": [], "jobs": {}}


def save_state(state: dict, path: Path = STATE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    temporary.replace(path)


STAGE_ORDER = {
    "capture": 0, "resolution": 2, "window": 3, "window_draws": 3, "operator": 3, "mondrian_covariate": 3, "budget": 4, "temporal": 5, "temporal_draws": 6, "ablation_loss": 5, "rotation": 5,
    "sensitivity": 6, "latency": 7, "panel_barrier": 8, "shift_gate": 8, "mondrian": 8,
    "frontier": 9, "tables": 10,
}
ALL_STAGES = ",".join(STAGE_ORDER)


def summarise(jobs: list[Job]) -> dict[str, tuple[int, int]]:
    by_stage: dict[str, list[Job]] = {}
    for job in jobs:
        by_stage.setdefault(job.stage, []).append(job)
    return {
        stage: (sum(1 for job in items if job.produced_output()), len(items))
        for stage, items in by_stage.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", default="13,37,73,101,137")
    parser.add_argument("--datasets", default=None,
                        help="default: the deployment_operational list in rq_matrix.yaml")
    parser.add_argument("--stages", default=ALL_STAGES)
    parser.add_argument("--state-file", type=Path, default=STATE,
                        help="separate state file lets a CPU-only driver run alongside")
    parser.add_argument("--max-minutes", type=float, default=None,
                        help="stop cleanly after this long; never interrupts a running job")
    parser.add_argument("--plan", action="store_true", help="list outstanding work and exit")
    parser.add_argument("--status", action="store_true", help="progress summary and exit")
    parser.add_argument("--job-timeout-minutes", type=float, default=180.0)
    args = parser.parse_args()

    matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    seeds = [int(v) for v in args.seeds.split(",")]
    datasets = (
        [v.strip() for v in args.datasets.split(",")]
        if args.datasets
        else matrix["datasets"]["deployment_operational"]
    )
    stages = [v.strip() for v in args.stages.split(",")]
    jobs = [job for job in build_jobs(matrix, seeds, datasets) if job.stage in stages]

    if args.status or args.plan:
        totals = summarise(jobs)
        print(f"{'stage':>12} {'done':>6} {'total':>6}")
        for stage in STAGE_ORDER:
            if stage in totals:
                done, total = totals[stage]
                print(f"{stage:>13} {done:6d} {total:6d}")
        outstanding = [job for job in jobs if not job.done()]
        print(f"\n{len(outstanding)} job(s) outstanding of {len(jobs)}")
        if args.plan:
            for job in outstanding[:40]:
                print(f"  [{job.stage}] {job.name}")
            if len(outstanding) > 40:
                print(f"  ... and {len(outstanding) - 40} more")
        return

    state = load_state(args.state_file)
    started = time.perf_counter()
    deadline = args.max_minutes * 60 if args.max_minutes else None
    run_record = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds,
        "datasets": datasets,
        "completed": [],
        "failed": [],
    }

    # Captures first (everything depends on them), cheapest dataset first.
    # Aggregation last, so it sees every capture the session managed to finish.
    # Passes repeat while they make progress: a job whose inputs appear during a
    # pass, or a stage added to the code, is picked up without a restart of the
    # scheduled task.
    attempted: set[str] = set()
    try:
        while True:
            jobs = [job for job in build_jobs(matrix, seeds, datasets) if job.stage in stages]
            pending = sorted(
                (job for job in jobs
                 if not job.done() and f"{job.stage}/{job.name}" not in attempted),
                key=lambda job: (STAGE_ORDER.get(job.stage, 99), job.cost, job.name),
            )
            runnable = [job for job in pending if job.ready()]
            if not runnable:
                break
            print(f"{len(runnable)} job(s) to run"
                  + (f", stopping after {args.max_minutes:g} minutes" if deadline else ""),
                  flush=True)
            progressed = False
            for index, job in enumerate(runnable, start=1):
                if deadline and time.perf_counter() - started > deadline:
                    print(f"\ndeadline reached; {len(runnable) - index + 1} job(s) left for next time")
                    raise StopIteration
                if job.done() or not job.ready():
                    continue
                attempted.add(f"{job.stage}/{job.name}")
                job.output.parent.mkdir(parents=True, exist_ok=True)
                log = job.output.with_suffix(".log")
                print(f"[{index}/{len(runnable)}] {job.stage}/{job.name} ...", flush=True)
                job_started = time.perf_counter()
                with log.open("w", encoding="utf-8") as handle:
                    try:
                        result = subprocess.run(
                            job.command, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT,
                            timeout=args.job_timeout_minutes * 60, check=False,
                        )
                        returncode = result.returncode
                    except subprocess.TimeoutExpired:
                        returncode = -9
                elapsed = time.perf_counter() - job_started
                ok = returncode == 0 and job.produced_output()
                progressed = progressed or ok
                entry = {"stage": job.stage, "name": job.name, "seconds": round(elapsed, 1),
                         "returncode": returncode}
                (run_record["completed"] if ok else run_record["failed"]).append(entry)
                state["jobs"][f"{job.stage}/{job.name}"] = {
                    **entry, "finished_at": datetime.now(timezone.utc).isoformat(), "ok": ok
                }
                save_state({**state, "runs": state["runs"] + [run_record]}, args.state_file)
                print(f"      {'ok' if ok else 'FAILED'} in {elapsed / 60:.1f} min"
                      + ("" if ok else f" (see {log})"), flush=True)
            if not progressed:
                break
    except StopIteration:
        pass
    except KeyboardInterrupt:
        print("\ninterrupted; progress saved, rerun the same command to continue")

    totals = summarise(jobs)
    print("\nprogress:")
    for stage in STAGE_ORDER:
        if stage in totals:
            done, total = totals[stage]
            print(f"  {stage:>13}: {done}/{total}")
    save_state({**state, "runs": state["runs"] + [run_record]}, args.state_file)
    print(f"state: {STATE}")


if __name__ == "__main__":
    main()
