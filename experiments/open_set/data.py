from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import yaml
from sklearn.preprocessing import RobustScaler


ROOT = Path(__file__).resolve().parents[2]
V7_ROOT = ROOT / "data" / "v7"
RAW_ROOT = ROOT / "data" / "dataraw"


@dataclass
class Split:
    x: np.ndarray
    y: np.ndarray
    families: np.ndarray
    source_ids: np.ndarray


@dataclass
class OpenSetData:
    train: Split
    calibration: Split
    test: Split
    known_families: tuple[str, ...]
    unknown_families: tuple[str, ...]
    feature_names: tuple[str, ...]

    @property
    def known_test_mask(self) -> np.ndarray:
        return np.isin(self.test.families, self.known_families)

    @property
    def unknown_test_mask(self) -> np.ndarray:
        return np.isin(self.test.families, self.unknown_families)


def _load_npz(path: Path) -> Split:
    archive = np.load(path, allow_pickle=False)
    return Split(
        x=archive["x"].astype(np.float32, copy=False),
        y=archive["y"].astype(np.int64, copy=False),
        families=archive["families"].astype(str),
        source_ids=archive["source_ids"].astype(str),
    )


def load_rotation(dataset: str, scenario: str) -> OpenSetData:
    manifest_path = V7_ROOT / "manifests" / f"{dataset}_v7.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    rotation = manifest["rq1"]["rotations"][scenario]
    base = V7_ROOT / "partitions" / dataset / "rq1" / scenario
    train_archive = np.load(base / "train.npz", allow_pickle=False)
    feature_names = tuple(train_archive["feature_names"].astype(str).tolist())
    train_archive.close()
    data = OpenSetData(
        train=_load_npz(base / "train.npz"),
        calibration=_load_npz(base / "calibration.npz"),
        test=_load_npz(base / "test.npz"),
        known_families=tuple(rotation["known_classes"]),
        unknown_families=tuple(rotation["unknown_classes"]),
        feature_names=feature_names,
    )
    validate_rotation(data)
    return data


def validate_rotation(data: OpenSetData) -> None:
    unknown = set(data.unknown_families)
    if unknown.intersection(data.train.families):
        raise ValueError("Unknown families leaked into training split")
    if unknown.intersection(data.calibration.families):
        raise ValueError("Unknown families leaked into calibration split")
    if not np.any(data.unknown_test_mask):
        raise ValueError("Test split contains no configured unknown samples")
    if data.train.x.shape[1] != len(data.feature_names):
        raise ValueError("Feature schema does not match train matrix")


def load_holdout_groups(dataset: str, threshold: float | None = None) -> list[list[str]]:
    """Inseparable attack-family groups from ``experiments.open_set.separability``.

    ``threshold`` selects one of the audit's sensitivity thresholds instead of
    the registered one; it exists for the sensitivity table, not for tuning.
    """
    path = V7_ROOT / "separability" / f"{dataset}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"No separability audit for {dataset}; run python -m experiments.open_set.separability"
        )
    report = yaml.safe_load(path.read_text(encoding="utf-8"))
    if threshold is None or abs(threshold - float(report["threshold"])) < 1e-9:
        return report["groups"]
    for key, groups in report["sensitivity"].items():
        if abs(float(key) - threshold) < 1e-9:
            return groups
    raise KeyError(f"{dataset}: no separability groups recorded at threshold {threshold}")


def hold_out_groups(data: OpenSetData, groups: Iterable[Iterable[str]]) -> OpenSetData:
    """Hold out every family that is inseparable from a held-out family.

    The twins leave the training and calibration splits, and their test flows
    become unknown.  The frozen test partition itself is not changed.  A
    rotation that holds out no group member comes back unchanged.
    """
    unknown = set(data.unknown_families)
    twins: list[str] = []
    for group in groups:
        group = list(group)
        if unknown.intersection(group):
            twins.extend(family for family in group if family in data.known_families)
    if not twins:
        return data
    known = tuple(family for family in data.known_families if family not in twins)
    unknown_families = tuple(dict.fromkeys((*data.unknown_families, *twins)))

    def drop(split: Split) -> Split:
        keep = ~np.isin(split.families, twins)
        return Split(split.x[keep], split.y[keep], split.families[keep], split.source_ids[keep])

    grouped = OpenSetData(
        train=drop(data.train),
        calibration=drop(data.calibration),
        test=data.test,
        known_families=known,
        unknown_families=unknown_families,
        feature_names=data.feature_names,
    )
    validate_rotation(grouped)
    return grouped


def cap_open_set_data(data: OpenSetData, max_rows: int | None, seed: int = 13) -> OpenSetData:
    if max_rows is None:
        return data

    def cap(split: Split, split_seed: int) -> Split:
        if len(split.x) <= max_rows:
            return split
        rng = np.random.default_rng(split_seed)
        selected: list[np.ndarray] = []
        families = np.unique(split.families)
        per_family = max(1, max_rows // len(families))
        for family in families:
            indices = np.flatnonzero(split.families == family)
            selected.append(rng.choice(indices, min(per_family, len(indices)), replace=False))
        indices = np.concatenate(selected)
        if len(indices) < max_rows:
            remaining = np.setdiff1d(np.arange(len(split.x)), indices, assume_unique=False)
            extra = rng.choice(remaining, min(max_rows - len(indices), len(remaining)), replace=False)
            indices = np.concatenate([indices, extra])
        rng.shuffle(indices)
        return Split(split.x[indices], split.y[indices], split.families[indices], split.source_ids[indices])

    capped = OpenSetData(
        train=cap(data.train, seed),
        calibration=cap(data.calibration, seed + 1),
        test=cap(data.test, seed + 2),
        known_families=data.known_families,
        unknown_families=data.unknown_families,
        feature_names=data.feature_names,
    )
    validate_rotation(capped)
    return capped


def encode_known_labels(data: OpenSetData) -> tuple[OpenSetData, dict[str, int]]:
    label_map = {family: index for index, family in enumerate(data.known_families)}

    def encode(split: Split) -> Split:
        labels = np.array([label_map.get(family, -1) for family in split.families], dtype=np.int64)
        return Split(split.x, labels, split.families, split.source_ids)

    return OpenSetData(
        train=encode(data.train),
        calibration=encode(data.calibration),
        test=encode(data.test),
        known_families=data.known_families,
        unknown_families=data.unknown_families,
        feature_names=data.feature_names,
    ), label_map


def derive_multi_unknown(
    data: OpenSetData,
    additional_unknown_families: Iterable[str],
) -> OpenSetData:
    additional = tuple(dict.fromkeys(additional_unknown_families))
    invalid = set(additional).difference(data.known_families)
    if invalid:
        raise ValueError(f"Additional unknown families are not known in base rotation: {sorted(invalid)}")
    unknown = tuple(dict.fromkeys((*data.unknown_families, *additional)))
    known = tuple(family for family in data.known_families if family not in unknown)

    moved_x: list[np.ndarray] = []
    moved_families: list[np.ndarray] = []
    moved_ids: list[np.ndarray] = []

    def remove_unknown(split: Split) -> Split:
        mask = ~np.isin(split.families, unknown)
        moved = ~mask
        if np.any(moved):
            moved_x.append(split.x[moved])
            moved_families.append(split.families[moved])
            moved_ids.append(split.source_ids[moved])
        return Split(split.x[mask], split.y[mask], split.families[mask], split.source_ids[mask])

    train = remove_unknown(data.train)
    calibration = remove_unknown(data.calibration)
    test_known = remove_unknown(data.test)
    x_unknown = np.concatenate(moved_x, axis=0)
    families_unknown = np.concatenate(moved_families, axis=0)
    ids_unknown = np.concatenate(moved_ids, axis=0)
    test = Split(
        x=np.concatenate([test_known.x, x_unknown], axis=0),
        y=np.concatenate([test_known.y, np.full(len(x_unknown), -1, dtype=np.int64)]),
        families=np.concatenate([test_known.families, families_unknown]),
        source_ids=np.concatenate([test_known.source_ids, ids_unknown]),
    )
    derived = OpenSetData(train, calibration, test, known, unknown, data.feature_names)
    validate_rotation(derived)
    return derived


NETFLOW_FILES = {
    "nf_unsw_nb15_v3": RAW_ROOT / "NF-UNSW-NB15-v3" / "NF-UNSW-NB15-v3.csv",
    "nf_ton_iot_v3": RAW_ROOT / "NF-ToN-IoT-v3" / "NF-ToN-IoT-v3.csv",
    "nf_bot_iot_v3": RAW_ROOT / "NF-BoT-IoT-v3" / "NF-BoT-IoT-v3.csv",
    "nf_cse_cic_ids2018_v3": RAW_ROOT / "NF-CSE-CIC-IDS2018-v3" / "NF-CICIDS2018-v3.csv",
}


def load_raw_netflow_sample(dataset: str, max_rows: int | None = None) -> tuple[pd.DataFrame, pd.Series]:
    path = NETFLOW_FILES[dataset]
    feature_names = list(load_rotation(dataset, "Z1").feature_names)
    raw_columns = [name.upper() for name in feature_names]
    frame = pd.read_csv(path, usecols=[*raw_columns, "Attack"], nrows=max_rows)
    x = frame[raw_columns].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    x.columns = feature_names
    families = frame["Attack"].astype(str).str.strip().str.lower().str.replace(" ", "_", regex=False)
    return x, families


def source_fitted_cross_domain(
    source_dataset: str,
    target_dataset: str,
    max_rows: int | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, tuple[str, ...]]:
    source = load_rotation(source_dataset, "Z1")
    target = load_rotation(target_dataset, "Z1")
    if source.feature_names != target.feature_names:
        raise ValueError("Source and target feature schemas differ")
    source_classes = source.known_families
    target_x = np.concatenate([target.train.x, target.calibration.x, target.test.x], axis=0)
    target_families = np.concatenate(
        [target.train.families, target.calibration.families, target.test.families], axis=0
    )
    target_ids = np.concatenate(
        [target.train.source_ids, target.calibration.source_ids, target.test.source_ids], axis=0
    )
    _, unique_indices = np.unique(target_ids, return_index=True)
    unique_indices = np.sort(unique_indices)
    target_x = target_x[unique_indices]
    target_families = target_families[unique_indices]
    shared = tuple(sorted(set(source_classes).intersection(target_families)))
    if "benign" not in shared:
        raise ValueError("Cross-domain protocol requires a shared benign class")
    label_map = {family: index for index, family in enumerate(source_classes)}
    source_train_y = np.array([label_map[family] for family in source.train.families], dtype=np.int64)
    source_calibration_y = np.array(
        [label_map[family] for family in source.calibration.families], dtype=np.int64
    )
    source_transform_path = V7_ROOT / "partitions" / source_dataset / "rq1" / "Z1" / "transform.json"
    target_transform_path = V7_ROOT / "partitions" / target_dataset / "rq1" / "Z1" / "transform.json"
    source_transform = yaml.safe_load(source_transform_path.read_text(encoding="utf-8"))
    target_transform = yaml.safe_load(target_transform_path.read_text(encoding="utf-8"))
    source_offsets = np.array(
        [source_transform["features"][name]["offset"] for name in source.feature_names], dtype=np.float64
    )
    source_scales = np.array(
        [source_transform["features"][name]["scale"] for name in source.feature_names], dtype=np.float64
    )
    target_offsets = np.array(
        [target_transform["features"][name]["offset"] for name in target.feature_names], dtype=np.float64
    )
    target_scales = np.array(
        [target_transform["features"][name]["scale"] for name in target.feature_names], dtype=np.float64
    )
    raw_target = target_x.astype(np.float64) * target_scales + target_offsets
    target_scaled = ((raw_target - source_offsets) / source_scales).astype(np.float32)
    target_y = np.array([label_map.get(family, -1) for family in target_families], dtype=np.int64)

    def cap(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        if max_rows is None or len(x) <= max_rows:
            return x, y
        rng = np.random.default_rng(13)
        selected: list[np.ndarray] = []
        classes = np.unique(y)
        per_class = max(1, max_rows // len(classes))
        for label in classes:
            indices = np.flatnonzero(y == label)
            selected.append(rng.choice(indices, min(per_class, len(indices)), replace=False))
        indices = np.concatenate(selected)
        if len(indices) < max_rows:
            remaining = np.setdiff1d(np.arange(len(y)), indices, assume_unique=False)
            extra = rng.choice(remaining, min(max_rows - len(indices), len(remaining)), replace=False)
            indices = np.concatenate([indices, extra])
        rng.shuffle(indices)
        return x[indices], y[indices]

    source_train, source_train_y = cap(source.train.x, source_train_y)
    source_calibration, source_calibration_y = cap(source.calibration.x, source_calibration_y)
    target_scaled, target_y = cap(target_scaled, target_y)
    return (
        source_train,
        source_train_y,
        source_calibration,
        source_calibration_y,
        target_scaled,
        target_y,
        shared,
    )


def _inverse_v7_transform(dataset: str, x: np.ndarray, feature_names: tuple[str, ...]) -> np.ndarray:
    transform_path = V7_ROOT / "partitions" / dataset / "rq1" / "Z1" / "transform.json"
    transform = yaml.safe_load(transform_path.read_text(encoding="utf-8"))
    offsets = np.array([transform["features"][name]["offset"] for name in feature_names], dtype=np.float64)
    scales = np.array([transform["features"][name]["scale"] for name in feature_names], dtype=np.float64)
    return x.astype(np.float64) * scales + offsets


def source_fitted_leave_one_domain_out(
    source_datasets: Iterable[str],
    target_dataset: str,
    max_rows: int | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, tuple[str, ...]]:
    source_names = tuple(source_datasets)
    if target_dataset in source_names:
        raise ValueError("Target dataset must not be one of the source datasets")
    sources = [(name, load_rotation(name, "Z1")) for name in source_names]
    target = load_rotation(target_dataset, "Z1")
    feature_names = sources[0][1].feature_names
    if any(data.feature_names != feature_names for _, data in sources) or target.feature_names != feature_names:
        raise ValueError("All leave-one-domain-out datasets must share the same feature schema")

    known_families = tuple(sorted(set().union(*(set(data.known_families) for _, data in sources))))
    if "benign" not in known_families:
        raise ValueError("Leave-one-domain-out protocol requires a shared benign class")
    label_map = {family: index for index, family in enumerate(known_families)}

    train_raw: list[np.ndarray] = []
    train_labels: list[np.ndarray] = []
    calibration_raw: list[np.ndarray] = []
    calibration_labels: list[np.ndarray] = []
    for name, data in sources:
        train_raw.append(_inverse_v7_transform(name, data.train.x, feature_names))
        calibration_raw.append(_inverse_v7_transform(name, data.calibration.x, feature_names))
        train_labels.append(np.array([label_map[family] for family in data.train.families], dtype=np.int64))
        calibration_labels.append(
            np.array([label_map[family] for family in data.calibration.families], dtype=np.int64)
        )

    train_raw_array = np.concatenate(train_raw, axis=0)
    train_y = np.concatenate(train_labels, axis=0)
    calibration_raw_array = np.concatenate(calibration_raw, axis=0)
    calibration_y = np.concatenate(calibration_labels, axis=0)
    scaler = RobustScaler().fit(train_raw_array)
    train_x = scaler.transform(train_raw_array).astype(np.float32)
    calibration_x = scaler.transform(calibration_raw_array).astype(np.float32)

    target_x_all = np.concatenate([target.train.x, target.calibration.x, target.test.x], axis=0)
    target_families = np.concatenate(
        [target.train.families, target.calibration.families, target.test.families], axis=0
    )
    target_ids = np.concatenate([target.train.source_ids, target.calibration.source_ids, target.test.source_ids])
    _, unique_indices = np.unique(target_ids, return_index=True)
    unique_indices = np.sort(unique_indices)
    target_raw = _inverse_v7_transform(target_dataset, target_x_all[unique_indices], feature_names)
    target_x = scaler.transform(target_raw).astype(np.float32)
    target_families = target_families[unique_indices]
    target_y = np.array([label_map.get(family, -1) for family in target_families], dtype=np.int64)

    def cap(x: np.ndarray, y: np.ndarray, seed: int) -> tuple[np.ndarray, np.ndarray]:
        if max_rows is None or len(x) <= max_rows:
            return x, y
        rng = np.random.default_rng(seed)
        selected: list[np.ndarray] = []
        labels = np.unique(y)
        per_label = max(1, max_rows // len(labels))
        for label in labels:
            indices = np.flatnonzero(y == label)
            selected.append(rng.choice(indices, min(per_label, len(indices)), replace=False))
        indices = np.concatenate(selected)
        if len(indices) < max_rows:
            remaining = np.setdiff1d(np.arange(len(y)), indices, assume_unique=False)
            extra = rng.choice(remaining, min(max_rows - len(indices), len(remaining)), replace=False)
            indices = np.concatenate([indices, extra])
        rng.shuffle(indices)
        return x[indices], y[indices]

    train_x, train_y = cap(train_x, train_y, 13)
    calibration_x, calibration_y = cap(calibration_x, calibration_y, 37)
    target_x, target_y = cap(target_x, target_y, 73)
    shared = tuple(sorted(set(known_families).intersection(target_families)))
    return train_x, train_y, calibration_x, calibration_y, target_x, target_y, shared
