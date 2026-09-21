from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.stats import rankdata, t, wilcoxon

from .run_full import build_jobs, method_list, result_is_complete

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MATRIX_PATH = HERE / "rq_matrix.yaml"
LOWER_IS_BETTER = {"fpr95", "far", "frr", "latency_ms_per_flow", "parameters"}


def markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return ""
    columns = [str(column) for column in frame.columns]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in frame.itertuples(index=False, name=None):
        values = [str(value).replace("|", "\\|") for value in row]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def scalar_metrics(metrics: dict) -> dict[str, float]:
    return {
        name: float(value)
        for name, value in metrics.items()
        if isinstance(value, (int, float)) and np.isfinite(value) and not name.startswith("adapter_")
    }


def condition_key(path: Path, track_root: Path) -> str:
    relative = path.relative_to(track_root)
    return str(relative.with_suffix("")).replace("\\", "/")


def load_rows(results_root: Path, matrix: dict, selected_rq: str | None) -> tuple[pd.DataFrame, list[str]]:
    rows: list[dict] = []
    warnings: list[str] = []
    rq_names = [selected_rq] if selected_rq else list(matrix["protocols"])
    for rq in rq_names:
        for track in ("ours", "baselines"):
            track_root = results_root / rq / track
            if not track_root.exists():
                warnings.append(f"missing result tree: {track_root}")
                continue
            expected = (
                {matrix["protocols"][rq]["proposed"]}
                if track == "ours"
                else set(matrix["protocols"][rq]["executable_baselines"])
            )
            for path in track_root.rglob("seed_*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as error:
                    warnings.append(f"invalid json {path}: {error}")
                    continue
                methods = payload.get("methods", {})
                missing = expected.difference(methods)
                if missing:
                    warnings.append(f"incomplete {path}: missing {sorted(missing)}")
                condition = condition_key(path, track_root)
                for method, metrics in methods.items():
                    base = {
                        "protocol_group": rq,
                        "track": track,
                        "condition": condition,
                        "protocol": payload.get("protocol", ""),
                        "dataset": payload.get("dataset", ""),
                        "scenario": payload.get("scenario", ""),
                        "seed": int(payload.get("seed", -1)),
                        "method": method,
                    }
                    for metric, value in scalar_metrics(metrics).items():
                        rows.append({**base, "metric": metric, "value": value})
                    prevalence = metrics.get("prevalence", {})
                    if isinstance(prevalence, dict):
                        for rate, rate_metrics in prevalence.items():
                            for metric, value in scalar_metrics(rate_metrics).items():
                                rows.append(
                                    {
                                        **base,
                                        "condition": f"{condition}/prevalence_{rate}",
                                        "metric": metric,
                                        "value": value,
                                    }
                                )
    return pd.DataFrame(rows), warnings


def full_completeness_warnings(matrix: dict, selected_rq: str | None) -> list[str]:
    warnings: list[str] = []
    rq_names = [selected_rq] if selected_rq else list(matrix["protocols"])
    for rq in rq_names:
        for track in ("ours", "baselines"):
            methods = method_list(matrix, rq, track, False)
            training_key = "hedl" if track == "ours" else "external_baselines"
            epochs = int(matrix["training"][training_key]["epochs"])
            jobs = build_jobs(matrix, rq, track, methods, epochs, False, None)
            missing = [job.output for job in jobs if not result_is_complete(job.output, methods)]
            if missing:
                warnings.append(f"{rq}/{track}: {len(missing)}/{len(jobs)} full jobs missing or incomplete")
    return warnings


def summarize(rows: pd.DataFrame) -> pd.DataFrame:
    output: list[dict] = []
    for keys, group in rows.groupby(["protocol_group", "track", "method", "metric"], sort=True):
        values = group["value"].to_numpy(dtype=float)
        count = len(values)
        mean = float(values.mean())
        standard_deviation = float(values.std(ddof=1)) if count > 1 else 0.0
        half_width = float(t.ppf(0.975, count - 1) * standard_deviation / math.sqrt(count)) if count > 1 else 0.0
        output.append(
            {
                "protocol_group": keys[0],
                "track": keys[1],
                "method": keys[2],
                "metric": keys[3],
                "n": count,
                "mean": mean,
                "std": standard_deviation,
                "ci95_low": mean - half_width,
                "ci95_high": mean + half_width,
            }
        )
    return pd.DataFrame(output)


def paired_comparisons(rows: pd.DataFrame, matrix: dict) -> pd.DataFrame:
    output: list[dict] = []
    for rq, config in matrix["protocols"].items():
        proposed = config["proposed"]
        rq_rows = rows[rows["protocol_group"] == rq]
        for metric in sorted(set(rq_rows["metric"])):
            proposed_rows = rq_rows[(rq_rows["method"] == proposed) & (rq_rows["metric"] == metric)][
                ["condition", "seed", "value"]
            ].rename(columns={"value": "proposed_value"})
            for baseline in config["executable_baselines"]:
                baseline_rows = rq_rows[(rq_rows["method"] == baseline) & (rq_rows["metric"] == metric)][
                    ["condition", "seed", "value"]
                ].rename(columns={"value": "baseline_value"})
                paired = proposed_rows.merge(baseline_rows, on=["condition", "seed"], how="inner")
                if paired.empty:
                    continue
                direction = -1.0 if metric in LOWER_IS_BETTER else 1.0
                improvements = direction * (paired["proposed_value"] - paired["baseline_value"])
                wins = int((improvements > 1e-12).sum())
                ties = int((np.abs(improvements) <= 1e-12).sum())
                losses = int((improvements < -1e-12).sum())
                if len(paired) > 1 and np.any(np.abs(improvements) > 1e-12):
                    try:
                        p_value = float(wilcoxon(improvements, alternative="greater").pvalue)
                    except ValueError:
                        p_value = 1.0
                    effect_size = float(improvements.mean() / improvements.std(ddof=1)) if improvements.std(ddof=1) else 0.0
                else:
                    p_value = 1.0
                    effect_size = 0.0
                output.append(
                    {
                        "protocol_group": rq,
                        "metric": metric,
                        "proposed": proposed,
                        "baseline": baseline,
                        "n_pairs": len(paired),
                        "mean_oriented_improvement": float(improvements.mean()),
                        "wins": wins,
                        "ties": ties,
                        "losses": losses,
                        "wilcoxon_one_sided_p": p_value,
                        "cohens_dz": effect_size,
                    }
                )
    result = pd.DataFrame(output)
    if result.empty:
        return result
    result["holm_adjusted_p"] = 1.0
    for _, indices in result.groupby(["protocol_group", "metric"]).groups.items():
        ordered = result.loc[indices, "wilcoxon_one_sided_p"].sort_values()
        adjusted: dict[int, float] = {}
        running = 0.0
        count = len(ordered)
        for rank, (index, p_value) in enumerate(ordered.items()):
            running = max(running, min(1.0, float(p_value) * (count - rank)))
            adjusted[index] = running
        for index, value in adjusted.items():
            result.loc[index, "holm_adjusted_p"] = value
    return result


def average_ranks(rows: pd.DataFrame, matrix: dict) -> pd.DataFrame:
    output: list[dict] = []
    for rq, config in matrix["protocols"].items():
        methods = [config["proposed"], *config["executable_baselines"]]
        rq_rows = rows[(rows["protocol_group"] == rq) & (rows["method"].isin(methods))]
        for metric in sorted(set(rq_rows["metric"])):
            metric_rows = rq_rows[rq_rows["metric"] == metric]
            pivot = metric_rows.pivot_table(index=["condition", "seed"], columns="method", values="value", aggfunc="mean")
            if not set(methods).issubset(pivot.columns):
                continue
            pivot = pivot.dropna(subset=methods)
            if pivot.empty:
                continue
            ranks = []
            for _, values in pivot[methods].iterrows():
                oriented = values.to_numpy(dtype=float)
                if metric not in LOWER_IS_BETTER:
                    oriented = -oriented
                ranks.append(rankdata(oriented, method="average"))
            rank_matrix = np.vstack(ranks)
            for index, method in enumerate(methods):
                output.append(
                    {
                        "protocol_group": rq,
                        "metric": metric,
                        "method": method,
                        "n_complete_cases": len(rank_matrix),
                        "average_rank": float(rank_matrix[:, index].mean()),
                    }
                )
    return pd.DataFrame(output)


def write_markdown(
    path: Path,
    summary: pd.DataFrame,
    paired: pd.DataFrame,
    ranks: pd.DataFrame,
    warnings: list[str],
) -> None:
    lines = ["# Three-RQ full experiment report", "", "## Completeness", ""]
    lines.append(f"- Aggregated scalar rows: {int(summary['n'].sum()) if not summary.empty else 0}")
    lines.append(f"- Completeness warnings: {len(warnings)}")
    if warnings:
        lines.extend(["", "### Warnings", "", *[f"- {warning}" for warning in warnings]])
    lines.extend(["", "## Mean and 95% confidence intervals", ""])
    if summary.empty:
        lines.append("No result rows found.")
    else:
        display = summary.copy()
        display["mean_ci95"] = display.apply(
            lambda row: f"{row['mean']:.6f} [{row['ci95_low']:.6f}, {row['ci95_high']:.6f}]", axis=1
        )
        lines.append(markdown_table(display[["protocol_group", "method", "metric", "n", "mean_ci95"]]))
    lines.extend(["", "## Paired H-EDL comparisons", ""])
    lines.append(markdown_table(paired) if not paired.empty else "No paired comparisons available.")
    lines.extend(["", "## Average ranks", ""])
    lines.append(markdown_table(ranks) if not ranks.empty else "No complete rank blocks available.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol-group", dest="rq", choices=["loao", "shift", "prevalence"])
    parser.add_argument("--results-root", type=Path, default=ROOT / "results" / "protocols")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "protocols" / "aggregate")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    matrix = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))
    rows, warnings = load_rows(args.results_root, matrix, args.rq)
    if args.strict:
        warnings.extend(full_completeness_warnings(matrix, args.rq))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows.to_csv(args.output_dir / "long_metrics.csv", index=False)
    summary = summarize(rows) if not rows.empty else pd.DataFrame()
    paired = paired_comparisons(rows, matrix) if not rows.empty else pd.DataFrame()
    ranks = average_ranks(rows, matrix) if not rows.empty else pd.DataFrame()
    summary.to_csv(args.output_dir / "summary_ci95.csv", index=False)
    paired.to_csv(args.output_dir / "paired_tests.csv", index=False)
    ranks.to_csv(args.output_dir / "average_ranks.csv", index=False)
    write_markdown(args.output_dir / "report.md", summary, paired, ranks, warnings)
    print(f"rows={len(rows)} warnings={len(warnings)} output={args.output_dir}")
    if args.strict and warnings:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
