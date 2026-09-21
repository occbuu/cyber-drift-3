"""Which attack families can a flow-level model tell apart at all?

Leave-one-attack-out assumes the held-out family is *new*.  When a family is
indistinguishable, flow by flow, from a family that stays in training, the
rotation does not test zero-day detection: every detector simply scores the
held-out flows like their known twin, and the ranking between detectors is
decided by how each happens to score that twin.  The audit below finds such
twins from labelled training data only and turns them into hold-out groups:
a rotation that holds out one member of a group holds out the whole group.

The rule is fixed before any open-set score is looked at again:

* data: the train partitions of every rotation of the dataset, mapped back to
  raw feature units and deduplicated by source id -- no calibration or test
  flow is read;
* for every pair of attack families, a gradient-boosted binary classifier is
  scored by 5-fold out-of-fold balanced accuracy (at most 3000 flows per
  family);
* two attack families are *inseparable* when that balanced accuracy is below
  ``SEPARABILITY_THRESHOLD`` (0.80, i.e. more than one flow in five cannot be
  attributed to the right family); groups are the connected components;
* benign is never merged with an attack family -- that confusion is the
  detection problem itself, not a labelling artefact.

Known-class labels are left at their original granularity: the classifier
still learns both twins when neither is held out, so rotations that do not
touch a group are unchanged.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import yaml
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import StratifiedKFold

from .data import V7_ROOT


SEPARABILITY_THRESHOLD = 0.80
SENSITIVITY_THRESHOLDS = (0.70, 0.90)
MAX_PER_FAMILY = 3000
FOLDS = 5
SEED = 13
AUDIT_ROOT = V7_ROOT / "separability"
NEVER_MERGED = ("benign",)


def _raw_train_pool(dataset: str) -> tuple[np.ndarray, np.ndarray]:
    manifest = yaml.safe_load((V7_ROOT / "manifests" / f"{dataset}_v7.yaml").read_text(encoding="utf-8"))
    xs, families, ids = [], [], []
    feature_names = None
    for scenario in manifest["rq1"]["rotations"]:
        base = V7_ROOT / "partitions" / dataset / "rq1" / scenario
        archive = np.load(base / "train.npz", allow_pickle=False)
        names = tuple(archive["feature_names"].astype(str).tolist())
        feature_names = feature_names or names
        if names != feature_names:
            raise ValueError(f"{dataset}: feature schema differs between rotations")
        transform = json.loads((base / "transform.json").read_text(encoding="utf-8"))
        offsets = np.array([transform["features"][n]["offset"] for n in names], dtype=np.float64)
        scales = np.array([transform["features"][n]["scale"] for n in names], dtype=np.float64)
        xs.append(archive["x"].astype(np.float64) * scales + offsets)
        families.append(archive["families"].astype(str))
        ids.append(archive["source_ids"].astype(str))
    x = np.concatenate(xs)
    fam = np.concatenate(families)
    _, first = np.unique(np.concatenate(ids), return_index=True)
    first = np.sort(first)
    return x[first], fam[first]


def pairwise_separability(x: np.ndarray, families: np.ndarray, family_a: str, family_b: str) -> float:
    rng = np.random.default_rng(SEED)
    chosen = []
    for family in (family_a, family_b):
        idx = np.flatnonzero(families == family)
        chosen.append(rng.choice(idx, min(MAX_PER_FAMILY, len(idx)), replace=False))
    idx = np.concatenate(chosen)
    y = (families[idx] == family_b).astype(int)
    folds = min(FOLDS, int(np.bincount(y).min()))
    if folds < 2:
        return float("nan")
    predictions = np.empty_like(y)
    splitter = StratifiedKFold(n_splits=folds, shuffle=True, random_state=SEED)
    for train, test in splitter.split(idx, y):
        model = HistGradientBoostingClassifier(max_iter=150, random_state=SEED)
        model.fit(x[idx[train]], y[train])
        predictions[test] = model.predict(x[idx[test]])
    return float(balanced_accuracy_score(y, predictions))


def holdout_groups(pairs: list[dict[str, object]], threshold: float) -> list[list[str]]:
    parent: dict[str, str] = {}

    def find(a: str) -> str:
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for pair in pairs:
        a, b, score = pair["family_a"], pair["family_b"], pair["balanced_accuracy"]
        if a in NEVER_MERGED or b in NEVER_MERGED or not np.isfinite(score):
            continue
        if score < threshold:
            parent[find(a)] = find(b)
    components: dict[str, list[str]] = {}
    for family in parent:
        components.setdefault(find(family), []).append(family)
    return sorted(sorted(group) for group in components.values() if len(group) > 1)


def audit(dataset: str) -> dict[str, object]:
    x, families = _raw_train_pool(dataset)
    names = sorted(set(families.tolist()))
    pairs = []
    for a, b in itertools.combinations(names, 2):
        score = pairwise_separability(x, families, a, b)
        pairs.append({"family_a": a, "family_b": b, "balanced_accuracy": score})
        flag = "  <-- inseparable" if score < SEPARABILITY_THRESHOLD and "benign" not in (a, b) else ""
        print(f"[separability] {dataset}: {a} vs {b}: {score:.3f}{flag}", flush=True)
    return {
        "dataset": dataset,
        "threshold": SEPARABILITY_THRESHOLD,
        "max_per_family": MAX_PER_FAMILY,
        "folds": FOLDS,
        "seed": SEED,
        "train_flows": int(len(families)),
        "family_counts": {name: int(np.sum(families == name)) for name in names},
        "pairs": sorted(pairs, key=lambda p: p["balanced_accuracy"]),
        "groups": holdout_groups(pairs, SEPARABILITY_THRESHOLD),
        "sensitivity": {str(t): holdout_groups(pairs, t) for t in SENSITIVITY_THRESHOLDS},
    }


def load_groups(dataset: str) -> list[list[str]]:
    path = AUDIT_ROOT / f"{dataset}.json"
    if not path.exists():
        raise FileNotFoundError(f"No separability audit for {dataset}; run experiments.open_set.separability")
    return json.loads(path.read_text(encoding="utf-8"))["groups"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--datasets", default="cicids2017,ciciomt2024,nf_ton_iot_v3,nf_cse_cic_ids2018_v3"
    )
    args = parser.parse_args()
    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    for dataset in (name.strip() for name in args.datasets.split(",") if name.strip()):
        report = audit(dataset)
        (AUDIT_ROOT / f"{dataset}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"[separability] {dataset}: groups {report['groups']}", flush=True)


if __name__ == "__main__":
    main()
