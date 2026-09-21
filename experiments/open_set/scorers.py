from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import torch
import torch.nn.functional as F
from scipy.stats import weibull_min
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import NearestNeighbors

def msp(logits: torch.Tensor) -> np.ndarray: return (1.0 - F.softmax(logits, dim=1).max(dim=1).values).detach().cpu().numpy()
def energy(logits: torch.Tensor, temperature: float = 1.0) -> np.ndarray: return (-temperature * torch.logsumexp(logits / temperature, dim=1)).detach().cpu().numpy()

def odin(model: torch.nn.Module, inputs: torch.Tensor, temperature: float = 1000.0, magnitude: float = 0.0014) -> np.ndarray:
    perturbed = inputs.detach().clone().requires_grad_(True)
    logits, _ = model(perturbed)
    pseudo_labels = logits.argmax(dim=1)
    loss = F.cross_entropy(logits / temperature, pseudo_labels)
    model.zero_grad(set_to_none=True)
    loss.backward()
    direction = perturbed.grad.sign()
    with torch.no_grad():
        logits, _ = model(perturbed - magnitude * direction)
    return (1.0 - F.softmax(logits / temperature, dim=1).max(dim=1).values).cpu().numpy()

def empirical_tail(reference: np.ndarray, values: np.ndarray) -> np.ndarray:
    sorted_reference = np.sort(np.asarray(reference, dtype=np.float64))
    return np.searchsorted(sorted_reference, values, side="right") / (len(sorted_reference) + 1.0)

@dataclass
class KnownOnlyHEDLScorer:
    neighbors: int = 10
    max_reference: int = 4096
    max_proxy_calibration: int = 2048
    density_selection_margin: float = 0.10
    reference_embeddings: np.ndarray | None = None
    calibration_vacuity: np.ndarray | None = None
    calibration_density: np.ndarray | None = None
    selected_mode: str = "fused"
    proxy_evidential_auroc: float = 0.5
    proxy_density_auroc: float = 0.5
    _neighbor_model: NearestNeighbors | None = None

    @staticmethod
    def _balanced_indices(labels: np.ndarray, maximum: int) -> np.ndarray:
        if len(labels) <= maximum: return np.arange(len(labels))
        rng = np.random.default_rng(13)
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

    @classmethod
    def _balanced_reference(cls, embeddings: np.ndarray, labels: np.ndarray, maximum: int) -> tuple[np.ndarray, np.ndarray]:
        indices = cls._balanced_indices(labels, maximum)
        return embeddings[indices], labels[indices]

    def _density(self, embeddings: np.ndarray) -> np.ndarray:
        if self._neighbor_model is None: raise RuntimeError("KnownOnlyHEDLScorer is not fitted")
        distances = self._neighbor_model.kneighbors(embeddings, return_distance=True)[0]
        return distances.mean(axis=1)

    def _proxy_aurocs(self, train_embeddings: np.ndarray, train_labels: np.ndarray, calibration_outputs: dict[str, np.ndarray], calibration_labels: np.ndarray) -> tuple[float, float]:
        proxy_labels: list[np.ndarray] = []
        proxy_evidential: list[np.ndarray] = []
        proxy_density: list[np.ndarray] = []
        classes = np.unique(train_labels)
        for held_out in classes:
            positive = calibration_labels == held_out
            negative = ~positive
            if positive.sum() < 2 or negative.sum() < 2: continue
            reference_mask = train_labels != held_out
            reference, _ = self._balanced_reference(train_embeddings[reference_mask], train_labels[reference_mask], self.max_reference)
            model = NearestNeighbors(n_neighbors=min(self.neighbors, len(reference))).fit(reference)
            density = model.kneighbors(calibration_outputs["embedding"], return_distance=True)[0].mean(axis=1)
            keep = np.arange(calibration_outputs["alpha"].shape[1]) != held_out
            reduced_alpha = calibration_outputs["alpha"][:, keep]
            vacuity = reduced_alpha.shape[1] / reduced_alpha.sum(axis=1)
            proxy_labels.append(positive.astype(np.int64))
            proxy_density.append(empirical_tail(density[negative], density))
            proxy_evidential.append(empirical_tail(vacuity[negative], vacuity))
        if not proxy_labels: return 0.5, 0.5
        all_labels = np.concatenate(proxy_labels)
        all_evidential = np.concatenate(proxy_evidential)
        all_density = np.concatenate(proxy_density)
        return roc_auc_score(all_labels, all_evidential), roc_auc_score(all_labels, all_density)

    def fit(self, train_outputs: dict[str, np.ndarray], train_labels: np.ndarray, calibration_outputs: dict[str, np.ndarray], calibration_labels: np.ndarray) -> "KnownOnlyHEDLScorer":
        reference, reference_labels = self._balanced_reference(train_outputs["embedding"], train_labels, self.max_reference)
        self.reference_embeddings = reference
        self._neighbor_model = NearestNeighbors(n_neighbors=min(self.neighbors, len(reference))).fit(reference)
        self.calibration_vacuity = calibration_outputs["vacuity"]
        self.calibration_density = self._density(calibration_outputs["embedding"])
        proxy_indices = self._balanced_indices(calibration_labels, self.max_proxy_calibration)
        proxy_outputs = {name: values[proxy_indices] for name, values in calibration_outputs.items()}
        self.proxy_evidential_auroc, self.proxy_density_auroc = self._proxy_aurocs(reference, reference_labels, proxy_outputs, calibration_labels[proxy_indices])
        
        self.selected_mode = "fused"
        return self

    def score(self, outputs: dict[str, np.ndarray]) -> np.ndarray:
        if self.calibration_vacuity is None or self.calibration_density is None: raise RuntimeError("KnownOnlyHEDLScorer is not fitted")
        density = self._density(outputs["embedding"])
        density_score = empirical_tail(self.calibration_density, density)
        evidential_score = empirical_tail(self.calibration_vacuity, outputs["vacuity"])
        w_e = max(0.0, self.proxy_evidential_auroc - 0.5)
        w_d = max(0.0, self.proxy_density_auroc - 0.5)
        total = w_e + w_d
        if total == 0: return evidential_score
        return (w_e / total) * evidential_score + (w_d / total) * density_score

    def diagnostics(self) -> dict[str, float | str]:
        return {
            "score_mode": self.selected_mode,
            "proxy_evidential_auroc": self.proxy_evidential_auroc,
            "proxy_density_auroc": self.proxy_density_auroc,
            "density_selection_margin": self.density_selection_margin,
            "density_reference_size": float(len(self.reference_embeddings)) if self.reference_embeddings is not None else 0.0,
        }

@dataclass
class MahalanobisScorer:
    means: np.ndarray | None = None
    precision: np.ndarray | None = None
    def fit(self, features: np.ndarray, labels: np.ndarray) -> "MahalanobisScorer":
        classes = np.unique(labels)
        self.means = np.stack([features[labels == label].mean(axis=0) for label in classes])
        centered = np.concatenate([features[labels == label] - self.means[index] for index, label in enumerate(classes)], axis=0)
        covariance = np.cov(centered, rowvar=False)
        self.precision = np.linalg.pinv(covariance + np.eye(covariance.shape[0]) * 1e-5)
        return self
    def score(self, features: np.ndarray) -> np.ndarray:
        if self.means is None or self.precision is None: raise RuntimeError("MahalanobisScorer is not fitted")
        differences = features[:, None, :] - self.means[None, :, :]
        distances = np.einsum("nkd,df,nkf->nk", differences, self.precision, differences)
        return distances.min(axis=1)

@dataclass
class OpenMaxScorer:
    tail_size: int = 20
    alpha_rank: int = 10
    class_means: np.ndarray | None = None
    weibull_models: list[tuple[float, float, float]] | None = None
    def fit(self, activations: np.ndarray, labels: np.ndarray, predictions: np.ndarray) -> "OpenMaxScorer":
        classes = np.unique(labels)
        means: list[np.ndarray] = []
        models: list[tuple[float, float, float]] = []
        for label in classes:
            correct = activations[(labels == label) & (predictions == label)]
            if len(correct) == 0: correct = activations[labels == label]
            mean = correct.mean(axis=0)
            distances = np.linalg.norm(correct - mean, axis=1)
            tail = np.sort(distances)[-min(self.tail_size, len(distances)) :]
            shape, location, scale = weibull_min.fit(tail, floc=0)
            means.append(mean)
            models.append((shape, location, max(scale, 1e-8)))
        self.class_means = np.stack(means)
        self.weibull_models = models
        return self
    def score(self, activations: np.ndarray) -> np.ndarray:
        if self.class_means is None or self.weibull_models is None: raise RuntimeError("OpenMaxScorer is not fitted")
        ranks = np.argsort(-activations, axis=1)
        revised = activations.copy()
        unknown = np.zeros(len(activations), dtype=np.float64)
        top = min(self.alpha_rank, activations.shape[1])
        for row in range(len(activations)):
            for rank in range(top):
                label = ranks[row, rank]
                distance = np.linalg.norm(activations[row] - self.class_means[label])
                weight = weibull_min.cdf(distance, *self.weibull_models[label])
                alpha = (top - rank) / top
                removed = revised[row, label] * weight * alpha
                revised[row, label] -= removed
                unknown[row] += removed
        augmented = np.concatenate([revised, unknown[:, None]], axis=1)
        augmented -= augmented.max(axis=1, keepdims=True)
        probabilities = np.exp(augmented)
        probabilities /= probabilities.sum(axis=1, keepdims=True)
        return probabilities[:, -1]

@dataclass
class PrototypeDistanceScorer:
    """Lightweight scorer: uses model's own hyperbolic distances + vacuity. O(K) not O(N).
    
    Key insight: the model already computes distances to prototypes in forward().
    We just reuse those distances directly — no need for separate kNN or Euclidean centroids.
    """
    calibration_min_dist: np.ndarray | None = None
    calibration_vacuity: np.ndarray | None = None
    selected_mode: str = "prototype_vacuity"
    vacuity_weight: float = 0.5
    proxy_evidential_auroc: float = 0.5
    proxy_distance_auroc: float = 0.5

    def fit(self, train_outputs: dict[str, np.ndarray], train_labels: np.ndarray,
            calibration_outputs: dict[str, np.ndarray], calibration_labels: np.ndarray) -> "PrototypeDistanceScorer":
        self.calibration_min_dist = calibration_outputs["distances"].min(axis=1)
        self.calibration_vacuity = self._uncertainty(calibration_outputs)
        self.proxy_evidential_auroc, self.proxy_distance_auroc = self._proxy_aurocs(
            calibration_outputs, calibration_labels)
        w_v = max(0.0, self.proxy_evidential_auroc - 0.5)
        w_d = max(0.0, self.proxy_distance_auroc - 0.5)
        total = w_v + w_d
        self.vacuity_weight = w_v / total if total > 0 else 0.5
        return self

    @staticmethod
    def _uncertainty(outputs: dict[str, np.ndarray]) -> np.ndarray:
        """Evidential uncertainty: 1 - (max_alpha - 1) / (sum_alpha - K).
        High when evidence is spread or total evidence is low."""
        alpha = outputs["alpha"]
        K = alpha.shape[1]
        S = alpha.sum(axis=1)
        max_ev = alpha.max(axis=1) - 1.0
        total_ev = S - K
        ratio = np.where(total_ev > 1e-6, max_ev / total_ev, 0.0)
        return 1.0 - ratio

    def score(self, outputs: dict[str, np.ndarray]) -> np.ndarray:
        if self.calibration_min_dist is None:
            raise RuntimeError("PrototypeDistanceScorer is not fitted")
        min_dist = outputs["distances"].min(axis=1)
        dist_tail = empirical_tail(self.calibration_min_dist, min_dist)
        unc = self._uncertainty(outputs)
        unc_tail = empirical_tail(self.calibration_vacuity, unc)
        return np.maximum(dist_tail, unc_tail)

    def diagnostics(self) -> dict[str, float | str]:
        return {
            "score_mode": self.selected_mode,
            "proxy_evidential_auroc": self.proxy_evidential_auroc,
            "proxy_density_auroc": self.proxy_distance_auroc,
            "vacuity_weight": self.vacuity_weight,
            "density_reference_size": 0.0,
        }

    def _proxy_aurocs(self, cal_outputs, cal_labels):
        classes = np.unique(cal_labels)
        lab_all, vac_all, dist_all = [], [], []
        for held in classes:
            pos = cal_labels == held
            neg = ~pos
            if pos.sum() < 2 or neg.sum() < 2:
                continue
            min_dist = cal_outputs["distances"].min(axis=1)
            keep = np.arange(cal_outputs["alpha"].shape[1]) != held
            reduced = cal_outputs["alpha"][:, keep]
            v = 1.0 - (np.where((reduced.sum(axis=1) - reduced.shape[1]) > 1e-6, (reduced.max(axis=1) - 1.0) / (reduced.sum(axis=1) - reduced.shape[1]), 0.0))
            lab_all.append(pos.astype(np.int64))
            dist_all.append(empirical_tail(min_dist[neg], min_dist))
            vac_all.append(empirical_tail(v[neg], v))
        if not lab_all:
            return 0.5, 0.5
        a = np.concatenate(lab_all)
        return roc_auc_score(a, np.concatenate(vac_all)), roc_auc_score(a, np.concatenate(dist_all))
