"""Deployment-time adaptation of the known-class reference, and its budget.

A source-trained encoder moved to a new network keeps its weights and loses its
geometry: the known families land somewhere else in latent space, the
known-class reference built on the source no longer describes them, and the
open-set score reads noise.  On NF-UNSW-NB15 to NF-ToN-IoT the source-only
scorer sits at 0.42 unknown AUROC, below a coin flip.

The obvious repair is to *transport* the source geometry onto the target using
a handful of verified target flows, and an earlier version of this module did
exactly that with a ridge affine map and per-class residual shrinkage.  That
machinery is gone, because measuring it against the right baseline showed it
was not doing the work.  Discarding the source reference entirely and keeping
only the thirty labelled target flows scored 0.816 AUROC and 0.749 OSCR against
0.840 and 0.768 for the full transport -- and when the trivial option was put
into the selection pool, the selector picked it.  What the data supports is not
a map between the two geometries but a single question: **how much of the
source reference is worth keeping at all.**

So the policy space here is one axis, ``retention_fraction``, running from
``anchors_only`` (keep nothing, trust the labelled target flows) to
``unaligned_full`` (keep everything, the do-nothing end), with an optional
per-class mean shift that costs one vector per class.

Measuring that axis over twelve cells -- three transfer cases by four
family-label budgets, three seeds each -- settles the design twice over.  The
winner is ``aligned_full``: keep every source row of an anchored class, shift
each class onto its anchors, drop the rest.  Mean AUROC regret against the best
policy in each cell is 0.0017, worst cell 0.0113.  And
:func:`select_reference_policy`, which picks per deployment using target knowns
only, has regret 0.0117 -- **seven times worse than simply always choosing
``aligned_full``**.  A selector that cannot beat a constant is not earning its
place, so the constant is the default and the selector stays only as the
ablation that demonstrates this.

The budget split is the other half.

Two of the four roles below need a *family
label* ("this is a port scan"), which is expensive and, as the shot sweep
shows, saturates around ten per class.  The other two need only *verified-known
status* ("this is not an attack"), which is cheap and, by the sizing rule in
:mod:`resolution`, is needed by the thousand.  Allocating the budget evenly
across the four roles -- the natural thing to do, and what the earlier version
did -- is therefore wrong by orders of magnitude on the cheap half.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

import numpy as np
from sklearn.metrics import balanced_accuracy_score

from .conformal import ConformalFusionScorer


@dataclass(frozen=True)
class AnchorSplit:
    """Disjoint target rows by the role they play, plus everything left over.

    ``geometry`` and ``selection`` carry family labels; ``calibration`` and
    ``audit`` are only asserted to be known traffic.  Separating them is what
    lets the budget study price the two kinds of label independently.
    """

    geometry: np.ndarray
    selection: np.ndarray
    calibration: np.ndarray
    audit: np.ndarray
    test: np.ndarray

    def family_labelled(self) -> np.ndarray:
        return np.concatenate([self.geometry, self.selection])

    def verified_known(self) -> np.ndarray:
        return np.concatenate([self.calibration, self.audit])

    def total_budget(self) -> int:
        return len(self.family_labelled()) + len(self.verified_known())


def allocate_target_budget(
    labels: np.ndarray,
    family_shots_per_class: int,
    verified_known_flows: int,
    seed: int,
    audit_fraction: float = 0.25,
) -> AnchorSplit:
    """Split a target labelling budget across the four deployment roles.

    Family-labelled rows are drawn per class, because a reference geometry
    needs every class represented.  Verified-known rows are drawn without
    regard to family, because a conformal calibration sample only has to be
    exchangeable with the known traffic being scored -- insisting on class
    balance there would make the calibration sample *less* like the traffic,
    not more.
    """
    labels = np.asarray(labels).reshape(-1)
    if family_shots_per_class < 0 or verified_known_flows < 0:
        raise ValueError("budget components must be non-negative")
    if not 0.0 < audit_fraction < 1.0:
        raise ValueError("audit_fraction must lie strictly between zero and one")

    rng = np.random.default_rng(seed)
    taken = np.zeros(len(labels), dtype=bool)
    geometry: list[np.ndarray] = []
    selection: list[np.ndarray] = []
    for label in np.unique(labels[labels >= 0]):
        pool = np.flatnonzero(labels == label)
        needed = 2 * family_shots_per_class
        if len(pool) < needed:
            raise ValueError(
                f"Known target class {label!r} has {len(pool)} rows, fewer than "
                f"two roles x {family_shots_per_class}"
            )
        picked = rng.choice(pool, needed, replace=False)
        geometry.append(picked[:family_shots_per_class])
        selection.append(picked[family_shots_per_class:])
        taken[picked] = True

    remaining_known = np.flatnonzero((labels >= 0) & ~taken)
    if verified_known_flows > len(remaining_known):
        raise ValueError(
            f"Requested {verified_known_flows} verified-known flows, only "
            f"{len(remaining_known)} target known rows remain"
        )
    verified = rng.choice(remaining_known, verified_known_flows, replace=False)
    audit_size = int(round(verified_known_flows * audit_fraction))
    taken[verified] = True

    empty = np.empty(0, dtype=np.int64)
    return AnchorSplit(
        geometry=np.concatenate(geometry).astype(np.int64) if geometry else empty,
        selection=np.concatenate(selection).astype(np.int64) if selection else empty,
        calibration=verified[audit_size:].astype(np.int64),
        audit=verified[:audit_size].astype(np.int64),
        test=np.flatnonzero(~taken).astype(np.int64),
    )


def _pooled_precision(
    features: np.ndarray, labels: np.ndarray, shrinkage: float = 1e-3
) -> np.ndarray:
    classes = np.unique(labels)
    means = {label: features[labels == label].mean(axis=0) for label in classes}
    centered = np.concatenate(
        [features[labels == label] - means[label] for label in classes], axis=0
    )
    covariance = np.atleast_2d(np.cov(centered, rowvar=False))
    scale = max(float(np.trace(covariance) / covariance.shape[0]), 1e-8)
    return np.linalg.pinv(covariance + shrinkage * scale * np.eye(covariance.shape[0]))


@dataclass
class TransportedGeometry:
    """Class-conditional Mahalanobis geometry over whatever reference survives."""

    classes: np.ndarray
    means: np.ndarray
    precision: np.ndarray

    @classmethod
    def fit(
        cls, features: np.ndarray, labels: np.ndarray, shrinkage: float = 1e-3
    ) -> "TransportedGeometry":
        classes = np.unique(labels)
        means = np.stack([features[labels == label].mean(axis=0) for label in classes])
        return cls(classes, means, _pooled_precision(features, labels, shrinkage))

    def distance_matrix(self, features: np.ndarray) -> np.ndarray:
        difference = features[:, None, :] - self.means[None, :, :]
        return np.einsum("nkd,df,nkf->nk", difference, self.precision, difference)

    def predict(self, features: np.ndarray) -> np.ndarray:
        return self.classes[self.distance_matrix(features).argmin(axis=1)]


@dataclass(frozen=True)
class ReferencePolicy:
    """One point on the keep-the-source axis.

    ``retention_fraction`` is the share of each anchored class's source rows
    kept, nearest-first to the anchor centre; zero keeps none.  ``align``
    applies a per-class mean shift before that, which is the cheapest repair
    that can exist -- one vector per class, no matrix, no gradient.
    """

    name: str
    retention_fraction: float
    align: bool


#: The measured default: per-class mean shift, keep every anchored-class row.
DEFAULT_REFERENCE_POLICY = ReferencePolicy("aligned_full", 1.0, True)

DEFAULT_REFERENCE_POLICIES = (
    ReferencePolicy("anchors_only", 0.0, False),
    ReferencePolicy("aligned_tenth", 0.1, True),
    ReferencePolicy("aligned_quarter", 0.25, True),
    ReferencePolicy("aligned_full", 1.0, True),
    ReferencePolicy("unaligned_full", 1.0, False),
)

MINIMUM_RETAINED_PER_CLASS = 32


def build_reference(
    policy: ReferencePolicy,
    source_features: np.ndarray,
    source_labels: np.ndarray,
    anchor_features: np.ndarray,
    anchor_labels: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, dict[str, float | str]]:
    """Assemble the known-class reference this policy would deploy.

    Classes absent from the target anchors are dropped outright.  A family that
    was known on some other network is not evidence that the same family is
    benign-and-expected here, and keeping it means scoring target traffic
    against a cluster nothing in the target ever occupies.
    """
    source_features = np.asarray(source_features, dtype=np.float64)
    anchor_features = np.asarray(anchor_features, dtype=np.float64)
    source_labels = np.asarray(source_labels).reshape(-1)
    anchor_labels = np.asarray(anchor_labels).reshape(-1)
    anchored = np.intersect1d(np.unique(source_labels), np.unique(anchor_labels))
    if not len(anchored):
        raise ValueError("The reference needs at least one class shared with the anchors")

    retained: list[np.ndarray] = []
    retained_labels: list[np.ndarray] = []
    eligible = 0
    shifts: list[float] = []
    for label in anchored:
        rows = np.flatnonzero(source_labels == label)
        if not len(rows):
            continue
        eligible += len(rows)
        anchor_centre = anchor_features[anchor_labels == label].mean(axis=0)
        cloud = source_features[rows]
        if policy.align:
            shift = anchor_centre - cloud.mean(axis=0)
            cloud = cloud + shift
            shifts.append(float(np.linalg.norm(shift)))
        if policy.retention_fraction <= 0.0:
            continue
        keep = min(
            len(rows),
            max(
                MINIMUM_RETAINED_PER_CLASS,
                int(np.ceil(len(rows) * policy.retention_fraction)),
            ),
        )
        distances = np.sum((cloud - anchor_centre) ** 2, axis=1)
        selected = np.argpartition(distances, keep - 1)[:keep]
        retained.append(cloud[selected])
        retained_labels.append(np.full(keep, label, dtype=source_labels.dtype))

    dimension = source_features.shape[1]
    source_reference = (
        np.concatenate(retained, axis=0)
        if retained
        else np.empty((0, dimension), dtype=np.float64)
    )
    source_reference_labels = (
        np.concatenate(retained_labels, axis=0)
        if retained_labels
        else np.empty(0, dtype=source_labels.dtype)
    )
    features = np.concatenate([source_reference, anchor_features], axis=0).astype(np.float32)
    labels = np.concatenate([source_reference_labels, anchor_labels], axis=0)
    diagnostics: dict[str, float | str] = {
        "reference_policy": policy.name,
        "reference_retention_fraction": float(policy.retention_fraction),
        "reference_aligned": float(policy.align),
        "reference_anchored_classes": float(len(anchored)),
        "reference_retained_source_rows": float(len(source_reference)),
        "reference_retained_source_fraction": float(len(source_reference) / max(1, eligible)),
        "reference_mean_class_shift": float(np.mean(shifts)) if shifts else 0.0,
    }
    return features, labels, diagnostics


def _selection_margin(
    geometry: TransportedGeometry, features: np.ndarray, labels: np.ndarray
) -> float:
    """Median relative gap to the nearest wrong class, on held-out anchors.

    Balanced accuracy alone saturates when the budget is tiny -- with five
    anchors a class is either right or wrong and ties are common -- so the
    margin breaks those ties with how *comfortably* the reference separates the
    classes, which is also what the open-set score reads.
    """
    distances = geometry.distance_matrix(features)
    column = {int(label): index for index, label in enumerate(geometry.classes)}
    rows = np.arange(len(labels))
    true_column = np.array([column[int(label)] for label in labels], dtype=np.int64)
    true_distance = distances[rows, true_column]
    alternatives = distances.copy()
    alternatives[rows, true_column] = np.inf
    nearest = alternatives.min(axis=1)
    return float(np.median((nearest - true_distance) / (nearest + 1e-8)))


@dataclass
class SelectedReference:
    policy: ReferencePolicy
    geometry: TransportedGeometry
    features: np.ndarray
    labels: np.ndarray
    candidates: list[dict[str, float | str]] = field(default_factory=list)

    def diagnostics(self) -> dict[str, float | str]:
        chosen = next(
            (c for c in self.candidates if c["reference_policy"] == self.policy.name), {}
        )
        return {**chosen, "selection_candidates": self.candidates}


def select_reference_policy(
    source_features: np.ndarray,
    source_labels: np.ndarray,
    geometry_features: np.ndarray,
    geometry_labels: np.ndarray,
    selection_features: np.ndarray,
    selection_labels: np.ndarray,
    policies: Iterable[ReferencePolicy] = DEFAULT_REFERENCE_POLICIES,
) -> SelectedReference:
    """Choose how much source reference to keep, using target knowns only."""
    evaluations: list[tuple[tuple[float, float], ReferencePolicy, dict[str, float | str]]] = []
    for policy in policies:
        features, labels, diagnostics = build_reference(
            policy, source_features, source_labels, geometry_features, geometry_labels
        )
        geometry = TransportedGeometry.fit(features, labels)
        predictions = geometry.predict(selection_features)
        accuracy = float(balanced_accuracy_score(selection_labels, predictions))
        margin = _selection_margin(geometry, selection_features, selection_labels)
        evaluations.append(
            (
                (accuracy, margin),
                policy,
                {
                    **diagnostics,
                    "selection_balanced_accuracy": accuracy,
                    "selection_median_margin": margin,
                },
            )
        )

    _, chosen, _ = max(evaluations, key=lambda item: item[0])
    # Refit on both family-labelled roles once the policy is fixed: the
    # selection anchors were spent deciding and can now be spent describing.
    anchor_features = np.concatenate([geometry_features, selection_features], axis=0)
    anchor_labels = np.concatenate([geometry_labels, selection_labels], axis=0)
    features, labels, _ = build_reference(
        chosen, source_features, source_labels, anchor_features, anchor_labels
    )
    return SelectedReference(
        policy=chosen,
        geometry=TransportedGeometry.fit(features, labels),
        features=features,
        labels=labels,
        candidates=[diagnostics for _, _, diagnostics in evaluations],
    )


def fit_reference_scorer(
    selected: SelectedReference,
    tuning_features: np.ndarray,
    tuning_labels: np.ndarray,
    calibration_features: np.ndarray,
    tail_extension: bool = False,
    tail_confidence: float = 0.9,
) -> ConformalFusionScorer:
    """Fuse the three geometry statistics over the adapted reference."""
    scorer = ConformalFusionScorer(
        tail_extension=tail_extension, tail_confidence=tail_confidence
    ).fit(
        {"tangent": selected.features},
        selected.labels,
        {"tangent": tuning_features},
        tuning_labels,
    )
    scorer.set_calibration(calibration_features)
    return scorer
