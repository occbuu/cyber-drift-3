"""RQ3: when does group-conditional (Mondrian) calibration pay for itself?

Proposition 11 prices grouping before any score is read: group ``g`` inherits
its own floor ``1/(n_g + 1)``, so it can alert at prevalence ``pi`` only if
``n_g >= 1 / (q pi c_g) - 1``, where ``c_g`` is the group's attack
concentration (share of the window's attacks over share of its flows).  Pooled
calibration pays one barrier for everyone but reads every group against the
tail of the most heterogeneous known class, which can hold an entire group's
attacks at zero power.

This runner measures both sides on cached scores, grouping by the detector's
predicted known class -- the one grouping variable every capture carries:

* per group: calibration size, attack concentration, the Prop. 11 verdict;
* per group, at the headline prevalence: in-group power of pooled BH versus
  Mondrian BH (p-values against the group's own calibration, BH over the whole
  window), and in-group false alarms;
* stream level: aggregate FDP and power of both procedures;
* validity: the exchangeability audit pooled versus inside each group.

The claim gate asks for a group whose pooled in-group power is zero and whose
Mondrian power is not, and for the Prop. 11 verdict to predict, before the
stream is drawn, which groups can and cannot benefit.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from .data import (cap_open_set_data, encode_known_labels, hold_out_groups,
                   load_holdout_groups, load_rotation, V7_ROOT)
from .fdr import benjamini_hochberg, conformal_pvalues, stratified_calibration_split
from .pact import exchangeability_audit
from .resolution import mondrian_break_even
from .run_fdr import _unique_source_indices


ROOT = Path(__file__).resolve().parents[2]
SCORES = ROOT / "results" / "scores"


PORT_EDGES = (1024.0, 49152.0)          # well-known / registered / ephemeral
PORT_NAMES = ("port<1024", "port1024-49151", "port>=49152")
PROTOCOL_NAMES = {1.0: "icmp", 6.0: "tcp", 17.0: "udp"}
PORT_FEATURES = ("l4_dst_port", "destination_port")
PROTOCOL_FEATURES = ("protocol", "protocol_type")


def _raw_column(data, dataset: str, split, names: tuple[str, ...]) -> tuple[np.ndarray, str]:
    """One feature of a split, back in raw units."""
    feature_names = [name.lower() for name in data.feature_names]
    for wanted in names:
        if wanted in feature_names:
            index = feature_names.index(wanted)
            transform = json.loads(
                (V7_ROOT / "partitions" / dataset / "rq1" / "Z1" / "transform.json")
                .read_text(encoding="utf-8")
            )
            entry = transform["features"][data.feature_names[index]]
            return split.x[:, index].astype(np.float64) * entry["scale"] + entry["offset"], wanted
    raise KeyError(f"{dataset}: none of {names} is in the feature schema")


def covariate_groups(dataset: str, scenario: str, grouping: str, seed: int,
                     tuning_fraction: float, arrays) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Group ids for the calibration and test rows of a capture.

    The capture stores scores, not features, so the rows are rebuilt from the
    frozen partition with the same steps ``capture_scores`` used -- hold-out
    groups, label encoding, deduplication by source id, the same stratified
    tuning split -- and the reconstruction is checked against the labels stored
    in the capture before anything is computed from it.
    """
    data = load_rotation(dataset, scenario)
    data = hold_out_groups(data, load_holdout_groups(dataset))
    data, _ = encode_known_labels(cap_open_set_data(data, None, seed))
    calibration_mask = data.calibration.y >= 0
    cal_ids = data.calibration.source_ids[calibration_mask]
    keep = _unique_source_indices(cal_ids)
    cal_rows = np.flatnonzero(calibration_mask)[keep]
    cal_y = data.calibration.y[cal_rows]
    test_rows = _unique_source_indices(data.test.source_ids)
    _, calibration_indices = stratified_calibration_split(cal_y, tuning_fraction, seed + 101)

    if not np.array_equal(data.test.y[test_rows], arrays["test_labels"]):
        raise RuntimeError("test rows do not line up with the capture")
    if not np.array_equal(cal_y[calibration_indices], arrays["calibration_labels"]):
        raise RuntimeError("calibration rows do not line up with the capture")

    if grouping == "port_class":
        cal_raw, name = _raw_column(data, dataset, data.calibration, PORT_FEATURES)
        test_raw, _ = _raw_column(data, dataset, data.test, PORT_FEATURES)
        cal_group = np.digitize(cal_raw[cal_rows][calibration_indices], PORT_EDGES)
        test_group = np.digitize(test_raw[test_rows], PORT_EDGES)
        labels = list(PORT_NAMES)
    elif grouping == "protocol":
        cal_raw, name = _raw_column(data, dataset, data.calibration, PROTOCOL_FEATURES)
        test_raw, _ = _raw_column(data, dataset, data.test, PROTOCOL_FEATURES)
        values = np.round(np.concatenate([cal_raw[cal_rows][calibration_indices], test_raw[test_rows]]))
        present = sorted(set(values.tolist()))
        index = {value: position for position, value in enumerate(present)}
        cal_group = np.array([index[v] for v in np.round(cal_raw[cal_rows][calibration_indices])])
        test_group = np.array([index[v] for v in np.round(test_raw[test_rows])])
        labels = [PROTOCOL_NAMES.get(v, f"proto{int(v)}") for v in present]
    else:
        raise ValueError(f"unknown grouping {grouping!r}")
    return cal_group, test_group, labels


def mondrian_pvalues(
    calibration: np.ndarray,
    calibration_groups: np.ndarray,
    scores: np.ndarray,
    groups: np.ndarray,
    min_group: int,
) -> np.ndarray:
    """Conformal p-values within each predicted group; pooled for tiny groups."""
    p_values = np.empty(len(scores), dtype=np.float64)
    for group in np.unique(groups):
        mask = groups == group
        reference = calibration[calibration_groups == group]
        if len(reference) < min_group:
            reference = calibration
        p_values[mask] = conformal_pvalues(reference, scores[mask])
    return p_values


def run_capture(tag: str, method: str, args: argparse.Namespace) -> dict[str, object]:
    arrays = np.load(SCORES / f"{tag}.npz")
    metadata = json.loads((SCORES / f"{tag}.json").read_text(encoding="utf-8"))
    calibration = arrays[f"{method}__calibration_scores"].astype(np.float64)
    test = arrays[f"{method}__test_scores"].astype(np.float64)
    is_unknown = arrays["test_is_unknown"]
    families = metadata["known_families"]
    if args.grouping == "predicted_class":
        calibration_groups = arrays[f"{method}__calibration_predictions"]
        test_groups = arrays[f"{method}__test_predictions"]
        group_names = list(families)
    else:
        calibration_groups, test_groups, group_names = covariate_groups(
            metadata["dataset"], metadata.get("scenario", "Z1"), args.grouping,
            int(metadata["seed"]), float(metadata["tuning_fraction"]), arrays,
        )
        families = group_names

    known_idx = np.flatnonzero(~is_unknown)
    unknown_idx = np.flatnonzero(is_unknown)
    group_ids = sorted(set(np.unique(calibration_groups).tolist()) | set(np.unique(test_groups).tolist()))
    groups_used = len([g for g in group_ids if (calibration_groups == g).sum() >= args.min_group])

    pooled_audit = exchangeability_audit(calibration, test[known_idx], args.audit_alpha)
    rng = np.random.default_rng(args.seed)
    prevalence = args.prevalence
    attacks_per_window = []
    stats = {g: {"pooled_hits": 0, "mondrian_hits": 0, "attacks": 0, "pooled_false": 0,
                 "mondrian_false": 0, "flows": 0} for g in group_ids}
    totals = {"pooled": [0, 0], "mondrian": [0, 0], "attacks": 0}
    for _ in range(args.windows):
        count = int(rng.binomial(args.window_size, prevalence))
        picked = np.concatenate([
            rng.choice(known_idx, args.window_size - count),
            rng.choice(unknown_idx, count),
        ])
        scores, groups, unknown = test[picked], test_groups[picked], is_unknown[picked]
        pooled = benjamini_hochberg(conformal_pvalues(calibration, scores), args.q)
        mondrian = benjamini_hochberg(
            mondrian_pvalues(calibration, calibration_groups, scores, groups, args.min_group), args.q
        )
        attacks_per_window.append(count)
        totals["attacks"] += count
        for name, rejected in (("pooled", pooled), ("mondrian", mondrian)):
            totals[name][0] += int(rejected.sum())
            totals[name][1] += int((rejected & unknown).sum())
        for g in np.unique(groups):
            mask = groups == g
            s = stats[int(g)]
            s["attacks"] += int((mask & unknown).sum())
            s["flows"] += int(mask.sum())
            s["pooled_hits"] += int((mask & unknown & pooled).sum())
            s["mondrian_hits"] += int((mask & unknown & mondrian).sum())
            s["pooled_false"] += int((mask & ~unknown & pooled).sum())
            s["mondrian_false"] += int((mask & ~unknown & mondrian).sum())

    rows = []
    for g in group_ids:
        s = stats[g]
        n_g = int((calibration_groups == g).sum())
        flow_share = float((test_groups[known_idx] == g).mean())
        attack_share = float((test_groups[unknown_idx] == g).mean())
        if s["attacks"] < args.min_group_attacks or n_g < args.min_group:
            continue
        concentration = attack_share / flow_share if flow_share > 0 else float("inf")
        verdict = mondrian_break_even(
            max(1, n_g * groups_used), groups_used, args.q, prevalence,
            attack_concentration=max(concentration, 1e-9) if np.isfinite(concentration) else 1e9,
        )
        in_group_audit = exchangeability_audit(
            calibration[calibration_groups == g],
            test[known_idx][test_groups[known_idx] == g],
            args.audit_alpha,
        ) if (test_groups[known_idx] == g).sum() >= 50 else {}
        rows.append({
            "group": int(g),
            "group_family": families[int(g)] if 0 <= int(g) < len(families) else str(g),
            "calibration_size": n_g,
            "known_flow_share": flow_share,
            "attack_share": attack_share,
            "attack_concentration": concentration,
            "prop11_affordable": bool(verdict["affordable"]),
            "prop11_required_per_group": float(1.0 / (args.q * prevalence * max(concentration, 1e-9)) - 1.0),
            "pooled_in_group_power": s["pooled_hits"] / s["attacks"],
            "mondrian_in_group_power": s["mondrian_hits"] / s["attacks"],
            "pooled_in_group_false_per_1000": 1000.0 * s["pooled_false"] / max(1, s["flows"]),
            "mondrian_in_group_false_per_1000": 1000.0 * s["mondrian_false"] / max(1, s["flows"]),
            "in_group_audit_rejected": in_group_audit.get("superuniform_audit_rejected"),
        })

    def aggregate(name):
        alerts, hits = totals[name]
        return {"fdp": (alerts - hits) / alerts if alerts else 0.0,
                "power": hits / totals["attacks"] if totals["attacks"] else 0.0,
                "alerts_per_1000": 1000.0 * alerts / (args.windows * args.window_size)}

    lifted = [r for r in rows if r["pooled_in_group_power"] == 0.0 and r["mondrian_in_group_power"] > 0.0]
    predicted = [r for r in rows if r["prop11_affordable"] == (r["mondrian_in_group_power"] > 0.0)]
    return {
        "tag": tag,
        "dataset": metadata["dataset"],
        "scenario": metadata.get("scenario"),
        "seed": metadata.get("seed"),
        "method": method,
        "prevalence": prevalence,
        "groups_used": groups_used,
        "pooled": aggregate("pooled"),
        "mondrian": aggregate("mondrian"),
        "pooled_audit_rejected": bool(pooled_audit["superuniform_audit_rejected"]),
        "groups_with_in_group_audit_rejected": int(sum(bool(r["in_group_audit_rejected"]) for r in rows)),
        "groups_evaluated": len(rows),
        "groups_lifted_from_zero": [r["group_family"] for r in lifted],
        "prop11_predicts_benefit_correctly": f"{len(predicted)}/{len(rows)}",
        "groups": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--methods", default="hedl")
    # Prop. 11 is about any grouping variable, not only the predicted class: a
    # covariate that concentrates attacks is exactly the case the break-even
    # condition says can pay for itself.
    parser.add_argument("--grouping", default="predicted_class",
                        choices=("predicted_class", "port_class", "protocol"))
    parser.add_argument("--prevalences", default="0.01,0.001")
    parser.add_argument("--q", type=float, default=0.1)
    parser.add_argument("--window-size", type=int, default=2000)
    parser.add_argument("--windows", type=int, default=400)
    parser.add_argument("--min-group", type=int, default=50)
    parser.add_argument("--min-group-attacks", type=int, default=20)
    parser.add_argument("--audit-alpha", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    started = time.perf_counter()
    results = []
    for method in (m.strip() for m in args.methods.split(",") if m.strip()):
        for prevalence in (float(v) for v in args.prevalences.split(",")):
            args.prevalence = prevalence
            report = run_capture(args.tag, method, args)
            results.append(report)
            print(f"[mondrian] {args.tag} {method} pi={prevalence}: pooled {report['pooled']} "
                  f"mondrian {report['mondrian']} lifted {report['groups_lifted_from_zero']}", flush=True)
    payload = {"protocol": f"mondrian_{args.grouping}", "tag": args.tag,
               "grouping": args.grouping, "results": results,
               "elapsed_seconds": time.perf_counter() - started}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
