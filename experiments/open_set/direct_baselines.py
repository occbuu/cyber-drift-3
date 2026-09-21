from __future__ import annotations

import importlib.util
import time
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.preprocessing import KBinsDiscretizer, MaxAbsScaler
from torch.utils.data import DataLoader, TensorDataset

from .specialist_baselines import run_specialist_baseline

ROOT = Path(__file__).resolve().parents[2]
EFC_PURE_PATH = ROOT / "baselines" / "github_clones" / "EFC-package" / "efc" / "tests" / "_base_pure.py"
DIRECT_BASELINE_METHODS = frozenset(
    {"closr", "efc", "renoir_dml", "ori", "docpp", "foss", "cd_zd_srl", "ais_nids", "usfad"}
)


@dataclass
class BaselinePredictions:
    calibration_predictions: np.ndarray
    calibration_scores: np.ndarray
    test_predictions: np.ndarray
    test_scores: np.ndarray
    inference_seconds: float
    parameters: int
    diagnostics: dict[str, float | str] = field(default_factory=dict)


class CLOSRNet(nn.Module):
    def __init__(self, input_dim: int, num_classes: int, hidden_dim: int = 256, embedding_dim: int = 32):
        super().__init__()
        self.num_classes = num_classes
        self.embedding_dim = embedding_dim
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )
        self.projection = nn.Linear(hidden_dim, num_classes * embedding_dim)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        projected = self.projection(self.encoder(inputs))
        projected = projected.reshape(len(inputs), self.num_classes, self.embedding_dim)
        return F.normalize(projected, dim=-1)


def closr_loss(embeddings: torch.Tensor, labels: torch.Tensor, margin: float = 1.0) -> torch.Tensor:
    _, num_classes, _ = embeddings.shape
    class_first = embeddings.transpose(0, 1)
    distances = (1.0 - torch.bmm(class_first, class_first.transpose(1, 2))) / 2.0
    equal_pairs = labels[:, None].eq(labels[None, :])
    losses: list[torch.Tensor] = []
    epsilon = torch.finfo(embeddings.dtype).eps
    for target_class in range(num_classes):
        target_rows = labels[:, None].eq(target_class)
        similar_mask = equal_pairs & target_rows
        dissimilar_mask = (~equal_pairs) & target_rows
        class_distances = distances[target_class]
        similar = class_distances[similar_mask]
        dissimilar = class_distances[dissimilar_mask]
        similar_loss = similar.square().mean() if similar.numel() else embeddings.new_tensor(0.0)
        dissimilar_loss = F.relu(margin - dissimilar).square().mean() if dissimilar.numel() else embeddings.new_tensor(0.0)
        losses.append(0.5 * similar_loss + 0.5 * dissimilar_loss + epsilon * class_distances.mean())
    return torch.stack(losses).mean()


def _tensor_loader(x: np.ndarray, y: np.ndarray, batch_size: int, shuffle: bool) -> DataLoader:
    return DataLoader(
        TensorDataset(torch.from_numpy(x).float(), torch.from_numpy(y).long()),
        batch_size=batch_size,
        shuffle=shuffle,
        drop_last=shuffle and len(x) > batch_size,
    )


@torch.no_grad()
def _closr_embeddings(model: CLOSRNet, x: np.ndarray, device: torch.device, batch_size: int) -> torch.Tensor:
    chunks: list[torch.Tensor] = []
    model.eval()
    for (batch_x,) in DataLoader(TensorDataset(torch.from_numpy(x).float()), batch_size=batch_size):
        chunks.append(model(batch_x.to(device)).cpu())
    return torch.cat(chunks, dim=0)


def run_closr(
    train_x: np.ndarray,
    train_y: np.ndarray,
    calibration_x: np.ndarray,
    test_x: np.ndarray,
    num_classes: int,
    device: torch.device,
    epochs: int,
    batch_size: int,
) -> BaselinePredictions:
    model = CLOSRNet(train_x.shape[1], num_classes).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    contrastive_batch_size = min(batch_size, 256)
    for _ in range(epochs):
        model.train()
        for batch_x, batch_y in _tensor_loader(train_x, train_y, contrastive_batch_size, True):
            optimizer.zero_grad(set_to_none=True)
            loss = closr_loss(model(batch_x.to(device)), batch_y.to(device))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()

    train_embeddings = _closr_embeddings(model, train_x, device, batch_size)
    centroids = []
    for label in range(num_classes):
        class_points = train_embeddings[torch.from_numpy(train_y == label), label]
        centroids.append(F.normalize(class_points.mean(dim=0), dim=0))
    centroids_tensor = torch.stack(centroids)

    def predict(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
        started = time.perf_counter()
        embeddings = _closr_embeddings(model, x, device, batch_size)
        similarities = torch.einsum("ncd,cd->nc", embeddings, centroids_tensor)
        probabilities = F.softmax(similarities, dim=1)
        knownness = torch.sum(similarities.square() * probabilities, dim=1)
        elapsed = time.perf_counter() - started
        return similarities.argmax(dim=1).numpy(), (-knownness).numpy(), elapsed

    calibration_predictions, calibration_scores, _ = predict(calibration_x)
    test_predictions, test_scores, inference_seconds = predict(test_x)
    return BaselinePredictions(
        calibration_predictions=calibration_predictions,
        calibration_scores=calibration_scores,
        test_predictions=test_predictions,
        test_scores=test_scores,
        inference_seconds=inference_seconds,
        parameters=sum(parameter.numel() for parameter in model.parameters()),
    )


def _load_efc_module() -> ModuleType:
    if not EFC_PURE_PATH.exists():
        raise FileNotFoundError(f"Official EFC pure-Python reference not found: {EFC_PURE_PATH}")
    spec = importlib.util.spec_from_file_location("efc_official_pure", EFC_PURE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load EFC reference from {EFC_PURE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PureEFCAdapter:
    def __init__(self, n_bins: int = 3, max_fit_rows_per_class: int = 5000):
        self.n_bins = n_bins
        self.max_fit_rows_per_class = max_fit_rows_per_class
        self.scaler = MaxAbsScaler()
        self.discretizer = KBinsDiscretizer(
            n_bins=n_bins,
            encode="ordinal",
            strategy="quantile",
            quantile_method="averaged_inverted_cdf",
        )
        self.estimators: list[object] = []
        self.cutoffs: np.ndarray | None = None

    def fit(self, x: np.ndarray, y: np.ndarray) -> "PureEFCAdapter":
        module = _load_efc_module()
        base_class = module.BaseEFC
        scaled = self.scaler.fit_transform(x)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=r"Feature .* is constant and will be replaced with 0\.")
            warnings.filterwarnings("ignore", message=r"Bins whose width are too small.*")
            discrete = self.discretizer.fit_transform(scaled).astype(np.int64)
        max_bin = int(discrete.max()) + 1
        rng = np.random.default_rng(13)
        self.estimators = []
        cutoffs: list[float] = []
        for label in np.unique(y):
            class_rows = discrete[y == label]
            if len(class_rows) > self.max_fit_rows_per_class:
                selected = rng.choice(len(class_rows), self.max_fit_rows_per_class, replace=False)
                class_rows = class_rows[selected]
            estimator = base_class(max_bin=max_bin, pseudocounts=0.5, cutoff_quantile=0.95)
            try:
                estimator.fit(class_rows)
            except np.linalg.LinAlgError:
                original_inverse = np.linalg.inv
                np.linalg.inv = np.linalg.pinv
                try:
                    estimator.fit(class_rows)
                finally:
                    np.linalg.inv = original_inverse
            self.estimators.append(estimator)
            cutoffs.append(float(estimator.cutoff_))
        self.cutoffs = np.asarray(cutoffs)
        return self

    def predict_scores(self, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        if not self.estimators or self.cutoffs is None:
            raise RuntimeError("EFC adapter is not fitted")
        discrete = self.discretizer.transform(self.scaler.transform(x)).astype(np.int64)
        energies = np.stack([estimator._compute_energy(discrete) for estimator in self.estimators], axis=1)
        predictions = energies.argmin(axis=1)
        selected_energies = energies[np.arange(len(energies)), predictions]
        scores = selected_energies - self.cutoffs[predictions]
        return predictions.astype(np.int64), scores.astype(np.float64)


def run_efc(
    train_x: np.ndarray,
    train_y: np.ndarray,
    calibration_x: np.ndarray,
    test_x: np.ndarray,
) -> BaselinePredictions:
    model = PureEFCAdapter().fit(train_x, train_y)
    calibration_predictions, calibration_scores = model.predict_scores(calibration_x)
    started = time.perf_counter()
    test_predictions, test_scores = model.predict_scores(test_x)
    inference_seconds = time.perf_counter() - started
    return BaselinePredictions(
        calibration_predictions=calibration_predictions,
        calibration_scores=calibration_scores,
        test_predictions=test_predictions,
        test_scores=test_scores,
        inference_seconds=inference_seconds,
        parameters=0,
    )


class RenoirNet(nn.Module):
    def __init__(self, input_dim: int, num_classes: int, hidden_dim: int = 256, embedding_dim: int = 64):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, embedding_dim),
        )
        self.decoder = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
        )
        self.classifier = nn.Linear(embedding_dim, num_classes)

    def forward(self, inputs: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        embeddings = self.encoder(inputs)
        reconstruction = self.decoder(embeddings)
        logits = self.classifier(embeddings)
        return logits, embeddings, reconstruction


def batch_hard_triplet_loss(embeddings: torch.Tensor, labels: torch.Tensor, margin: float = 1.0) -> torch.Tensor:
    distances = torch.cdist(embeddings, embeddings)
    same_class = labels[:, None].eq(labels[None, :])
    same_class.fill_diagonal_(False)
    different_class = ~labels[:, None].eq(labels[None, :])
    hardest_positive = distances.masked_fill(~same_class, float("-inf")).max(dim=1).values
    hardest_negative = distances.masked_fill(~different_class, float("inf")).min(dim=1).values
    valid = torch.isfinite(hardest_positive) & torch.isfinite(hardest_negative)
    if not torch.any(valid):
        return embeddings.new_tensor(0.0)
    return F.relu(hardest_positive[valid] - hardest_negative[valid] + margin).mean()


@torch.no_grad()
def _renoir_embeddings(
    model: RenoirNet,
    x: np.ndarray,
    device: torch.device,
    batch_size: int,
) -> torch.Tensor:
    chunks: list[torch.Tensor] = []
    model.eval()
    for (batch_x,) in DataLoader(TensorDataset(torch.from_numpy(x).float()), batch_size=batch_size):
        _, embeddings, _ = model(batch_x.to(device))
        chunks.append(embeddings.cpu())
    return torch.cat(chunks, dim=0)


def run_renoir(
    train_x: np.ndarray,
    train_y: np.ndarray,
    calibration_x: np.ndarray,
    test_x: np.ndarray,
    num_classes: int,
    device: torch.device,
    epochs: int,
    batch_size: int,
) -> BaselinePredictions:
    model = RenoirNet(train_x.shape[1], num_classes).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    metric_batch_size = min(batch_size, 256)
    for _ in range(epochs):
        model.train()
        for batch_x, batch_y in _tensor_loader(train_x, train_y, metric_batch_size, True):
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)
            optimizer.zero_grad(set_to_none=True)
            logits, embeddings, reconstruction = model(batch_x)
            classification = F.cross_entropy(logits, batch_y)
            reconstruction_loss = F.mse_loss(reconstruction, batch_x)
            metric_loss = batch_hard_triplet_loss(F.normalize(embeddings, dim=1), batch_y)
            loss = classification + 0.2 * reconstruction_loss + 0.5 * metric_loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()

    train_embeddings = F.normalize(_renoir_embeddings(model, train_x, device, batch_size), dim=1)
    centroids = torch.stack(
        [F.normalize(train_embeddings[torch.from_numpy(train_y == label)].mean(dim=0), dim=0) for label in range(num_classes)]
    )

    def predict(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
        started = time.perf_counter()
        embeddings = F.normalize(_renoir_embeddings(model, x, device, batch_size), dim=1)
        distances = torch.cdist(embeddings, centroids)
        elapsed = time.perf_counter() - started
        return distances.argmin(dim=1).numpy(), distances.min(dim=1).values.numpy(), elapsed

    calibration_predictions, calibration_scores, _ = predict(calibration_x)
    test_predictions, test_scores, inference_seconds = predict(test_x)
    return BaselinePredictions(
        calibration_predictions=calibration_predictions,
        calibration_scores=calibration_scores,
        test_predictions=test_predictions,
        test_scores=test_scores,
        inference_seconds=inference_seconds,
        parameters=sum(parameter.numel() for parameter in model.parameters()),
    )


def run_direct_baseline(
    method: str,
    train_x: np.ndarray,
    train_y: np.ndarray,
    calibration_x: np.ndarray,
    calibration_y: np.ndarray,
    test_x: np.ndarray,
    num_classes: int,
    device: torch.device,
    epochs: int,
    batch_size: int,
    seed: int,
) -> BaselinePredictions:
    if method == "closr":
        return run_closr(train_x, train_y, calibration_x, test_x, num_classes, device, epochs, batch_size)
    if method == "efc":
        return run_efc(train_x, train_y, calibration_x, test_x)
    if method == "renoir_dml":
        return run_renoir(train_x, train_y, calibration_x, test_x, num_classes, device, epochs, batch_size)
    if method in DIRECT_BASELINE_METHODS:
        return run_specialist_baseline(
            method,
            train_x,
            train_y,
            calibration_x,
            calibration_y,
            test_x,
            num_classes,
            device,
            epochs,
            batch_size,
            seed,
        )
    raise KeyError(f"No executable direct baseline adapter registered for {method}")
