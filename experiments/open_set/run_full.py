from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import yaml

from .data import load_rotation

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MATRIX_PATH = HERE / "rq_matrix.yaml"


@dataclass(frozen=True)
class Job:
    command: tuple[str, ...]
    output: Path


def scenarios(dataset: str) -> list[str]:
    # "rq1" here is a directory name inside the frozen v7 partition artefact,
    # not this runner's protocol identifier.  It must not be renamed with them.
    #
    # Z rotations only.  The T rotations are time-ordered splits built by
    # experiments.open_set.build_temporal for the deployment protocol; they hold
    # out the same family as Z1 and would double-count it in the leave-one-attack
    # -out table, which is why the locked job count excludes them.
    root = ROOT / "data" / "v7" / "partitions" / dataset / "rq1"
    return sorted(path.name for path in root.iterdir()
                  if path.is_dir() and path.name.startswith("Z"))


def openness_cases(dataset: str) -> list[tuple[str, list[str]]]:
    data = load_rotation(dataset, "Z1")
    candidates = sorted(family for family in data.known_families if family != "benign")
    total_attacks = len(candidates) + len(data.unknown_families)
    targets = {
        "O1": 1,
        "O2": 2,
        "O3": 3,
        "O25": max(1, math.ceil(total_attacks * 0.25)),
        "O50": max(1, math.ceil(total_attacks * 0.50)),
    }
    cases: list[tuple[str, list[str]]] = []
    seen: set[tuple[str, ...]] = set()
    for name, target_count in targets.items():
        additional_count = max(0, target_count - len(data.unknown_families))
        additional = tuple(candidates[:additional_count])
        if additional in seen:
            continue
        seen.add(additional)
        cases.append((name, list(additional)))
    return cases


def method_list(matrix: dict, protocol: str, track: str, include_auxiliary: bool) -> list[str]:
    config = matrix["protocols"][protocol]
    if track == "ours":
        return [config["proposed"]]
    methods = list(config["executable_baselines"])
    if include_auxiliary:
        methods.extend(matrix["auxiliary_sanity_methods"])
    methods = list(dict.fromkeys(methods))
    unavailable = [
        method
        for method in methods
        if matrix["methods"][method]["status"] not in {"ready", "adapter_ready", "paper_reimplementation_ready"}
    ]
    if unavailable:
        raise RuntimeError(f"Configured baseline adapters are not executable: {unavailable}")
    return methods


def command_for(
    protocol_group: str,
    protocol: str,
    dataset: str,
    methods: list[str],
    seed: int,
    epochs: int,
    output: Path,
    scenario: str = "Z1",
    target_dataset: str | None = None,
    source_datasets: list[str] | None = None,
    additional_unknown: list[str] | None = None,
    max_rows: int | None = None,
    batch_size: int = 256,
    profile: str | None = None,
) -> Job:
    command = [
        sys.executable,
        "-m",
        "experiments.open_set.run",
        "--protocol-group",
        protocol_group,
        "--protocol",
        protocol,
        "--dataset",
        dataset,
        "--scenario",
        scenario,
        "--methods",
        ",".join(methods),
        "--seed",
        str(seed),
        "--epochs",
        str(epochs),
        "--batch-size",
        str(batch_size),
        "--output",
        str(output),
    ]
    if target_dataset:
        command.extend(["--target-dataset", target_dataset])
    if source_datasets:
        command.extend(["--source-datasets", ",".join(source_datasets)])
    if additional_unknown:
        command.extend(["--additional-unknown", ",".join(additional_unknown)])
    if max_rows:
        command.extend(["--max-rows", str(max_rows)])
    if profile:
        command.extend(["--profile", profile])
    return Job(tuple(command), output)

def fdr_command_for(
    dataset: str,
    scenario: str,
    methods: list[str],
    seed: int,
    epochs: int,
    output: Path,
    alert_batch_size: int,
    repeats: int,
    q_levels: list[float],
    procedures: list[str],
    tuning_fraction: float,
    minimum_group_size: int,
    validity_audit_alpha: float,
    max_rows: int | None = None,
    inference_batch_size: int = 256,
    profile: str | None = None,
) -> Job:
    command = [
        sys.executable,
        "-m",
        "experiments.open_set.run_fdr",
        "--dataset",
        dataset,
        "--scenario",
        scenario,
        "--methods",
        ",".join(methods),
        "--seed",
        str(seed),
        "--epochs",
        str(epochs),
        "--inference-batch-size",
        str(inference_batch_size),
        "--alert-batch-size",
        str(alert_batch_size),
        "--repeats",
        str(repeats),
        "--q-levels",
        ",".join(map(str, q_levels)),
        "--procedures",
        ",".join(procedures),
        "--tuning-fraction",
        str(tuning_fraction),
        "--minimum-group-size",
        str(minimum_group_size),
        "--validity-audit-alpha",
        str(validity_audit_alpha),
        "--output",
        str(output),
    ]
    if max_rows:
        command.extend(["--max-rows", str(max_rows)])
    if profile:
        command.extend(["--profile", profile])
    return Job(tuple(command), output)


def build_jobs(
    matrix: dict,
    protocol: str,
    track: str,
    methods: list[str],
    epochs: int,
    smoke: bool,
    requested_protocol: str | None,
    smoke_epochs: int = 1,
    smoke_max_rows: int = 500,
    profile: str | None = None,
) -> list[Job]:
    seeds = [matrix["seeds"][0]] if smoke else matrix["seeds"]
    run_epochs = smoke_epochs if smoke else epochs
    max_rows = smoke_max_rows if smoke else None
    training_key = "hedl" if track == "ours" else "external_baselines"
    training = matrix["training"][training_key]
    batch_size = training["smoke_batch_size"] if smoke else training["batch_size"]
    if smoke and smoke_max_rows > 2000:
        batch_size = training["batch_size"]
    base = ROOT / "results" / "protocols" / protocol / track
    jobs: list[Job] = []

    if protocol == "loao":
        datasets = matrix["datasets"][matrix["protocols"][protocol]["datasets"]]
        if smoke:
            datasets = datasets[:1]
        for dataset in datasets:
            selected_scenarios = scenarios(dataset)
            if smoke:
                selected_scenarios = selected_scenarios[:1]
            for scenario in selected_scenarios:
                for seed in seeds:
                    output = base / "loao" / dataset / scenario / f"seed_{seed}.json"
                    jobs.append(
                        command_for(
                            protocol,
                            "loao",
                            dataset,
                            methods,
                            seed,
                            run_epochs,
                            output,
                            scenario,
                            max_rows=max_rows,
                            batch_size=batch_size,
                            profile=profile if track == "ours" else None,
                        )
                    )
        return jobs

    if protocol == "shift":
        config = matrix["protocols"][protocol]["arms"]
        protocols = [requested_protocol] if requested_protocol else ["difficulty", "cross_domain"]
        if "difficulty" in protocols:
            datasets = matrix["datasets"][config["difficulty"]["datasets"]]
            if smoke:
                datasets = datasets[:1]
            for dataset in datasets:
                cases = openness_cases(dataset)
                if smoke:
                    # The lowest openness level usually adds no family beyond the
                    # base rotation, which makes it the very same experiment as the
                    # near-distance case below.  Smoke runs keep one case, so pick
                    # the first one that genuinely raises openness.
                    raising = [case for case in cases if case[1]]
                    cases = raising[:1] or cases[:1]
                for openness, additional in cases:
                    for seed in seeds:
                        output = base / "difficulty" / "openness" / dataset / openness / f"seed_{seed}.json"
                        jobs.append(
                            command_for(
                                protocol,
                                "difficulty",
                                dataset,
                                methods,
                                seed,
                                run_epochs,
                                output,
                                "Z1",
                                additional_unknown=additional,
                                max_rows=max_rows,
                                batch_size=batch_size,
                            profile=profile if track == "ours" else None,
                            )
                        )
            near_far_groups = (("near", config["difficulty"]["near_cases"]), ("far", config["difficulty"]["far_cases"]))
            for distance_name, cases in near_far_groups:
                selected_cases = cases[:1] if smoke else cases
                for dataset, scenario in selected_cases:
                    for seed in seeds:
                        output = base / "difficulty" / "near_far" / distance_name / dataset / scenario / f"seed_{seed}.json"
                        jobs.append(
                            command_for(
                                protocol,
                                "difficulty",
                                dataset,
                                methods,
                                seed,
                                run_epochs,
                                output,
                                scenario,
                                max_rows=max_rows,
                                batch_size=batch_size,
                            profile=profile if track == "ours" else None,
                            )
                        )
        if "cross_domain" in protocols:
            datasets = matrix["datasets"][config["cross_domain"]["datasets"]]
            pairs = [(source, target) for source in datasets for target in datasets if source != target]
            if smoke:
                pairs = pairs[:1]
            for source, target in pairs:
                for seed in seeds:
                    output = base / "cross_domain" / "source_target" / f"{source}_to_{target}" / f"seed_{seed}.json"
                    jobs.append(
                        command_for(
                            protocol,
                            "cross_domain",
                            source,
                            methods,
                            seed,
                            run_epochs,
                            output,
                            target_dataset=target,
                            max_rows=max_rows,
                            batch_size=batch_size,
                            profile=profile if track == "ours" else None,
                        )
                    )
            targets = datasets[:1] if smoke else datasets
            for target in targets:
                sources = [dataset for dataset in datasets if dataset != target]
                for seed in seeds:
                    output = base / "cross_domain" / "leave_one_environment_out" / target / f"seed_{seed}.json"
                    jobs.append(
                        command_for(
                            protocol,
                            "cross_domain",
                            sources[0],
                            methods,
                            seed,
                            run_epochs,
                            output,
                            target_dataset=target,
                            source_datasets=sources,
                            max_rows=max_rows,
                            batch_size=batch_size,
                            profile=profile if track == "ours" else None,
                        )
                    )
        return jobs

    datasets = matrix["datasets"][matrix["protocols"][protocol]["datasets"]]
    if requested_protocol == "conformal_fdr_audit":
        fdr_config = matrix["protocols"][protocol]["conformal_fdr_audit"]
        cases = fdr_config["cases"][:1] if smoke else fdr_config["cases"]
        alert_batch_size = (
            fdr_config["smoke_alert_batch_size"] if smoke else fdr_config["alert_batch_size"]
        )
        repeats = fdr_config["smoke_repeats"] if smoke else fdr_config["repeats"]
        fdr_base = ROOT / "results" / "fdr" / "official" / track
        for dataset, scenario in cases:
            for seed in seeds:
                output = fdr_base / dataset / scenario / f"seed_{seed}.json"
                jobs.append(
                    fdr_command_for(
                        dataset,
                        scenario,
                        methods,
                        seed,
                        run_epochs,
                        output,
                        alert_batch_size,
                        repeats,
                        fdr_config["q_levels"],
                        fdr_config["procedures"],
                        fdr_config["tuning_fraction"],
                        fdr_config["minimum_group_size"],
                        fdr_config["validity_audit_alpha"],
                        max_rows=max_rows,
                        inference_batch_size=batch_size,
                        profile=profile if track == "ours" else None,
                    )
                )
        return jobs
    if smoke:
        datasets = datasets[:1]
    for dataset in datasets:
        selected_scenarios = scenarios(dataset)
        if smoke:
            selected_scenarios = selected_scenarios[:1]
        for scenario in selected_scenarios:
            for seed in seeds:
                output = base / "prevalence" / dataset / scenario / f"seed_{seed}.json"
                jobs.append(
                    command_for(
                        protocol,
                        "prevalence",
                        dataset,
                        methods,
                        seed,
                        run_epochs,
                        output,
                        scenario,
                        max_rows=max_rows,
                        batch_size=batch_size,
                            profile=profile if track == "ours" else None,
                    )
                )
    return jobs


def result_is_complete(path: Path, expected_methods: list[str]) -> bool:
    if not path.exists():
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    methods = payload.get("methods")
    return isinstance(methods, dict) and set(methods) == set(expected_methods)


def write_manifest(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    temporary.replace(path)


def main(default_protocol: str | None = None, default_track: str | None = None) -> None:
    matrix = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))
    parser = argparse.ArgumentParser()
    # Protocols are named for what they do.  The paper's research questions are
    # a separate, higher-level structure (see reports/RQ_DESIGN_2026-09-12.md);
    # one protocol feeds several questions and numbering them invited exactly
    # the confusion this rename removes.
    parser.add_argument(
        "--protocol-group",
        dest="protocol",
        choices=["loao", "shift", "prevalence"],
        default=default_protocol,
        required=default_protocol is None,
    )
    parser.add_argument("--track", choices=["ours", "baselines"], default=default_track, required=default_track is None)
    parser.add_argument(
        "--protocol",
        dest="sub_protocol",
        choices=["difficulty", "cross_domain", "prevalence", "conformal_fdr_audit"],
    )
    parser.add_argument("--epochs", type=int)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument(
        "--profile",
        help="H-EDL backbone profile forwarded to the proposed-method jobs (defaults to run.py's default).",
    )
    parser.add_argument(
        "--smoke-epochs",
        type=int,
        default=1,
        help="Training epochs for --smoke jobs. The default of 1 only checks that the pipeline runs; "
        "raise it when the reduced condition set should also compare the algorithms.",
    )
    parser.add_argument(
        "--smoke-max-rows",
        type=int,
        default=500,
        help="Row cap per split for --smoke jobs.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--include-auxiliary", action="store_true")
    parser.add_argument("--resume", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--timeout-minutes", type=float, default=720.0)
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--limit-jobs", type=int)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    if args.epochs is None:
        training_key = "hedl" if args.track == "ours" else "external_baselines"
        args.epochs = int(matrix["training"][training_key]["epochs"])
    methods = method_list(matrix, args.protocol, args.track, args.include_auxiliary)
    jobs = build_jobs(
        matrix,
        args.protocol,
        args.track,
        methods,
        args.epochs,
        args.smoke,
        args.sub_protocol,
        smoke_epochs=args.smoke_epochs,
        smoke_max_rows=args.smoke_max_rows,
        profile=args.profile,
    )
    if args.limit_jobs is not None:
        jobs = jobs[: args.limit_jobs]
    for job in jobs:
        print(" ".join(job.command))
    if args.dry_run:
        print(f"jobs={len(jobs)} methods={','.join(methods)}")
        return

    started_at = datetime.now(timezone.utc).isoformat()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    manifest_path = args.manifest or (
        ROOT / "results" / "protocols" / "_runs" / f"{timestamp}_{args.protocol}_{args.track}.json"
    )
    manifest: dict = {
        "protocol_group": args.protocol,
        "track": args.track,
        "methods": methods,
        "epochs": args.epochs,
        "smoke": args.smoke,
        "started_at": started_at,
        "jobs_total": len(jobs),
        "jobs": [],
    }
    failures = 0
    for index, job in enumerate(jobs, start=1):
        record = {
            "index": index,
            "output": str(job.output),
            "command": list(job.command),
        }
        if args.resume and result_is_complete(job.output, methods):
            record["status"] = "skipped_complete"
            manifest["jobs"].append(record)
            write_manifest(manifest_path, manifest)
            print(f"[{index}/{len(jobs)}] skip {job.output}")
            continue
        print(f"[{index}/{len(jobs)}] run {job.output}")
        started = time.perf_counter()
        try:
            completed = subprocess.run(
                job.command,
                cwd=ROOT,
                check=True,
                timeout=args.timeout_minutes * 60.0,
                capture_output=True,
                text=True,
            )
            record.update(
                status="passed",
                elapsed_seconds=time.perf_counter() - started,
                stdout_tail=completed.stdout[-4000:],
                stderr_tail=completed.stderr[-4000:],
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
            failures += 1
            record.update(
                status="failed",
                elapsed_seconds=time.perf_counter() - started,
                error=str(error),
                stdout_tail=(error.stdout or "")[-4000:] if isinstance(error.stdout, str) else "",
                stderr_tail=(error.stderr or "")[-4000:] if isinstance(error.stderr, str) else "",
            )
        manifest["jobs"].append(record)
        manifest["jobs_passed"] = sum(item["status"] == "passed" for item in manifest["jobs"])
        manifest["jobs_skipped"] = sum(item["status"] == "skipped_complete" for item in manifest["jobs"])
        manifest["jobs_failed"] = failures
        write_manifest(manifest_path, manifest)
        if failures and args.fail_fast:
            break
    manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
    manifest["status"] = "failed" if failures else "complete"
    write_manifest(manifest_path, manifest)
    print(f"manifest={manifest_path}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
