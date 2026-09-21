from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    precision_recall_fscore_support,
    roc_auc_score,
    roc_curve,
)


def fpr_at_tpr(y_true: np.ndarray, scores: np.ndarray, target_tpr: float = 0.95) -> float:
    fpr, tpr, _ = roc_curve(y_true, scores)
    indices = np.flatnonzero(tpr >= target_tpr)
    return float(fpr[indices[0]]) if len(indices) else 1.0


def tpr_at_fpr(y_true: np.ndarray, scores: np.ndarray, target_fpr: float) -> float:
    fpr, tpr, _ = roc_curve(y_true, scores)
    valid = np.flatnonzero(fpr <= target_fpr)
    return float(tpr[valid[-1]]) if len(valid) else 0.0


def oscr(
    known_labels: np.ndarray,
    known_predictions: np.ndarray,
    known_scores: np.ndarray,
    unknown_scores: np.ndarray,
) -> float:
    correct = known_predictions == known_labels
    thresholds = np.unique(np.concatenate([known_scores, unknown_scores]))
    thresholds = np.concatenate(([-np.inf], thresholds, [np.inf]))
    ccr = np.array([np.mean(correct & (known_scores < threshold)) for threshold in thresholds])
    fpr = np.array([np.mean(unknown_scores < threshold) for threshold in thresholds])
    order = np.argsort(fpr)
    return float(np.trapezoid(ccr[order], fpr[order]))


def evaluate_open_set(
    labels: np.ndarray,
    predictions: np.ndarray,
    unknown_scores: np.ndarray,
    threshold: float | None = None,
) -> dict[str, float]:
    known_mask = labels >= 0
    unknown_mask = ~known_mask
    binary = unknown_mask.astype(np.int64)
    known_labels = labels[known_mask]
    known_predictions = predictions[known_mask]
    metrics = {
        "known_accuracy": accuracy_score(known_labels, known_predictions),
        "known_macro_f1": f1_score(known_labels, known_predictions, average="macro", zero_division=0),
        "known_weighted_f1": f1_score(known_labels, known_predictions, average="weighted", zero_division=0),
        "unknown_auroc": roc_auc_score(binary, unknown_scores),
        "fpr95": fpr_at_tpr(binary, unknown_scores),
        "aupr_out": average_precision_score(binary, unknown_scores),
        "oscr": oscr(known_labels, known_predictions, unknown_scores[known_mask], unknown_scores[unknown_mask]),
        "tpr_at_5_fpr": tpr_at_fpr(binary, unknown_scores, 0.05),
        "tpr_at_1_fpr": tpr_at_fpr(binary, unknown_scores, 0.01),
        "tpr_at_0_1_fpr": tpr_at_fpr(binary, unknown_scores, 0.001),
    }
    if threshold is not None:
        rejected = unknown_scores >= threshold
        open_predictions = predictions.copy()
        open_predictions[rejected] = -1
        metrics["open_world_macro_f1"] = f1_score(labels, open_predictions, average="macro", zero_division=0)
        precision, recall, f1, _ = precision_recall_fscore_support(
            binary,
            rejected.astype(np.int64),
            average="binary",
            zero_division=0,
        )
        metrics.update(
            unknown_precision=float(precision),
            unknown_recall=float(recall),
            unknown_f1=float(f1),
            far=float(rejected[known_mask].mean()),
            frr=float((~rejected[unknown_mask]).mean()),
        )
    return metrics


def known_only_metrics(labels: np.ndarray, predictions: np.ndarray) -> dict[str, float]:
    return {
        "known_accuracy": accuracy_score(labels, predictions),
        "known_macro_f1": f1_score(labels, predictions, average="macro", zero_division=0),
        "known_weighted_f1": f1_score(labels, predictions, average="weighted", zero_division=0),
    }
