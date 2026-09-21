from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

import geoopt
import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

from .data import (
    cap_open_set_data,
    derive_multi_unknown,
    encode_known_labels,
    load_rotation,
    source_fitted_cross_domain,
    source_fitted_leave_one_domain_out,
)
from .direct_baselines import DIRECT_BASELINE_METHODS, run_direct_baseline
from .metrics import evaluate_open_set, known_only_metrics
from .models import DEFAULT_PROFILE, PROFILES, HyperbolicEvidentialModel, TabularBackbone, hedl_loss
from .conformal import COMPONENT_NAMES, ConformalFusionScorer
from .scorers import PrototypeDistanceScorer, KnownOnlyHEDLScorer, MahalanobisScorer, OpenMaxScorer, energy, msp, odin


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    if torch.backends.cudnn.is_available():
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True


def loader(x: np.ndarray, y: np.ndarray, batch_size: int, shuffle: bool) -> DataLoader:
    return DataLoader(
        TensorDataset(torch.from_numpy(x).float(), torch.from_numpy(y).long()),
        batch_size=batch_size,
        shuffle=shuffle,
        drop_last=shuffle and len(x) >= batch_size,
    )


def train_backbone(
    x: np.ndarray,
    y: np.ndarray,
    num_classes: int,
    device: torch.device,
    epochs: int,
    batch_size: int,
) -> TabularBackbone:
    model = TabularBackbone(x.shape[1], num_classes).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    for _ in range(epochs):
        model.train()
        for batch_x, batch_y in loader(x, y, batch_size, True):
            optimizer.zero_grad(set_to_none=True)
            logits, _ = model(batch_x.to(device))
            loss = F.cross_entropy(logits, batch_y.to(device))
            loss.backward()
            optimizer.step()
    return model


def infer_backbone(
    model: TabularBackbone,
    x: np.ndarray,
    device: torch.device,
    batch_size: int,
    with_odin: bool = False,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray | None, float]:
    logits_list: list[np.ndarray] = []
    features_list: list[np.ndarray] = []
    odin_list: list[np.ndarray] = []
    model.eval()
    started = time.perf_counter()
    for (batch_x,) in DataLoader(TensorDataset(torch.from_numpy(x).float()), batch_size=batch_size):
        batch_x = batch_x.to(device)
        with torch.no_grad():
            logits, features = model(batch_x)
        logits_list.append(logits.cpu().numpy())
        features_list.append(features.cpu().numpy())
        if with_odin:
            odin_list.append(odin(model, batch_x))
    logits_array = np.concatenate(logits_list)
    features_array = np.concatenate(features_list)
    predictions = logits_array.argmax(axis=1)
    elapsed = time.perf_counter() - started
    return logits_array, features_array, predictions, np.concatenate(odin_list) if with_odin else None, elapsed


def train_hedl(
    x: np.ndarray,
    y: np.ndarray,
    num_classes: int,
    device: torch.device,
    epochs: int,
    batch_size: int,
    profile: str = DEFAULT_PROFILE,
    curvature: float = 0.5,
    evidential_weight: float = 1.0,
    margin_weight: float = 1.0,
) -> HyperbolicEvidentialModel:
    model = HyperbolicEvidentialModel.build(x, num_classes, profile=profile, curvature=curvature).to(device)
    optimizer = geoopt.optim.RiemannianAdam(model.parameters(), lr=2e-3, weight_decay=1e-4)
    steps_per_epoch = max(1, len(x) // batch_size)
    total_steps = epochs * steps_per_epoch
    warmup_steps = min(steps_per_epoch * 3, total_steps // 5)
    def lr_lambda(step):
        if step < warmup_steps:
            return max(0.1, step / max(1, warmup_steps))
        progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
        return max(0.01, 0.5 * (1.0 + __import__('math').cos(__import__('math').pi * progress)))
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)
    counts = np.bincount(y, minlength=num_classes).astype(np.float64)
    class_weights = np.sqrt(counts.max() / np.maximum(counts, 1.0))
    class_weights = np.clip(class_weights, 1.0, 4.0)
    class_weights = torch.from_numpy((class_weights / class_weights.mean()).astype(np.float32)).to(device)
    for epoch in range(1, epochs + 1):
        model.train()
        for batch_x, batch_y in loader(x, y, batch_size, True):
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)
            optimizer.zero_grad(set_to_none=True)
            outputs = model(batch_x)
            loss = hedl_loss(outputs, batch_y, epoch, class_weights=class_weights,
                             evidential_weight=evidential_weight, margin_weight=margin_weight)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 3.0)
            optimizer.step()
            scheduler.step()
    return model


def infer_hedl(
    model: HyperbolicEvidentialModel,
    x: np.ndarray,
    device: torch.device,
    batch_size: int,
) -> tuple[np.ndarray, dict[str, np.ndarray], float]:
    predictions: list[np.ndarray] = []
    collected: dict[str, list[np.ndarray]] = {
        "alpha": [],
        "vacuity": [],
        "embedding": [],
        "distances": [],
        "tangent": [],
    }
    model.eval()
    started = time.perf_counter()
    with torch.no_grad():
        for (batch_x,) in DataLoader(TensorDataset(torch.from_numpy(x).float()), batch_size=batch_size):
            outputs = model(batch_x.to(device))
            predictions.append(outputs["logits"].argmax(dim=1).cpu().numpy())
            for name in collected:
                collected[name].append(outputs[name].cpu().numpy())
    return (
        np.concatenate(predictions),
        {name: np.concatenate(values) for name, values in collected.items()},
        time.perf_counter() - started,
    )


def fit_and_infer_hedl(
    train_x: np.ndarray,
    train_y: np.ndarray,
    calibration_x: np.ndarray,
    calibration_y: np.ndarray,
    test_x: np.ndarray,
    num_classes: int,
    device: torch.device,
    epochs: int,
    batch_size: int,
    profile: str = DEFAULT_PROFILE,
    scorer_components: tuple[str, ...] = COMPONENT_NAMES,
    curvature: float = 0.5,
    tail_extension: bool = False,
    tail_anchor_exceedances: int = 250,
    tail_confidence: float = 0.0,
    evidential_weight: float = 1.0,
    margin_weight: float = 1.0,
) -> tuple[HyperbolicEvidentialModel, np.ndarray, np.ndarray, np.ndarray, float, dict[str, float | str]]:
    model = train_hedl(train_x, train_y, num_classes, device, epochs, batch_size, profile, curvature,
                       evidential_weight, margin_weight)
    _, train_outputs, _ = infer_hedl(model, train_x, device, batch_size)
    _, calibration_outputs, _ = infer_hedl(model, calibration_x, device, batch_size)
    scorer = ConformalFusionScorer(
        components=scorer_components,
        tail_extension=tail_extension,
        tail_anchor_exceedances=tail_anchor_exceedances,
        tail_confidence=tail_confidence,
    ).fit(
        train_outputs,
        train_y,
        calibration_outputs,
        calibration_y,
    )
    if tail_extension:
        # The device-resident scorer reproduces the floored p-values only, so a
        # tail-extended run stays on the reference NumPy path.  This costs
        # latency, which is why the latency benchmark never switches it on.
        _, calibration_outputs_again, _ = infer_hedl(model, calibration_x, device, batch_size)
        test_predictions, test_outputs, inference_seconds = infer_hedl(
            model, test_x, device, batch_size
        )
        calibration_scores = scorer.score(calibration_outputs_again)
        test_scores = scorer.score(test_outputs)
        return (
            model,
            calibration_scores,
            test_predictions,
            test_scores,
            inference_seconds,
            scorer.diagnostics(),
        )
    deployed = scorer.to_torch(device)
    _, calibration_scores, _ = deploy_hedl(model, deployed, calibration_x, device, batch_size)
    test_predictions, test_scores, inference_seconds = deploy_hedl(model, deployed, test_x, device, batch_size)
    return model, calibration_scores, test_predictions, test_scores, inference_seconds, scorer.diagnostics()


@torch.no_grad()
def deploy_hedl(
    model: HyperbolicEvidentialModel,
    scorer,
    x: np.ndarray,
    device: torch.device,
    batch_size: int,
) -> tuple[np.ndarray, np.ndarray, float]:
    """The timed inference path: encoder, predicted class and zero-day score, all on
    ``device``, one host transfer per batch.  Returns (predictions, scores, seconds)."""
    model.eval()
    predictions: list[torch.Tensor] = []
    scores: list[torch.Tensor] = []
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    started = time.perf_counter()
    for (batch_x,) in DataLoader(TensorDataset(torch.from_numpy(x).float()), batch_size=batch_size):
        tangent, predicted = model.predict_fast(batch_x.to(device))
        predictions.append(predicted.cpu())
        scores.append(scorer.score(tangent).cpu())
    elapsed = time.perf_counter() - started
    return (
        torch.cat(predictions).numpy(),
        torch.cat(scores).double().numpy(),
        elapsed,
    )


def calibration_threshold(scores: np.ndarray, false_positive_budget: float = 0.01) -> float:
    return float(np.quantile(scores, 1.0 - false_positive_budget))


def deployment_threshold(
    calibration_scores: np.ndarray,
    test_scores: np.ndarray,
    false_positive_budget: float = 0.01,
    minimum_accepted: float = 0.2,
) -> tuple[float, dict[str, float | str]]:
    """Rejection threshold that refuses to flood the operator with alarms.

    The calibrated threshold is the (1 - budget) quantile of the calibration
    scores, and it controls the false-alarm rate only while the calibration split
    stays exchangeable with the traffic being scored.  Under a domain change that
    assumption breaks: every flow of the new network looks unfamiliar, the whole
    batch lands above the threshold, and the detector alarms on ~90% of traffic
    instead of the budgeted 1%.

    The share of the batch that falls *below* the calibrated threshold is a
    label-free check on that assumption.  A live network in which the detector
    accepts almost nothing is far more likely to be mis-calibrated than to be
    almost entirely malicious, so when that share drops under ``minimum_accepted``
    the calibrated threshold is declared invalid and the alarm budget is applied
    to the batch itself instead.  Detection quality cannot be recovered this way --
    a score with no ranking signal stays useless -- but the failure becomes a
    reported, bounded one rather than an alarm flood.

    The reported mode makes the fallback auditable; it must never be silent.

    Returns the threshold and a diagnostics dict.  The same policy is applied to
    every method, so comparisons stay fair.
    """
    calibrated = calibration_threshold(calibration_scores, false_positive_budget)
    accepted = float(np.mean(np.asarray(test_scores) < calibrated))
    if accepted >= minimum_accepted:
        return calibrated, {
            "threshold_mode": "calibrated",
            "threshold_accepted_fraction": accepted,
            "threshold_value": calibrated,
        }
    fallback = calibration_threshold(test_scores, false_positive_budget)
    return fallback, {
        "threshold_mode": "alarm_budget_fallback",
        "threshold_accepted_fraction": accepted,
        "threshold_value": fallback,
    }


def evaluate_with_budget(
    labels: np.ndarray,
    predictions: np.ndarray,
    test_scores: np.ndarray,
    calibration_scores: np.ndarray,
) -> dict[str, float | str]:
    """Open-set metrics under the deployment threshold policy."""
    threshold, diagnostics = deployment_threshold(calibration_scores, test_scores)
    metrics: dict[str, float | str] = evaluate_open_set(labels, predictions, test_scores, threshold)
    metrics.update(diagnostics)
    return metrics


def evaluate_partition(
    dataset: str,
    scenario: str,
    protocol_group: str,
    protocol: str,
    methods: list[str],
    seed: int,
    epochs: int,
    batch_size: int,
    max_rows: int | None = None,
    additional_unknown: list[str] | None = None,
    profile: str = DEFAULT_PROFILE,
    scorer_components: tuple[str, ...] = COMPONENT_NAMES,
    curvature: float = 0.5,
) -> dict[str, dict[str, float]]:
    raw = load_rotation(dataset, scenario)
    if protocol_group == "shift" and protocol == "difficulty" and additional_unknown:
        raw = derive_multi_unknown(raw, additional_unknown)
    raw = cap_open_set_data(raw, max_rows, seed)
    data, _ = encode_known_labels(raw)
    train_mask = data.train.y >= 0
    calibration_mask = data.calibration.y >= 0
    num_classes = len(data.known_families)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    results: dict[str, dict[str, float]] = {}
    closed_reference_macro_f1: float | None = None
    if protocol_group == "loao":
        reference_backbone = train_backbone(
            data.train.x[train_mask],
            data.train.y[train_mask],
            num_classes,
            device,
            min(10, epochs),
            batch_size,
        )
        _, _, reference_predictions, _, _ = infer_backbone(
            reference_backbone,
            data.test.x[data.known_test_mask],
            device,
            batch_size,
        )
        closed_reference_macro_f1 = known_only_metrics(
            data.test.y[data.known_test_mask], reference_predictions
        )["known_macro_f1"]

    def evaluate_scores(
        predictions: np.ndarray,
        test_scores: np.ndarray,
        calibration_scores: np.ndarray,
    ) -> dict[str, float | dict[str, dict[str, float]]]:
        threshold, threshold_diagnostics = deployment_threshold(calibration_scores, test_scores)
        metrics: dict[str, float | dict[str, dict[str, float]]] = evaluate_open_set(
            data.test.y,
            predictions,
            test_scores,
            threshold,
        )
        metrics.update(threshold_diagnostics)
        if protocol_group == "prevalence":
            metrics["prevalence"] = {
                str(prevalence): prevalence_metrics(
                    data.test.y,
                    predictions,
                    test_scores,
                    threshold,
                    prevalence,
                    seed,
                )
                for prevalence in (0.5, 0.25, 0.1, 0.05, 0.01, 0.001)
            }
        return metrics

    posthoc = set(methods).intersection({"closed_backbone", "msp", "energy", "odin", "mahalanobis", "openmax"})
    if posthoc:
        backbone = train_backbone(
            data.train.x[train_mask], data.train.y[train_mask], num_classes, device, epochs, batch_size
        )
        train_logits, train_features, train_predictions, _, _ = infer_backbone(
            backbone, data.train.x[train_mask], device, batch_size
        )
        cal_logits, cal_features, cal_predictions, cal_odin, _ = infer_backbone(
            backbone, data.calibration.x[calibration_mask], device, batch_size, with_odin="odin" in posthoc
        )
        test_logits, test_features, test_predictions, test_odin, backbone_seconds = infer_backbone(
            backbone, data.test.x, device, batch_size, with_odin="odin" in posthoc
        )
        if "closed_backbone" in posthoc:
            mask = data.known_test_mask
            results["closed_backbone"] = known_only_metrics(data.test.y[mask], test_predictions[mask])
        if "msp" in posthoc:
            cal_scores = msp(torch.from_numpy(cal_logits))
            test_scores = msp(torch.from_numpy(test_logits))
            results["msp"] = evaluate_scores(test_predictions, test_scores, cal_scores)
        if "energy" in posthoc:
            cal_scores = energy(torch.from_numpy(cal_logits))
            test_scores = energy(torch.from_numpy(test_logits))
            results["energy"] = evaluate_scores(test_predictions, test_scores, cal_scores)
        if "odin" in posthoc and cal_odin is not None and test_odin is not None:
            results["odin"] = evaluate_scores(test_predictions, test_odin, cal_odin)
        if "mahalanobis" in posthoc:
            scorer = MahalanobisScorer().fit(train_features, data.train.y[train_mask])
            cal_scores = scorer.score(cal_features)
            test_scores = scorer.score(test_features)
            results["mahalanobis"] = evaluate_scores(test_predictions, test_scores, cal_scores)
        if "openmax" in posthoc:
            scorer = OpenMaxScorer().fit(train_logits, data.train.y[train_mask], train_predictions)
            cal_scores = scorer.score(cal_logits)
            test_scores = scorer.score(test_logits)
            results["openmax"] = evaluate_scores(test_predictions, test_scores, cal_scores)

        if protocol_group == "prevalence":
            for method in posthoc.difference({"closed_backbone"}):
                if method in results:
                    results[method]["latency_ms_per_flow"] = 1000.0 * backbone_seconds / len(data.test.x)
                    results[method]["throughput_fps"] = len(data.test.x) / max(backbone_seconds, 1e-12)
                    results[method]["parameters"] = float(sum(parameter.numel() for parameter in backbone.parameters()))

    for method in sorted(set(methods).intersection(DIRECT_BASELINE_METHODS)):
        output = run_direct_baseline(
            method=method,
            train_x=data.train.x[train_mask],
            train_y=data.train.y[train_mask],
            calibration_x=data.calibration.x[calibration_mask],
            calibration_y=data.calibration.y[calibration_mask],
            test_x=data.test.x,
            num_classes=num_classes,
            device=device,
            epochs=epochs,
            batch_size=batch_size,
            seed=seed,
        )
        results[method] = evaluate_scores(output.test_predictions, output.test_scores, output.calibration_scores)
        results[method].update(
            {key if key.startswith("adapter_") else f"adapter_{key}": value for key, value in output.diagnostics.items()}
        )
        if protocol_group == "prevalence":
            results[method]["latency_ms_per_flow"] = 1000.0 * output.inference_seconds / len(data.test.x)
            results[method]["throughput_fps"] = len(data.test.x) / max(output.inference_seconds, 1e-12)
            results[method]["parameters"] = float(output.parameters)

    if "hedl" in methods:
        model, cal_scores, test_predictions, test_scores, hedl_seconds, diagnostics = fit_and_infer_hedl(
            data.train.x[train_mask],
            data.train.y[train_mask],
            data.calibration.x[calibration_mask],
            data.calibration.y[calibration_mask],
            data.test.x,
            num_classes,
            device,
            epochs,
            batch_size,
            profile,
            scorer_components,
            curvature,
        )
        results["hedl"] = evaluate_scores(test_predictions, test_scores, cal_scores)
        results["hedl"].update({f"scorer_{key}": value for key, value in diagnostics.items()})
        if protocol_group == "prevalence":
            results["hedl"]["latency_ms_per_flow"] = 1000.0 * hedl_seconds / len(data.test.x)
            results["hedl"]["throughput_fps"] = len(data.test.x) / max(hedl_seconds, 1e-12)
            results["hedl"]["parameters"] = float(sum(parameter.numel() for parameter in model.parameters()))
            results["hedl"]["state_floats"] = float(model.state_floats())

    if protocol_group == "loao" and closed_reference_macro_f1 is not None:
        for method_results in results.values():
            method_results["delta_f1"] = method_results["known_macro_f1"] - closed_reference_macro_f1
            method_results["closed_reference_macro_f1"] = closed_reference_macro_f1
    return results


def evaluate_cross_domain(
    source_dataset: str,
    target_dataset: str,
    methods: list[str],
    epochs: int,
    batch_size: int,
    max_rows: int | None,
    seed: int,
    profile: str = DEFAULT_PROFILE,
    scorer_components: tuple[str, ...] = COMPONENT_NAMES,
) -> tuple[dict[str, dict[str, float]], tuple[str, ...]]:
    (
        train_x,
        train_y,
        calibration_x,
        calibration_y,
        target_x,
        target_y,
        shared,
    ) = source_fitted_cross_domain(source_dataset, target_dataset, max_rows=max_rows)
    num_classes = len(np.unique(train_y))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    results: dict[str, dict[str, float]] = {}
    posthoc = set(methods).intersection({"msp", "energy", "odin", "mahalanobis", "openmax"})
    if posthoc:
        backbone = train_backbone(train_x, train_y, num_classes, device, epochs, batch_size)
        train_logits, train_features, train_predictions, _, _ = infer_backbone(
            backbone, train_x, device, batch_size
        )
        calibration_logits, calibration_features, _, calibration_odin, _ = infer_backbone(
            backbone, calibration_x, device, batch_size, with_odin="odin" in posthoc
        )
        target_logits, target_features, target_predictions, target_odin, _ = infer_backbone(
            backbone, target_x, device, batch_size, with_odin="odin" in posthoc
        )
        score_pairs: dict[str, tuple[np.ndarray, np.ndarray]] = {}
        if "msp" in posthoc:
            score_pairs["msp"] = (
                msp(torch.from_numpy(calibration_logits)),
                msp(torch.from_numpy(target_logits)),
            )
        if "energy" in posthoc:
            score_pairs["energy"] = (
                energy(torch.from_numpy(calibration_logits)),
                energy(torch.from_numpy(target_logits)),
            )
        if "odin" in posthoc and calibration_odin is not None and target_odin is not None:
            score_pairs["odin"] = (calibration_odin, target_odin)
        if "mahalanobis" in posthoc:
            scorer = MahalanobisScorer().fit(train_features, train_y)
            score_pairs["mahalanobis"] = (scorer.score(calibration_features), scorer.score(target_features))
        if "openmax" in posthoc:
            scorer = OpenMaxScorer().fit(train_logits, train_y, train_predictions)
            score_pairs["openmax"] = (scorer.score(calibration_logits), scorer.score(target_logits))
        for method, (calibration_scores, target_scores) in score_pairs.items():
            results[method] = evaluate_with_budget(
                target_y, target_predictions, target_scores, calibration_scores
            )
    for method in sorted(set(methods).intersection(DIRECT_BASELINE_METHODS)):
        output = run_direct_baseline(
            method=method,
            train_x=train_x,
            train_y=train_y,
            calibration_x=calibration_x,
            calibration_y=calibration_y,
            test_x=target_x,
            num_classes=num_classes,
            device=device,
            epochs=epochs,
            batch_size=batch_size,
            seed=seed,
        )
        results[method] = evaluate_with_budget(
            target_y, output.test_predictions, output.test_scores, output.calibration_scores
        )
        results[method].update(
            {key if key.startswith("adapter_") else f"adapter_{key}": value for key, value in output.diagnostics.items()}
        )
    if "hedl" in methods:
        _, calibration_scores, target_predictions, target_scores, _, diagnostics = fit_and_infer_hedl(
            train_x,
            train_y,
            calibration_x,
            calibration_y,
            target_x,
            num_classes,
            device,
            epochs,
            batch_size,
            profile,
            scorer_components,
        )
        results["hedl"] = evaluate_with_budget(
            target_y, target_predictions, target_scores, calibration_scores
        )
        results["hedl"].update({f"scorer_{key}": value for key, value in diagnostics.items()})
    return results, shared


def evaluate_leave_one_domain_out(
    source_datasets: list[str],
    target_dataset: str,
    methods: list[str],
    epochs: int,
    batch_size: int,
    max_rows: int | None,
    seed: int,
    profile: str = DEFAULT_PROFILE,
    scorer_components: tuple[str, ...] = COMPONENT_NAMES,
) -> tuple[dict[str, dict[str, float]], tuple[str, ...]]:
    (
        train_x,
        train_y,
        calibration_x,
        calibration_y,
        target_x,
        target_y,
        shared,
    ) = source_fitted_leave_one_domain_out(source_datasets, target_dataset, max_rows=max_rows)
    num_classes = len(np.unique(train_y))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    results: dict[str, dict[str, float]] = {}
    posthoc = set(methods).intersection({"msp", "energy", "odin", "mahalanobis", "openmax"})
    if posthoc:
        backbone = train_backbone(train_x, train_y, num_classes, device, epochs, batch_size)
        train_logits, train_features, train_predictions, _, _ = infer_backbone(
            backbone, train_x, device, batch_size
        )
        calibration_logits, calibration_features, _, calibration_odin, _ = infer_backbone(
            backbone, calibration_x, device, batch_size, with_odin="odin" in posthoc
        )
        target_logits, target_features, target_predictions, target_odin, _ = infer_backbone(
            backbone, target_x, device, batch_size, with_odin="odin" in posthoc
        )
        score_pairs: dict[str, tuple[np.ndarray, np.ndarray]] = {}
        if "msp" in posthoc:
            score_pairs["msp"] = (
                msp(torch.from_numpy(calibration_logits)),
                msp(torch.from_numpy(target_logits)),
            )
        if "energy" in posthoc:
            score_pairs["energy"] = (
                energy(torch.from_numpy(calibration_logits)),
                energy(torch.from_numpy(target_logits)),
            )
        if "odin" in posthoc and calibration_odin is not None and target_odin is not None:
            score_pairs["odin"] = (calibration_odin, target_odin)
        if "mahalanobis" in posthoc:
            scorer = MahalanobisScorer().fit(train_features, train_y)
            score_pairs["mahalanobis"] = (
                scorer.score(calibration_features),
                scorer.score(target_features),
            )
        if "openmax" in posthoc:
            scorer = OpenMaxScorer().fit(train_logits, train_y, train_predictions)
            score_pairs["openmax"] = (
                scorer.score(calibration_logits),
                scorer.score(target_logits),
            )
        for method, (calibration_scores, target_scores) in score_pairs.items():
            results[method] = evaluate_with_budget(
                target_y, target_predictions, target_scores, calibration_scores
            )
    for method in sorted(set(methods).intersection(DIRECT_BASELINE_METHODS)):
        output = run_direct_baseline(
            method=method,
            train_x=train_x,
            train_y=train_y,
            calibration_x=calibration_x,
            calibration_y=calibration_y,
            test_x=target_x,
            num_classes=num_classes,
            device=device,
            epochs=epochs,
            batch_size=batch_size,
            seed=seed,
        )
        results[method] = evaluate_with_budget(
            target_y, output.test_predictions, output.test_scores, output.calibration_scores
        )
        results[method].update(
            {key if key.startswith("adapter_") else f"adapter_{key}": value for key, value in output.diagnostics.items()}
        )
    if "hedl" in methods:
        _, calibration_scores, target_predictions, target_scores, _, diagnostics = fit_and_infer_hedl(
            train_x,
            train_y,
            calibration_x,
            calibration_y,
            target_x,
            num_classes,
            device,
            epochs,
            batch_size,
            profile,
            scorer_components,
        )
        results["hedl"] = evaluate_with_budget(
            target_y, target_predictions, target_scores, calibration_scores
        )
        results["hedl"].update({f"scorer_{key}": value for key, value in diagnostics.items()})
    return results, shared


def prevalence_metrics(
    labels: np.ndarray,
    predictions: np.ndarray,
    scores: np.ndarray,
    threshold: float,
    prevalence: float,
    seed: int,
) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    known = np.flatnonzero(labels >= 0)
    unknown = np.flatnonzero(labels < 0)
    if not len(known) or not len(unknown):
        raise ValueError("Prevalence evaluation requires both known and unknown samples")
    if not 0.0 < prevalence < 1.0:
        raise ValueError("Prevalence must be strictly between zero and one")

    available_prevalence = len(unknown) / (len(known) + len(unknown))
    if available_prevalence >= prevalence:
        selected_known = known
        unknown_count = min(
            len(unknown),
            max(1, round(len(selected_known) * prevalence / (1.0 - prevalence))),
        )
        selected_unknown = rng.choice(unknown, unknown_count, replace=False)
    else:
        selected_unknown = unknown
        known_count = min(
            len(known),
            max(1, round(len(selected_unknown) * (1.0 - prevalence) / prevalence)),
        )
        selected_known = rng.choice(known, known_count, replace=False)

    selected = np.concatenate([selected_known, selected_unknown])
    rng.shuffle(selected)
    metrics = evaluate_open_set(labels[selected], predictions[selected], scores[selected], threshold)
    metrics.update(
        {
            "requested_prevalence": float(prevalence),
            "realized_prevalence": float(len(selected_unknown) / len(selected)),
            "sampled_known": float(len(selected_known)),
            "sampled_unknown": float(len(selected_unknown)),
        }
    )
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    # Protocol groups are named for what they run.  The paper's research
    # questions live in reports/RQ_DESIGN_2026-09-12.md and deliberately do not
    # map one-to-one onto these.
    parser.add_argument(
        "--protocol-group", dest="protocol_group", choices=["loao", "shift", "prevalence"], required=True
    )
    parser.add_argument("--protocol", choices=["loao", "difficulty", "cross_domain", "prevalence"])
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--scenario", default="Z1")
    parser.add_argument("--target-dataset")
    parser.add_argument("--source-datasets", default="")
    parser.add_argument("--methods", default="closed_backbone,msp,energy,odin,mahalanobis,openmax,hedl")
    parser.add_argument("--additional-unknown", default="")
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument(
        "--curvature",
        type=float,
        default=0.5,
        help="Poincare ball curvature. 0 selects the Euclidean ablation of the same architecture.",
    )
    parser.add_argument(
        "--scorer-components",
        default=",".join(COMPONENT_NAMES),
        help="Comma-separated conformal statistics to fuse. The default fuses all three; "
        "'md,rmd' drops the nearest-neighbour term and with it the stored reference set, "
        "which is the profile to use when inference latency is the binding constraint.",
    )
    parser.add_argument(
        "--profile",
        default=DEFAULT_PROFILE,
        choices=sorted(PROFILES),
        help="H-EDL backbone profile: lite keeps the ~6k-parameter budget, balanced adds an "
        "8-bin piecewise-linear input expansion, max widens both.",
    )
    parser.add_argument("--max-rows", type=int)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    seed_everything(args.seed)
    scorer_components = tuple(item.strip() for item in args.scorer_components.split(",") if item.strip())
    unknown_components = set(scorer_components).difference(COMPONENT_NAMES)
    if unknown_components or not scorer_components:
        parser.error(f"--scorer-components must be a non-empty subset of {list(COMPONENT_NAMES)}")
    methods = [method.strip() for method in args.methods.split(",") if method.strip()]
    default_protocol = {"loao": "loao", "shift": "difficulty", "prevalence": "prevalence"}
    protocol = args.protocol or default_protocol[args.protocol_group]
    valid_protocols = {
        "loao": {"loao"},
        "shift": {"difficulty", "cross_domain"},
        "prevalence": {"prevalence"},
    }
    if protocol not in valid_protocols[args.protocol_group]:
        parser.error(f"Protocol {protocol} is not valid for group {args.protocol_group}")
    started = time.perf_counter()
    if args.protocol_group == "shift" and protocol == "cross_domain":
        if not args.target_dataset:
            parser.error("--target-dataset is required for shift cross_domain")
        source_datasets = [item for item in args.source_datasets.split(",") if item]
        if source_datasets:
            results, shared = evaluate_leave_one_domain_out(
                source_datasets,
                args.target_dataset,
                methods,
                args.epochs,
                args.batch_size,
                args.max_rows,
                args.seed,
                args.profile,
                scorer_components,
            )
        else:
            results, shared = evaluate_cross_domain(
                args.dataset,
                args.target_dataset,
                methods,
                args.epochs,
                args.batch_size,
                args.max_rows,
                args.seed,
                args.profile,
                scorer_components,
            )
    else:
        results = evaluate_partition(
            dataset=args.dataset,
            scenario=args.scenario,
            protocol_group=args.protocol_group,
            protocol=protocol,
            methods=methods,
            seed=args.seed,
            epochs=args.epochs,
            batch_size=args.batch_size,
            max_rows=args.max_rows,
            additional_unknown=[item for item in args.additional_unknown.split(",") if item],
            profile=args.profile,
            scorer_components=scorer_components,
            curvature=args.curvature,
        )
    payload = {
        "curvature": args.curvature,
        "profile": args.profile,
        "scorer_components": list(scorer_components),
        "protocol_group": args.protocol_group,
        "protocol": protocol,
        "dataset": args.dataset,
        "scenario": args.scenario,
        "seed": args.seed,
        "methods": results,
        "elapsed_seconds": time.perf_counter() - started,
    }
    if args.protocol_group == "shift" and protocol == "cross_domain":
        payload["target_dataset"] = args.target_dataset
        if args.source_datasets:
            payload["source_datasets"] = [item for item in args.source_datasets.split(",") if item]
        payload["shared_families"] = shared
    text = json.dumps(payload, indent=2, sort_keys=True)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary_output = args.output.with_suffix(args.output.suffix + ".tmp")
        temporary_output.write_text(text, encoding="utf-8")
        temporary_output.replace(args.output)


if __name__ == "__main__":
    main()
