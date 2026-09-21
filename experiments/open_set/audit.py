from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from .data import NETFLOW_FILES, V7_ROOT, load_rotation


ROOT = Path(__file__).resolve().parents[2]


def audit() -> list[dict[str, str]]:
    matrix = yaml.safe_load((Path(__file__).with_name("rq_matrix.yaml")).read_text(encoding="utf-8"))
    rows: list[dict[str, str]] = []
    for rq_name, rq in matrix["rqs"].items():
        if rq_name == "rq2":
            difficulty = matrix["datasets"][rq["protocols"]["difficulty"]["datasets"]]
            cross_domain = matrix["datasets"][rq["protocols"]["cross_domain"]["datasets"]]
            datasets = list(dict.fromkeys([*difficulty, *cross_domain]))
        else:
            datasets = matrix["datasets"][rq["datasets"]]
        data_status = "ready"
        details: list[str] = []
        if rq_name in {"rq1", "rq2", "rq3"}:
            for dataset in datasets:
                partition_root = V7_ROOT / "partitions" / dataset / "rq1"
                scenarios = sorted(path.name for path in partition_root.iterdir() if path.is_dir())
                if not scenarios:
                    data_status = "missing"
                    details.append(f"{dataset}:no_scenarios")
                    continue
                try:
                    load_rotation(dataset, scenarios[0])
                except Exception as error:
                    data_status = "invalid"
                    details.append(f"{dataset}:{error}")
        if rq_name == "rq2":
            cross_datasets = matrix["datasets"][rq["protocols"]["cross_domain"]["datasets"]]
            missing = [dataset for dataset in cross_datasets if not NETFLOW_FILES[dataset].exists()]
            if missing:
                data_status = "missing_raw"
                details.extend(missing)
        primary_states = [matrix["methods"][method]["status"] for method in rq["primary_sota"]]
        proposed_state = matrix["methods"][rq["proposed"]]["status"]
        controls = rq.get("internal_controls", [])
        control_states = [matrix["methods"][method]["status"] for method in controls]
        rows.append(
            {
                "rq": rq_name,
                "datasets": str(len(datasets)),
                "data": data_status,
                "ready_primary": str(
                    sum(state in {"ready", "adapter_ready", "paper_reimplementation_ready"} for state in primary_states)
                ),
                "total_primary": str(len(primary_states)),
                "proposed": "ready"
                if proposed_state in {"ready", "adapter_ready", "paper_reimplementation_ready"}
                else proposed_state,
                "ready_controls": str(
                    sum(state in {"ready", "adapter_ready", "paper_reimplementation_ready"} for state in control_states)
                ),
                "total_controls": str(len(control_states)),
                "details": ";".join(details),
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    rows = audit()
    print("RQ  datasets  data       primary  proposed  controls")
    for row in rows:
        controls = f"{row['ready_controls']}/{row['total_controls']}" if row["total_controls"] != "0" else "-"
        print(
            f"{row['rq']:<3} {row['datasets']:<9} {row['data']:<10} "
            f"{row['ready_primary']}/{row['total_primary']:<6} {row['proposed']:<9} {controls}"
        )
        if row["details"]:
            print(f"    {row['details']}")


if __name__ == "__main__":
    main()
