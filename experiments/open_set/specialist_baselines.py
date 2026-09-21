from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.ensemble import ExtraTreesClassifier, IsolationForest
from sklearn.feature_selection import mutual_info_classif
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import QuantileTransformer
from torch.utils.data import DataLoader, TensorDataset


@dataclass
class SpecialistPredictions:
    calibration_predictions: np.ndarray
    calibration_scores: np.ndarray
    test_predictions: np.ndarray
    test_scores: np.ndarray
    inference_seconds: float
    parameters: int
    diagnostics: dict[str, float | str]


def _loader(x: np.ndarray, y: np.ndarray, batch_size: int, shuffle: bool) -> DataLoader:
    return DataLoader(
        TensorDataset(torch.from_numpy(x).float(), torch.from_numpy(y).long()),
        batch_size=batch_size,
        shuffle=shuffle,
        drop_last=shuffle and len(x) > batch_size,
    )


def _empirical(reference: np.ndarray, values: np.ndarray) -> np.ndarray:
    sorted_reference = np.sort(np.asarray(reference, dtype=np.float64))
    return np.searchsorted(sorted_reference, values, side="right") / (len(sorted_reference) + 1.0)


def _balanced_indices(labels: np.ndarray, maximum: int, seed: int = 13) -> np.ndarray:
    if len(labels) <= maximum:
        return np.arange(len(labels))
    rng = np.random.default_rng(seed)
    classes = np.unique(labels)
    per_class = max(1, maximum // len(classes))
    selected = [
        rng.choice(indices, min(per_class, len(indices)), replace=False)
        for label in classes
        for indices in [np.flatnonzero(labels == label)]
    ]
    result = np.concatenate(selected)
    if len(result) < maximum:
        remaining = np.setdiff1d(np.arange(len(labels)), result, assume_unique=False)
        result = np.concatenate(
            [result, rng.choice(remaining, min(maximum - len(result), len(remaining)), replace=False)]
        )
    rng.shuffle(result)
    return result


def _tree_parameters(model: ExtraTreesClassifier | IsolationForest) -> int:
    return int(sum(estimator.tree_.node_count for estimator in model.estimators_))


def _fit_closed_forest(train_x: np.ndarray, train_y: np.ndarray, seed: int) -> ExtraTreesClassifier:
    model = ExtraTreesClassifier(
        n_estimators=160,
        max_depth=24,
        min_samples_leaf=2,
        class_weight="balanced",
        max_features="sqrt",
        n_jobs=-1,
        random_state=seed,
    )
    model.fit(train_x, train_y)
    return model


def _fit_isolation(train_x: np.ndarray, seed: int) -> IsolationForest:
    model = IsolationForest(
        n_estimators=200,
        max_samples=min(4096, len(train_x)),
        contamination="auto",
        n_jobs=-1,
        random_state=seed,
    )
    model.fit(train_x)
    return model


def _forest_predict(
    classifier: ExtraTreesClassifier,
    x: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    probabilities = classifier.predict_proba(x)
    return probabilities.argmax(axis=1).astype(np.int64), 1.0 - probabilities.max(axis=1)


class DOCPlusPlusNet(nn.Module):
    def __init__(self, input_dim: int, num_classes: int):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, num_classes),
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.network(inputs)


@torch.no_grad()
def _doc_outputs(
    model: DOCPlusPlusNet,
    x: np.ndarray,
    device: torch.device,
    batch_size: int,
) -> tuple[np.ndarray, np.ndarray]:
    logits: list[torch.Tensor] = []
    model.eval()
    for (batch_x,) in DataLoader(TensorDataset(torch.from_numpy(x).float()), batch_size=batch_size):
        logits.append(model(batch_x.to(device)).cpu())
    probabilities = torch.sigmoid(torch.cat(logits, dim=0)).numpy()
    return probabilities.argmax(axis=1).astype(np.int64), 1.0 - probabilities.max(axis=1)


def run_docpp(
    train_x: np.ndarray,
    train_y: np.ndarray,
    calibration_x: np.ndarray,
    test_x: np.ndarray,
    num_classes: int,
    device: torch.device,
    epochs: int,
    batch_size: int,
    seed: int,
) -> SpecialistPredictions:
    model = DOCPlusPlusNet(train_x.shape[1], num_classes).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    rng = np.random.default_rng(seed)
    for _ in range(epochs):
        model.train()
        for batch_x, batch_y in _loader(train_x, train_y, min(batch_size, 256), True):
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)
            optimizer.zero_grad(set_to_none=True)
            logits = model(batch_x)
            targets = F.one_hot(batch_y, num_classes=num_classes).float()
            known_loss = F.binary_cross_entropy_with_logits(logits, targets)
            if len(batch_x) > 1:
                permutation = torch.from_numpy(rng.permutation(len(batch_x))).to(device)
                different = batch_y != batch_y[permutation]
                if torch.any(different):
                    mix = 0.5 * batch_x[different] + 0.5 * batch_x[permutation[different]]
                    exposure_loss = F.binary_cross_entropy_with_logits(
                        model(mix), torch.zeros((len(mix), num_classes), device=device)
                    )
                else:
                    exposure_loss = logits.new_tensor(0.0)
            else:
                exposure_loss = logits.new_tensor(0.0)
            loss = known_loss + 0.15 * exposure_loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()

    calibration_predictions, calibration_scores = _doc_outputs(model, calibration_x, device, batch_size)
    started = time.perf_counter()
    test_predictions, test_scores = _doc_outputs(model, test_x, device, batch_size)
    elapsed = time.perf_counter() - started
    return SpecialistPredictions(
        calibration_predictions,
        calibration_scores,
        test_predictions,
        test_scores,
        elapsed,
        sum(parameter.numel() for parameter in model.parameters()),
        {
            "adapter_provenance": "source_derived_v7_adapter",
            "source_algorithm": "DOC++ one-vs-rest sigmoid with known-only synthetic exposure",
        },
    )


def run_ori(
    train_x: np.ndarray,
    train_y: np.ndarray,
    calibration_x: np.ndarray,
    test_x: np.ndarray,
    seed: int,
) -> SpecialistPredictions:
    classifier = _fit_closed_forest(train_x, train_y, seed)
    reference_indices = _balanced_indices(train_y, 50000, seed)
    neighbors = NearestNeighbors(n_neighbors=min(15, len(reference_indices)), n_jobs=-1).fit(
        train_x[reference_indices]
    )

    def components(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        predictions, confidence_score = _forest_predict(classifier, x)
        density_score = neighbors.kneighbors(x, return_distance=True)[0].mean(axis=1)
        return predictions, confidence_score, density_score

    calibration_predictions, calibration_confidence, calibration_density = components(calibration_x)
    started = time.perf_counter()
    test_predictions, test_confidence, test_density = components(test_x)
    elapsed = time.perf_counter() - started
    calibration_scores = 0.5 * _empirical(calibration_confidence, calibration_confidence) + 0.5 * _empirical(
        calibration_density, calibration_density
    )
    test_scores = 0.5 * _empirical(calibration_confidence, test_confidence) + 0.5 * _empirical(
        calibration_density, test_density
    )
    return SpecialistPredictions(
        calibration_predictions,
        calibration_scores,
        test_predictions,
        test_scores,
        elapsed,
        _tree_parameters(classifier),
        {
            "adapter_provenance": "paper_reimplementation",
            "source_algorithm": "open recognition plus local-density inspection",
        },
    )


def run_foss(
    train_x: np.ndarray,
    train_y: np.ndarray,
    calibration_x: np.ndarray,
    test_x: np.ndarray,
    seed: int,
) -> SpecialistPredictions:
    selection_indices = _balanced_indices(train_y, 50000, seed)
    information = mutual_info_classif(
        train_x[selection_indices], train_y[selection_indices], discrete_features=False, random_state=seed
    )
    selected_count = min(train_x.shape[1], max(8, int(np.ceil(np.sqrt(train_x.shape[1]) * 2))))
    selected_features = np.argsort(information)[-selected_count:]
    selected_train = train_x[:, selected_features]
    selected_calibration = calibration_x[:, selected_features]
    selected_test = test_x[:, selected_features]
    classifier = _fit_closed_forest(selected_train, train_y, seed)
    detector = _fit_isolation(selected_train, seed + 1)

    calibration_predictions, calibration_confidence = _forest_predict(classifier, selected_calibration)
    calibration_partition = -detector.decision_function(selected_calibration)
    started = time.perf_counter()
    test_predictions, test_confidence = _forest_predict(classifier, selected_test)
    test_partition = -detector.decision_function(selected_test)
    elapsed = time.perf_counter() - started
    calibration_scores = 0.35 * _empirical(calibration_confidence, calibration_confidence) + 0.65 * _empirical(
        calibration_partition, calibration_partition
    )
    test_scores = 0.35 * _empirical(calibration_confidence, test_confidence) + 0.65 * _empirical(
        calibration_partition, test_partition
    )
    return SpecialistPredictions(
        calibration_predictions,
        calibration_scores,
        test_predictions,
        test_scores,
        elapsed,
        _tree_parameters(classifier) + _tree_parameters(detector),
        {
            "adapter_provenance": "source_derived_v7_adapter",
            "source_algorithm": "weighted-information features plus random-partition forest",
            "selected_features": float(selected_count),
        },
    )


class SiamesePolicyNet(nn.Module):
    def __init__(self, input_dim: int, num_classes: int):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Linear(128, 32),
        )
        self.classifier = nn.Linear(32, num_classes)

    def forward(self, inputs: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        embeddings = F.normalize(self.encoder(inputs), dim=1)
        return self.classifier(embeddings), embeddings


def _batch_hard(embeddings: torch.Tensor, labels: torch.Tensor, margin: float = 0.5) -> torch.Tensor:
    distances = torch.cdist(embeddings, embeddings)
    same = labels[:, None].eq(labels[None, :])
    same.fill_diagonal_(False)
    different = ~labels[:, None].eq(labels[None, :])
    positives = distances.masked_fill(~same, float("-inf")).max(dim=1).values
    negatives = distances.masked_fill(~different, float("inf")).min(dim=1).values
    valid = torch.isfinite(positives) & torch.isfinite(negatives)
    return F.relu(positives[valid] - negatives[valid] + margin).mean() if torch.any(valid) else distances.new_tensor(0.0)


@torch.no_grad()
def _siamese_outputs(
    model: SiamesePolicyNet,
    x: np.ndarray,
    device: torch.device,
    batch_size: int,
) -> tuple[np.ndarray, np.ndarray]:
    logits: list[torch.Tensor] = []
    embeddings: list[torch.Tensor] = []
    model.eval()
    for (batch_x,) in DataLoader(TensorDataset(torch.from_numpy(x).float()), batch_size=batch_size):
        batch_logits, batch_embeddings = model(batch_x.to(device))
        logits.append(batch_logits.cpu())
        embeddings.append(batch_embeddings.cpu())
    return torch.cat(logits).numpy(), torch.cat(embeddings).numpy()


def run_cd_zd_srl(
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
) -> SpecialistPredictions:
    model = SiamesePolicyNet(train_x.shape[1], num_classes).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    for _ in range(epochs):
        model.train()
        for batch_x, batch_y in _loader(train_x, train_y, min(batch_size, 256), True):
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)
            optimizer.zero_grad(set_to_none=True)
            logits, embeddings = model(batch_x)
            loss = F.cross_entropy(logits, batch_y) + 0.5 * _batch_hard(embeddings, batch_y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()

    _, train_embeddings = _siamese_outputs(model, train_x, device, batch_size)
    calibration_logits, calibration_embeddings = _siamese_outputs(model, calibration_x, device, batch_size)
    centroids = np.stack([train_embeddings[train_y == label].mean(axis=0) for label in range(num_classes)])
    centroid_calibration = np.linalg.norm(calibration_embeddings[:, None, :] - centroids[None, :, :], axis=2).min(axis=1)
    detector = _fit_isolation(train_embeddings, seed)
    isolation_calibration = -detector.decision_function(calibration_embeddings)
    started = time.perf_counter()
    test_logits, test_embeddings = _siamese_outputs(model, test_x, device, batch_size)
    centroid_test = np.linalg.norm(test_embeddings[:, None, :] - centroids[None, :, :], axis=2).min(axis=1)
    isolation_test = -detector.decision_function(test_embeddings)
    elapsed = time.perf_counter() - started
    calibration_centroid_tail = _empirical(centroid_calibration, centroid_calibration)
    calibration_isolation_tail = _empirical(isolation_calibration, isolation_calibration)
    test_centroid_tail = _empirical(centroid_calibration, centroid_test)
    test_isolation_tail = _empirical(isolation_calibration, isolation_test)

    rng = np.random.default_rng(seed)
    proxy_indices = _balanced_indices(train_y, min(4096, len(train_y)), seed=seed)
    permutation = rng.permutation(proxy_indices)
    different = train_y[proxy_indices] != train_y[permutation]
    proxy_x = 0.5 * train_x[proxy_indices[different]] + 0.5 * train_x[permutation[different]]
    if len(proxy_x):
        _, proxy_embeddings = _siamese_outputs(model, proxy_x, device, batch_size)
        proxy_centroid = np.linalg.norm(proxy_embeddings[:, None, :] - centroids[None, :, :], axis=2).min(axis=1)
        proxy_isolation = -detector.decision_function(proxy_embeddings)
        proxy_centroid_tail = _empirical(centroid_calibration, proxy_centroid)
        proxy_isolation_tail = _empirical(isolation_calibration, proxy_isolation)
        labels = np.concatenate([np.zeros(len(calibration_x)), np.ones(len(proxy_x))])
        best_weight = 0.5
        best_auc = -np.inf
        for weight in np.linspace(0.0, 1.0, 11):
            scores = np.concatenate(
                [
                    weight * calibration_centroid_tail + (1.0 - weight) * calibration_isolation_tail,
                    weight * proxy_centroid_tail + (1.0 - weight) * proxy_isolation_tail,
                ]
            )
            auc = roc_auc_score(labels, scores)
            if auc > best_auc:
                best_auc = auc
                best_weight = float(weight)
    else:
        best_weight = 0.5
        best_auc = 0.5

    calibration_scores = best_weight * calibration_centroid_tail + (1.0 - best_weight) * calibration_isolation_tail
    test_scores = best_weight * test_centroid_tail + (1.0 - best_weight) * test_isolation_tail
    return SpecialistPredictions(
        calibration_logits.argmax(axis=1).astype(np.int64),
        calibration_scores,
        test_logits.argmax(axis=1).astype(np.int64),
        test_scores,
        elapsed,
        sum(parameter.numel() for parameter in model.parameters()) + _tree_parameters(detector),
        {
            "adapter_provenance": "paper_reimplementation",
            "source_algorithm": "Siamese metric learning plus adaptive anomaly-score policy",
            "policy_centroid_weight": best_weight,
            "proxy_policy_auroc": float(best_auc),
        },
    )


class IncrementalMemoryNet(nn.Module):
    def __init__(self, input_dim: int, num_classes: int):
        super().__init__()
        self.encoder = nn.Sequential(nn.Linear(input_dim, 96), nn.ReLU(), nn.Linear(96, 24))
        self.decoder = nn.Sequential(nn.Linear(24, 96), nn.ReLU(), nn.Linear(96, input_dim))
        self.classifier = nn.Linear(24, num_classes)

    def forward(self, inputs: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        embedding = self.encoder(inputs)
        return self.classifier(embedding), embedding, self.decoder(embedding)


@torch.no_grad()
def _memory_outputs(
    model: IncrementalMemoryNet,
    x: np.ndarray,
    device: torch.device,
    batch_size: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    logits: list[torch.Tensor] = []
    embeddings: list[torch.Tensor] = []
    reconstruction_error: list[torch.Tensor] = []
    model.eval()
    for (batch_x,) in DataLoader(TensorDataset(torch.from_numpy(x).float()), batch_size=batch_size):
        batch_x = batch_x.to(device)
        batch_logits, batch_embeddings, reconstruction = model(batch_x)
        logits.append(batch_logits.cpu())
        embeddings.append(batch_embeddings.cpu())
        reconstruction_error.append(F.mse_loss(reconstruction, batch_x, reduction="none").mean(dim=1).cpu())
    return torch.cat(logits).numpy(), torch.cat(embeddings).numpy(), torch.cat(reconstruction_error).numpy()


def run_ais_nids(
    train_x: np.ndarray,
    train_y: np.ndarray,
    calibration_x: np.ndarray,
    test_x: np.ndarray,
    num_classes: int,
    device: torch.device,
    epochs: int,
    batch_size: int,
    seed: int,
) -> SpecialistPredictions:
    model = IncrementalMemoryNet(train_x.shape[1], num_classes).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    for _ in range(epochs):
        model.train()
        for batch_x, batch_y in _loader(train_x, train_y, batch_size, True):
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)
            optimizer.zero_grad(set_to_none=True)
            logits, embeddings, reconstruction = model(batch_x)
            compactness = embeddings.var(dim=0).mean()
            loss = F.cross_entropy(logits, batch_y) + 0.25 * F.mse_loss(reconstruction, batch_x) + 0.01 * compactness
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()

    _, train_embeddings, train_reconstruction = _memory_outputs(model, train_x, device, batch_size)
    calibration_logits, calibration_embeddings, calibration_reconstruction = _memory_outputs(
        model, calibration_x, device, batch_size
    )
    centroids = np.stack([train_embeddings[train_y == label].mean(axis=0) for label in range(num_classes)])
    calibration_memory = np.linalg.norm(calibration_embeddings[:, None, :] - centroids[None, :, :], axis=2).min(axis=1)
    started = time.perf_counter()
    test_logits, test_embeddings, test_reconstruction = _memory_outputs(model, test_x, device, batch_size)
    test_memory = np.linalg.norm(test_embeddings[:, None, :] - centroids[None, :, :], axis=2).min(axis=1)
    elapsed = time.perf_counter() - started
    calibration_scores = 0.5 * _empirical(calibration_reconstruction, calibration_reconstruction) + 0.5 * _empirical(
        calibration_memory, calibration_memory
    )
    test_scores = 0.5 * _empirical(calibration_reconstruction, test_reconstruction) + 0.5 * _empirical(
        calibration_memory, test_memory
    )
    return SpecialistPredictions(
        calibration_logits.argmax(axis=1).astype(np.int64),
        calibration_scores,
        test_logits.argmax(axis=1).astype(np.int64),
        test_scores,
        elapsed,
        sum(parameter.numel() for parameter in model.parameters()),
        {
            "adapter_provenance": "paper_reimplementation",
            "source_algorithm": "self-sustaining representation memory with reconstruction novelty",
            "train_reconstruction_mean": float(train_reconstruction.mean()),
        },
    )


def run_usfad(
    train_x: np.ndarray,
    train_y: np.ndarray,
    calibration_x: np.ndarray,
    test_x: np.ndarray,
    seed: int,
) -> SpecialistPredictions:
    quantiles = min(1000, max(10, len(train_x)))
    transformer = QuantileTransformer(
        n_quantiles=quantiles,
        output_distribution="uniform",
        subsample=min(100000, len(train_x)),
        random_state=seed,
    )
    transformed_train = transformer.fit_transform(train_x)
    transformed_calibration = transformer.transform(calibration_x)
    classifier = _fit_closed_forest(transformed_train, train_y, seed)
    detector = _fit_isolation(transformed_train, seed + 1)
    calibration_predictions, _ = _forest_predict(classifier, transformed_calibration)
    calibration_raw = -detector.decision_function(transformed_calibration)
    started = time.perf_counter()
    transformed_test = transformer.transform(test_x)
    test_predictions, _ = _forest_predict(classifier, transformed_test)
    test_raw = -detector.decision_function(transformed_test)
    elapsed = time.perf_counter() - started
    return SpecialistPredictions(
        calibration_predictions,
        _empirical(calibration_raw, calibration_raw),
        test_predictions,
        _empirical(calibration_raw, test_raw),
        elapsed,
        _tree_parameters(classifier) + _tree_parameters(detector),
        {
            "adapter_provenance": "paper_reimplementation",
            "source_algorithm": "unit-scale-robust stochastic isolation forest",
            "quantile_features": float(train_x.shape[1]),
        },
    )


def run_specialist_baseline(
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
) -> SpecialistPredictions:
    if method == "docpp":
        return run_docpp(train_x, train_y, calibration_x, test_x, num_classes, device, epochs, batch_size, seed)
    if method == "ori":
        return run_ori(train_x, train_y, calibration_x, test_x, seed)
    if method == "foss":
        return run_foss(train_x, train_y, calibration_x, test_x, seed)
    if method == "cd_zd_srl":
        return run_cd_zd_srl(
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
    if method == "ais_nids":
        return run_ais_nids(train_x, train_y, calibration_x, test_x, num_classes, device, epochs, batch_size, seed)
    if method == "usfad":
        return run_usfad(train_x, train_y, calibration_x, test_x, seed)
    raise KeyError(f"No specialist baseline adapter registered for {method}")
