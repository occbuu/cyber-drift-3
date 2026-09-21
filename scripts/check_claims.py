"""Every number the claim document states, checked against the generated tables.

A paper's numbers should not be retyped, and when they are, something has to
catch it.  This reads `results/paper/paper_tables.json`, recomputes each figure
the claim document quotes, formats it the way the document writes it, and fails
if the document does not contain that exact string.

    python scripts/check_claims.py            # report
    python scripts/check_claims.py --strict   # non-zero exit on any mismatch
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "paper" / "paper_tables.json"
CLAIMS = ROOT / "reports" / "PAPER_CLAIMS_2026-09-17.md"
OVERVIEW = ROOT / "TONG_QUAN_DU_AN.md"


def _draw(tables, dataset, q, pi, arm, field):
    for row in tables["rq1_rq2_draws"]["rows"]:
        if (row["dataset"] == dataset and row["q"] == q and row["prevalence"] == pi
                and row["arm"] == arm):
            value = row[field]
            return value["mean"] if isinstance(value, dict) else value
    raise KeyError(f"{dataset} q={q} pi={pi} {arm} {field}")


def checks(tables: dict) -> list[tuple[str, str]]:
    """(description, the exact string the claim document must contain)."""
    out: list[tuple[str, str]] = []

    contamination = tables["rq1_contamination"]
    out.append(("contamination floor", f"{contamination['holds']}/{contamination['cells']}"))

    prediction = tables["prediction_table"]["agreement"]
    out.append(("pre-stream classification", prediction.replace("/", " of ")))

    shipped = "PACT conditional L=100 (shipped)"
    for dataset, q, price in (("cse2018", 0.2, None), ("cse2018", 0.1, None), ("cicids2017", 0.2, None)):
        power = _draw(tables, dataset, q, 0.01, shipped, "power")
        out.append((f"{dataset} q={q} shipped power", f"{power:.3f}"))
        marginal = _draw(tables, dataset, q, 0.01, "marginal BH", "draws_over_q")
        out.append((f"{dataset} q={q} marginal draws over q", f"{100 * marginal:.0f}%"))

    for row in tables["rq1_rq2_draws"]["rq2"]:
        if row["dataset"] == "cse2018" and row["q"] == 0.2 and row["prevalence"] == 0.01:
            out.append(("cse2018 q=0.2 power price", f"{100 * row['relative_power_price']:.1f}%"))

    margin = tables["headline_bootstrap"]["rq3_margin_over_best_baseline"]
    out.append(("panel margin over best baseline", f"{margin['point']:+.3f}"))
    out.append(("panel margin interval", f"[{margin['low']:+.3f}, {margin['high']:+.3f}]"))

    gate = tables["rq4_shift_gate"]
    out.append(("shift-gate detection", f"{100 * gate['detection']:.1f}%"))
    out.append(("shift-gate false refusal", f"{100 * gate['false_refusal']:.1f}%"))
    out.append(("cicids2017 gate detection",
                f"{100 * gate['per_dataset']['cicids2017']['detection_where_broken']:.1f}%"))

    budget = tables["rq4_budget"]
    out.append(("cross-domain false refusal", f"{100 * budget['false_refusal']:.1f}%"))

    temporal = tables["temporal"]
    out.append(("temporal captures refused", temporal["temporal_refused_total"]))
    marginal_random = temporal["alerting"]["cse2018::marginal BH"]["Z1"]["fdr"]
    marginal_temporal = temporal["alerting"]["cse2018::marginal BH"]["T2"]["fdr"]
    out.append(("cse2018 marginal FDR, random split", f"{marginal_random:.3f}"))
    out.append(("cse2018 marginal FDR, temporal split", f"{marginal_temporal:.3f}"))

    # Guarded because two table builders once mixed the time-ordered split into
    # random-split rows through a shared dataset name.
    for key, value in tables["operator_baseline"].items():
        if key == "cse2018::0.1::0.01::top 0.1%":
            out.append(("operator top-0.1% streams over q", f"{100 * value['over_q']:.0f}%"))
        if key == "cse2018::0.1::0.001::top 0.1%":
            out.append(("operator top-0.1% FDP at pi=1e-3", f"{value['fdp']['mean']:.3f}"))

    components = tables["method_components"]
    pooled = components["evidential_pooled"]
    out.append(("evidential pooled difference", f"{pooled['difference']:+.4f}"))
    out.append(("curvature difference", f"{components['curvature']['difference']:+.4f}"))
    worst = max(abs(r["difference"]) for r in components["encoder"]["records"])
    out.append(("encoder ablation, largest cost", f"{worst:.3f}"))

    temporal_ext = tables.get("temporal_extension", {})
    if "alerting" in temporal_ext:
        out.append(("temporal extension refusals",
                    f"{temporal_ext['temporal_refused']} of {temporal_ext['captures']}"))
        for key, label in (("botiot::marginal BH", "NF-BoT-IoT-v3 marginal"),
                           ("unsw::marginal BH", "NF-UNSW-NB15-v3 marginal"),
                           ("botiot::PACT conditional L=100", "NF-BoT-IoT-v3 PACT")):
            entry = temporal_ext["alerting"].get(key)
            if entry:
                out.append((f"{label} FDR, random split", f"{entry['Z1']['fdr']:.3f}"))
                out.append((f"{label} FDR, temporal split", f"{entry['T2']['fdr']:.3f}"))

    extension = tables.get("rq1_extension", {})
    if "cells" in extension:
        out.append(("extension cells where marginal BH exceeded q",
                    f"{extension['marginal_cells_with_an_exceeding_draw']} of {extension['cells']}"))
        out.append(("extension certified cells", str(extension["certified"])))
        out.append(("extension certified cells with a draw over q",
                    str(extension["certified_cells_with_an_exceeding_draw"])))
        for dataset, q in (("insdn", 0.1), ("insdn", 0.2), ("cidds", 0.2)):
            row = next((r for r in extension["records"] if r["dataset"] == dataset
                        and r["q"] == q and r["prevalence"] == 0.01), None)
            if row:
                out.append((f"extension power, {dataset} q={q}", f"{row['pact_power']:.3f}"))

    null = tables.get("rq4_audit_null", {})
    for key, label in (("dkw::calibration", "exchangeable null, closed form"),
                       ("permutation::calibration", "exchangeable null, permutation"),
                       ("dkw::test", "held-out known traffic, closed form")):
        if key in null:
            out.append((f"audit fire rate, {label}", f"{100 * null[key]['fire_rate']:.1f}%"))
    if "per_dataset" in null:
        for dataset in ("ciciomt2024", "toniot", "cse2018", "cicids2017"):
            if dataset in null["per_dataset"]:
                out.append((f"audit fire rate on held-out known traffic, {dataset}",
                            f"{100 * null['per_dataset'][dataset]['test']:.1f}%"))

    permutation = tables.get("rq4_shift_gate_permutation", {})
    if "false_refusal" in permutation:
        out.append(("permutation arm false refusal", f"{100 * permutation['false_refusal']:.1f}%"))
        out.append(("permutation arm detection", f"{100 * permutation['detection']:.1f}%"))

    sensitivity = tables.get("rq1_prevalence_sensitivity", {})
    if "records" in sensitivity:
        out.append(("cells wrongly certified at twice the prevalence",
                    f"{sensitivity['wrongly_certified_at_double']}/{len(sensitivity['records'])}"))
        for q, prevalence in ((0.1, 0.01), (0.2, 0.01), (0.1, 0.001), (0.2, 0.001)):
            row = next(r for r in sensitivity["records"]
                       if r["q"] == q and r["prevalence"] == prevalence)
            out.append((f"prevalence factor that flips the state, q={q} pi={prevalence}",
                        f"{row['factor_to_certify']:.2f}"))

    # The claim that ranking quality does not determine certifiability rests on
    # these two correlations, so they are checked like any other quoted number.
    association = tables["rq1_panel_barrier"].get("auroc_vs_certified_power", {})
    for name, label in (("all", "all pairs"), ("auroc_at_least_0.90", "strong detectors")):
        if name in association:
            entry = association[name]
            out.append((f"AUROC vs certified power, {label}", f"{entry['spearman_rho']:.2f}"))
            out.append((f"AUROC vs certified power p, {label}", f"{entry['p']:.3f}"))

    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    tables = json.loads(TABLES.read_text(encoding="utf-8"))
    # Both documents quote the tables; a number may live in either.  The overview
    # writes decimals with a comma, so it is normalised before matching.
    document = CLAIMS.read_text(encoding="utf-8")
    if OVERVIEW.exists():
        overview = OVERVIEW.read_text(encoding="utf-8")
        document += "\n" + re.sub(r"(\d),(\d)", r"\1.\2", overview)
    # Markdown emphasis and non-breaking punctuation must not hide a match.
    flattened = re.sub(r"[*`]", "", document).replace("−", "-").replace("–", "-")

    failures = []
    for description, expected in checks(tables):
        if expected in flattened:
            print(f"  ok       {description:<42} {expected}")
        else:
            failures.append((description, expected))
            print(f"  MISMATCH {description:<42} generated: {expected}")

    print(f"\n{len(checks(tables)) - len(failures)} of {len(checks(tables))} quoted numbers match "
          f"{TABLES.relative_to(ROOT)}")
    if failures:
        print("The claim document quotes something the tables do not produce; fix the document, "
              "not the table.")
    if failures and args.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
