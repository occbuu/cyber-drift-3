"""Known-only conformal scoring for open-set zero-day detection.

The scorer reads three complementary geometry statistics off the hyperbolic
tangent space that the H-EDL encoder already produces, converts each one into a
conformal p-value against the held-out calibration split, and combines the
p-values with Fisher's method.  No unknown-class sample is used at any point.

References
    Bates, Candes, Lei, Romano and Sesia. Testing for outliers with conformal
        p-values. Annals of Statistics 51(1), 2023.
    Ren, Fort, Liu, Guha Roy, Padhy and Lakshminarayanan. A simple fix to
        Mahalanobis distance for improving near-OOD detection. 2021.
    Sun, Ming, Zhu and Li. Out-of-distribution detection with deep nearest
        neighbors. ICML 2022.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import torch
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import NearestNeighbors

from .tail import TailExtendedCalibration

COMPONENT_NAMES = ("md", "rmd", "knn")


def conformal_pvalue(calibration: np.ndarray, values: np.ndarray) -> np.ndarray:
    """One-sided conformal p-value for the hypothesis that ``values`` are known.

    ``p(x) = (1 + #{c in calibration : c >= x}) / (n + 1)``.  Small p means the
    observation sits in the extreme upper tail of the known-class distribution,
    and thresholding p at ``alpha`` controls the false-alarm rate at ``alpha``
    in finite samples when the calibration split is exchangeable with the
    known-class test traffic.
    """
    reference = np.sort(np.asarray(calibration, dtype=np.float64))
    greater_or_equal = len(reference) - np.searchsorted(reference, values, side="left")
    return (1.0 + greater_or_equal) / (len(reference) + 1.0)


def _shrunk_precision(centered: np.ndarray, shrinkage: float) -> np.ndarray:
    covariance = np.atleast_2d(np.cov(centered, rowvar=False))
    ridge = shrinkage * np.trace(covariance) / covariance.shape[0]
    return np.linalg.pinv(covariance + ridge * np.eye(covariance.shape[0]))


@dataclass
class TangentGeometry:
    """Class-conditional and background Gaussians of the tangent space."""

    means: np.ndarray
    precision: np.ndarray
    background_mean: np.ndarray
    background_precision: np.ndarray

    @classmethod
    def fit(cls, features: np.ndarray, labels: np.ndarray, shrinkage: float = 1e-6) -> "TangentGeometry":
        classes = np.unique(labels)
        means = np.stack([features[labels == label].mean(axis=0) for label in classes])
        centered = np.concatenate(
            [features[labels == label] - means[index] for index, label in enumerate(classes)], axis=0
        )
        background_mean = features.mean(axis=0, keepdims=True)
        return cls(
            means=means,
            precision=_shrunk_precision(centered, shrinkage),
            background_mean=background_mean,
            background_precision=_shrunk_precision(features - background_mean, shrinkage),
        )

    def class_distance(self, features: np.ndarray) -> np.ndarray:
        difference = features[:, None, :] - self.means[None, :, :]
        return np.einsum("nkd,df,nkf->nk", difference, self.precision, difference).min(axis=1)

    def background_distance(self, features: np.ndarray) -> np.ndarray:
        difference = features - self.background_mean
        return np.einsum("nd,df,nf->n", difference, self.background_precision, difference)


def _normalise(features: np.ndarray) -> np.ndarray:
    return features / np.maximum(np.linalg.norm(features, axis=1, keepdims=True), 1e-12)


def _neighbor_index(reference: np.ndarray, neighbors: int) -> NearestNeighbors:
    """Brute-force index on purpose.

    The latent space has a few tens of dimensions, where tree indices degenerate
    to a full scan with a large constant factor, while the brute-force path is a
    single BLAS matrix product.  Forcing it keeps inference latency predictable
    and roughly an order of magnitude lower than the sklearn ``auto`` choice.
    """
    return NearestNeighbors(
        n_neighbors=min(neighbors, len(reference)), algorithm="brute", metric="euclidean", n_jobs=-1
    ).fit(reference)


def _uniform_indices(population: int, maximum: int, seed: int = 13) -> np.ndarray:
    """Uniform subsample, which preserves the empirical density.

    The nearest-neighbour statistic estimates how crowded the neighbourhood of a
    flow is, so its reference set has to keep the natural class proportions.
    Class-balancing the reference -- the right thing to do when *fitting* a
    classifier -- inflates rare families and deflates common ones, and measurably
    degrades the low-false-alarm end of the detector.
    """
    if population <= maximum:
        return np.arange(population)
    return np.random.default_rng(seed).choice(population, maximum, replace=False)


def _balanced_indices(labels: np.ndarray, maximum: int, seed: int = 13) -> np.ndarray:
    if len(labels) <= maximum:
        return np.arange(len(labels))
    rng = np.random.default_rng(seed)
    classes = np.unique(labels)
    per_class = max(1, maximum // len(classes))
    selected = []
    for label in classes:
        indices = np.flatnonzero(labels == label)
        selected.append(rng.choice(indices, min(per_class, len(indices)), replace=False))
    indices = np.concatenate(selected)
    if len(indices) < maximum:
        remaining = np.setdiff1d(np.arange(len(labels)), indices, assume_unique=False)
        extra = rng.choice(remaining, min(maximum - len(indices), len(remaining)), replace=False)
        indices = np.concatenate([indices, extra])
    return indices


@dataclass
class ConformalFusionScorer:
    """Fisher fusion of conformal p-values over tangent-space geometry.

    ``md``   class-conditional Mahalanobis distance minimised over the known
             prototypes; a parametric O(K d^2) view of cluster membership.
    ``rmd``  relative Mahalanobis, ``md`` minus the distance under a single
             background Gaussian fitted to all known traffic, which cancels the
             shared feature-norm component that dominates near-OOD scores.
    ``knn``  distance to the nearest L2-normalised training reference, the
             non-parametric counterpart that captures multi-modal families.

    Fusion weights come from a leave-one-class-out proxy AUROC estimated from
    known families only, so the selection never observes zero-day traffic.

    ``tail_extension`` addresses a ceiling that is easy to miss.  Each
    component p-value is bounded below by ``1 / (n_tuning + 1)``, so the fused
    score ``-sum_i w_i log p_i`` is bounded *above* by
    ``sum_i w_i log(n_tuning + 1)``.  Every flow past that point receives the
    same score, attacker and benign alike, and the far tail -- the only region
    a low-prevalence alerting policy ever reads -- collapses into one tie.  On
    CICIDS2017 that tie holds 2,600 test flows.  Switching the extension on
    replaces each component's floored p-value with the tail-extended version
    from :mod:`tail`, which removes the ceiling and restores an ordering where
    deployment actually operates.  It is off by default because it trades the
    distribution-free guarantee for a fitted tail model, and that trade should
    be a deliberate, audited choice.
    """

    neighbors: int = 1
    max_reference: int = 65536
    max_proxy_calibration: int = 2048
    proxy_reference: int = 4096
    shrinkage: float = 1e-6
    components: tuple[str, ...] = COMPONENT_NAMES
    tail_extension: bool = False
    tail_anchor_exceedances: int = 250
    tail_confidence: float = 0.0
    geometry: TangentGeometry | None = None
    reference: np.ndarray | None = None
    calibration_statistics: dict[str, np.ndarray] = field(default_factory=dict)
    component_tails: dict[str, TailExtendedCalibration] = field(default_factory=dict)
    weights: dict[str, float] = field(default_factory=dict)
    proxy_aurocs: dict[str, float] = field(default_factory=dict)
    _neighbor_model: NearestNeighbors | None = None

    @staticmethod
    def _assemble(
        geometry: TangentGeometry,
        neighbor_model: NearestNeighbors | None,
        features: np.ndarray,
        components: tuple[str, ...],
    ) -> dict[str, np.ndarray]:
        # Evaluated lazily: a profile that drops "knn" must not pay for the
        # neighbour query, which is the whole point of dropping it.
        statistics: dict[str, np.ndarray] = {}
        class_distance = None
        if {"md", "rmd"}.intersection(components):
            class_distance = geometry.class_distance(features)
        if "md" in components:
            statistics["md"] = class_distance
        if "rmd" in components:
            statistics["rmd"] = class_distance - geometry.background_distance(features)
        if "knn" in components:
            if neighbor_model is None:
                raise RuntimeError("The knn component needs a fitted neighbour index")
            statistics["knn"] = neighbor_model.kneighbors(_normalise(features), return_distance=True)[0][:, -1]
        return {name: statistics[name] for name in components}

    def _statistics(self, features: np.ndarray) -> dict[str, np.ndarray]:
        if self.geometry is None:
            raise RuntimeError("ConformalFusionScorer is not fitted")
        return self._assemble(self.geometry, self._neighbor_model, features, self.components)

    def _proxy_weights(
        self,
        train_features: np.ndarray,
        train_labels: np.ndarray,
        calibration_features: np.ndarray,
        calibration_labels: np.ndarray,
    ) -> tuple[dict[str, float], dict[str, float]]:
        """Hold out one known family at a time, refit every statistic without it,
        and measure how well each separates that family from the rest."""
        proxy_indices = _balanced_indices(calibration_labels, self.max_proxy_calibration)
        proxy_features = calibration_features[proxy_indices]
        proxy_labels = calibration_labels[proxy_indices]
        reference_indices = _balanced_indices(train_labels, self.proxy_reference, seed=29)
        reference_features = train_features[reference_indices]
        reference_labels = train_labels[reference_indices]

        collected: dict[str, list[np.ndarray]] = {name: [] for name in self.components}
        targets: list[np.ndarray] = []
        for held_out in np.unique(reference_labels):
            positive = proxy_labels == held_out
            if positive.sum() < 2 or (~positive).sum() < 2:
                continue
            mask = reference_labels != held_out
            if int(mask.sum()) < max(self.neighbors, 2) or len(np.unique(reference_labels[mask])) < 2:
                continue
            geometry = TangentGeometry.fit(reference_features[mask], reference_labels[mask], self.shrinkage)
            neighbor_model = (
                _neighbor_index(_normalise(reference_features[mask]), self.neighbors)
                if "knn" in self.components else None
            )
            statistics = self._assemble(geometry, neighbor_model, proxy_features, self.components)
            targets.append(positive.astype(np.int64))
            for name in self.components:
                collected[name].append(statistics[name])
        if not targets:
            return {name: 1.0 for name in self.components}, {name: 0.5 for name in self.components}
        target = np.concatenate(targets)
        aurocs = {name: float(roc_auc_score(target, np.concatenate(values))) for name, values in collected.items()}
        raw = {name: max(0.0, value - 0.5) for name, value in aurocs.items()}
        total = sum(raw.values())
        if total <= 0.0:
            return {name: 1.0 for name in self.components}, aurocs
        weights = {name: len(self.components) * value / total for name, value in raw.items()}
        return weights, aurocs

    def fit(
        self,
        train_outputs: dict[str, np.ndarray],
        train_labels: np.ndarray,
        calibration_outputs: dict[str, np.ndarray],
        calibration_labels: np.ndarray,
    ) -> "ConformalFusionScorer":
        train_features = train_outputs["tangent"]
        calibration_features = calibration_outputs["tangent"]
        self.geometry = TangentGeometry.fit(train_features, train_labels, self.shrinkage)
        if "knn" in self.components:
            self.reference = train_features[_uniform_indices(len(train_features), self.max_reference)]
            self._neighbor_model = _neighbor_index(_normalise(self.reference), self.neighbors)
        else:
            self.reference = None
            self._neighbor_model = None
        self.set_calibration(calibration_features)
        self.weights, self.proxy_aurocs = self._proxy_weights(
            train_features, train_labels, calibration_features, calibration_labels
        )
        return self

    def set_calibration(self, calibration_features: np.ndarray) -> "ConformalFusionScorer":
        """Point the component p-values at a new calibration sample.

        Deployment adaptation replaces the calibration split without touching
        the geometry or the fusion weights, and the tail models belong to the
        calibration sample rather than to the encoder, so they are refitted
        here and nowhere else.
        """
        self.calibration_statistics = self._statistics(calibration_features)
        self.component_tails = {}
        if self.tail_extension:
            for name, values in self.calibration_statistics.items():
                self.component_tails[name] = TailExtendedCalibration(
                    anchor_exceedances=self.tail_anchor_exceedances,
                    confidence=self.tail_confidence,
                ).fit(values)
        return self

    def _component_pvalues(self, name: str, values: np.ndarray) -> np.ndarray:
        tail = self.component_tails.get(name)
        if tail is None:
            return conformal_pvalue(self.calibration_statistics[name], values)
        return tail.pvalues(values)

    def score(self, outputs: dict[str, np.ndarray]) -> np.ndarray:
        if not self.calibration_statistics:
            raise RuntimeError("ConformalFusionScorer is not fitted")
        statistics = self._statistics(outputs["tangent"])
        fused = np.zeros(len(outputs["tangent"]), dtype=np.float64)
        for name, values in statistics.items():
            p_values = self._component_pvalues(name, values)
            fused -= self.weights[name] * np.log(np.clip(p_values, 1e-300, 1.0))
        return fused

    def to_torch(self, device: torch.device | str) -> "TorchConformalScorer":
        """Device-resident copy for deployment; same statistics, same p-values."""
        if self.geometry is None or not self.calibration_statistics:
            raise RuntimeError("ConformalFusionScorer is not fitted")
        return TorchConformalScorer.from_fitted(self, torch.device(device))

    def diagnostics(self) -> dict[str, float | str]:
        report: dict[str, float | str] = {
            "score_mode": "conformal_fisher_" + "_".join(self.components),
            "density_reference_size": float(len(self.reference)) if self.reference is not None else 0.0,
            "neighbors": float(self.neighbors),
        }
        for name in self.components:
            report[f"proxy_auroc_{name}"] = float(self.proxy_aurocs.get(name, 0.5))
            report[f"fusion_weight_{name}"] = float(self.weights.get(name, 0.0))
        report["tail_extension"] = "on" if self.component_tails else "off"
        for name, tail in self.component_tails.items():
            report[f"tail_shape_{name}"] = float(tail.shape)
            report[f"tail_anchor_pvalue_{name}"] = float(tail.anchor_pvalue)
        report["proxy_evidential_auroc"] = report.get("proxy_auroc_md", 0.5)
        report["proxy_density_auroc"] = report.get("proxy_auroc_knn", 0.5)
        return report


def _whitening(precision: np.ndarray) -> np.ndarray:
    """Matrix L with L @ L.T == precision, so a Mahalanobis form becomes a squared
    Euclidean norm after one matrix product.  Eigen-decomposition rather than
    Cholesky because a pseudo-inverse precision can be positive semi-definite."""
    values, vectors = np.linalg.eigh((precision + precision.T) / 2.0)
    return vectors * np.sqrt(np.clip(values, 0.0, None))[None, :]


class TorchConformalScorer:
    """The fitted ``ConformalFusionScorer`` evaluated with device tensors.

    The NumPy scorer is the reference implementation and is what gets fitted.
    This class only re-expresses its three statistics as dense matrix products --
    class-conditional Mahalanobis through a whitening transform, the background
    term the same way, and the 1-NN distance as a maximum cosine similarity --
    so that a batch of flows is scored with a handful of kernels on the same
    device as the encoder instead of a round trip through NumPy and scikit-learn.
    """

    def __init__(self, components, weights, neighbors, whitened_means, whitening,
                 background_mean, background_whitening, reference, calibration, tails=None):
        self.tails = tails or {}
        self.components = components
        self.weights = weights
        self.neighbors = neighbors
        self.whitened_means = whitened_means
        self.whitened_means_sq = whitened_means.pow(2).sum(dim=1)[None, :]
        self.whitening = whitening
        self.background_mean = background_mean
        self.background_whitening = background_whitening
        self.reference = reference
        self.calibration = calibration

    @classmethod
    def from_fitted(cls, scorer: "ConformalFusionScorer", device: torch.device) -> "TorchConformalScorer":
        tensor = lambda a: torch.as_tensor(np.asarray(a, dtype=np.float32), device=device)
        geometry = scorer.geometry
        whitening = _whitening(geometry.precision)
        reference = None
        if "knn" in scorer.components:
            reference = tensor(_normalise(scorer.reference))
        return cls(
            components=tuple(scorer.components),
            weights={name: float(scorer.weights[name]) for name in scorer.components},
            neighbors=int(scorer.neighbors),
            whitened_means=tensor(geometry.means @ whitening),
            whitening=tensor(whitening),
            background_mean=tensor(geometry.background_mean),
            background_whitening=tensor(_whitening(geometry.background_precision)),
            reference=reference,
            calibration={name: torch.sort(tensor(scorer.calibration_statistics[name])).values
                         for name in scorer.components},
            tails={name: _torch_tail(tail, device) for name, tail in scorer.component_tails.items()},
        )

    def statistics(self, tangent: torch.Tensor) -> dict[str, torch.Tensor]:
        values: dict[str, torch.Tensor] = {}
        if {"md", "rmd"}.intersection(self.components):
            z = tangent @ self.whitening
            squared = (z.pow(2).sum(dim=1, keepdim=True) - 2.0 * z @ self.whitened_means.T
                       + self.whitened_means_sq)
            class_distance = squared.clamp_min(0.0).min(dim=1).values
            if "md" in self.components:
                values["md"] = class_distance
            if "rmd" in self.components:
                background = ((tangent - self.background_mean) @ self.background_whitening).pow(2).sum(dim=1)
                values["rmd"] = class_distance - background
        if "knn" in self.components:
            query = tangent / tangent.norm(dim=1, keepdim=True).clamp_min(1e-12)
            similarity = query @ self.reference.T
            kth = similarity.topk(self.neighbors, dim=1).values[:, -1]
            values["knn"] = (2.0 - 2.0 * kth).clamp_min(0.0).sqrt()
        return values

    def score(self, tangent: torch.Tensor) -> torch.Tensor:
        # Float64 only with tails: a tail-extended p-value can sit far below the
        # 1e-12 a float32 log still resolves.  The floored path keeps float32 so
        # its scores stay bit-identical to captures made before tails existed.
        dtype = torch.float64 if self.tails else torch.float32
        fused = torch.zeros(len(tangent), dtype=dtype, device=tangent.device)
        for name, value in self.statistics(tangent).items():
            sorted_calibration = self.calibration[name]
            count = sorted_calibration.numel()
            at_least = count - torch.searchsorted(sorted_calibration, value.contiguous(), right=False)
            p_values = (1.0 + at_least.to(dtype)) / (count + 1.0)
            tail = self.tails.get(name)
            if tail is not None:
                p_values = _torch_tail_pvalues(tail, value.to(torch.float64), p_values)
                floor = 1e-300
            else:
                floor = 1e-12
            fused -= self.weights[name] * torch.log(p_values.clamp(floor, 1.0))
        return fused


def _torch_tail(tail, device: torch.device) -> dict[str, object]:
    """Device copy of a fitted ``TailExtendedCalibration`` (see ``tail.pvalues``)."""
    as64 = lambda a: torch.as_tensor(np.asarray(a, dtype=np.float64), device=device)
    use_grid = tail.confidence > 0.0 and tail.bootstrap >= 2
    return {
        "anchor": float(tail.anchor),
        "anchor_pvalue": float(tail.anchor_pvalue),
        "scale": float(tail.scale),
        "shape": float(tail.shape),
        "use_grid": use_grid,
        "grid": as64(tail._grid),
        "log_survival": as64(np.log(np.maximum(tail._grid_survival, 1e-300))),
    }


def _torch_interp(x: torch.Tensor, grid: torch.Tensor, values: torch.Tensor) -> torch.Tensor:
    """``np.interp`` semantics: linear inside the grid, clamped outside it."""
    x = x.clamp(grid[0], grid[-1])
    upper = torch.searchsorted(grid, x.contiguous(), right=True).clamp(1, grid.numel() - 1)
    lower = upper - 1
    x0, x1 = grid[lower], grid[upper]
    y0, y1 = values[lower], values[upper]
    weight = torch.where(x1 > x0, (x - x0) / (x1 - x0), torch.zeros_like(x))
    return y0 + weight * (y1 - y0)


def _torch_tail_pvalues(tail: dict[str, object], value: torch.Tensor, empirical: torch.Tensor) -> torch.Tensor:
    above = value > tail["anchor"]
    if not bool(above.any()):
        return empirical.clamp(0.0, 1.0)
    excess = (value - tail["anchor"]).clamp_min(0.0)
    if tail["use_grid"]:
        survival = torch.exp(_torch_interp(excess, tail["grid"], tail["log_survival"]))
    else:
        scale, shape = tail["scale"], tail["shape"]
        if scale <= 0.0:
            survival = torch.where(excess > 0.0, torch.zeros_like(excess), torch.ones_like(excess))
        elif abs(shape) < 1e-8:
            survival = torch.exp(-excess / scale)
        else:
            argument = 1.0 + shape * excess / scale
            argument = argument.clamp_min(0.0) if shape < 0.0 else argument.clamp_min(1e-300)
            survival = torch.pow(argument, -1.0 / shape)
    extended = tail["anchor_pvalue"] * survival
    return torch.where(above, extended, empirical).clamp(0.0, 1.0)
