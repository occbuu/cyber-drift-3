"""Batch false-discovery-rate control for zero-day alerts.

The score function must be fixed before final calibration scores are observed.
The runner therefore uses disjoint tuning and FDR-calibration subsets. The same
conformal wrapper is applied to every method: the comparison is power at a fixed
FDR target, not whether a raw detector happened to emit calibrated scores.
"""

from __future__ import annotations

import math
from collections.abc import Iterable

import numpy as np


def _validate_level(level: float, name: str) -> float:
    value = float(level)
    if not 0.0 < value < 1.0:
        raise ValueError(f"{name} must be strictly between zero and one")
    return value


def _as_finite_vector(values: np.ndarray, name: str, allow_empty: bool = False) -> np.ndarray:
    vector = np.asarray(values, dtype=np.float64).reshape(-1)
    if not allow_empty and not len(vector):
        raise ValueError(f"{name} must not be empty")
    if not np.all(np.isfinite(vector)):
        raise ValueError(f"{name} must contain only finite values")
    return vector


def conformal_pvalues(calibration_scores: np.ndarray, test_scores: np.ndarray) -> np.ndarray:
    """Marginal split-conformal p-values for upper-tail anomaly scores."""
    calibration = np.sort(_as_finite_vector(calibration_scores, "calibration_scores"))
    test = _as_finite_vector(test_scores, "test_scores", allow_empty=True)
    at_least = len(calibration) - np.searchsorted(calibration, test, side="left")
    return (1.0 + at_least) / (len(calibration) + 1.0)


def mondrian_conformal_pvalues(
    calibration_scores: np.ndarray,
    test_scores: np.ndarray,
    calibration_groups: np.ndarray,
    test_groups: np.ndarray,
    minimum_group_size: int = 30,
) -> np.ndarray:
    """Predicted-group conditional p-values with a conservative pooled fallback."""
    calibration = _as_finite_vector(calibration_scores, "calibration_scores")
    test = _as_finite_vector(test_scores, "test_scores", allow_empty=True)
    calibration_groups = np.asarray(calibration_groups).reshape(-1)
    test_groups = np.asarray(test_groups).reshape(-1)
    if calibration.shape != calibration_groups.shape:
        raise ValueError("calibration_scores and calibration_groups must have the same shape")
    if test.shape != test_groups.shape:
        raise ValueError("test_scores and test_groups must have the same shape")
    if minimum_group_size < 1:
        raise ValueError("minimum_group_size must be positive")
    p_values = conformal_pvalues(calibration, test)
    for group in np.unique(test_groups):
        calibration_mask = calibration_groups == group
        if int(calibration_mask.sum()) < minimum_group_size:
            continue
        test_mask = test_groups == group
        p_values[test_mask] = conformal_pvalues(calibration[calibration_mask], test[test_mask])
    return p_values


def calibrated_pvalues(
    calibration_scores: np.ndarray,
    test_scores: np.ndarray,
    calibration_groups: np.ndarray | None = None,
    test_groups: np.ndarray | None = None,
    minimum_group_size: int = 30,
) -> np.ndarray:
    if calibration_groups is None and test_groups is None:
        return conformal_pvalues(calibration_scores, test_scores)
    if calibration_groups is None or test_groups is None:
        raise ValueError("calibration_groups and test_groups must be supplied together")
    return mondrian_conformal_pvalues(
        calibration_scores,
        test_scores,
        calibration_groups,
        test_groups,
        minimum_group_size,
    )


def null_pvalue_diagnostics(
    calibration_scores: np.ndarray,
    known_test_scores: np.ndarray,
    levels: Iterable[float] = (0.001, 0.01, 0.05, 0.1),
    calibration_groups: np.ndarray | None = None,
    known_test_groups: np.ndarray | None = None,
    minimum_group_size: int = 30,
    audit_alpha: float = 0.05,
) -> dict[str, float | bool | str]:
    """Check whether held-out known traffic still yields super-uniform p-values."""
    audit_alpha = _validate_level(audit_alpha, "audit_alpha")
    p_values = calibrated_pvalues(
        calibration_scores,
        known_test_scores,
        calibration_groups,
        known_test_groups,
        minimum_group_size,
    )
    sorted_p = np.sort(p_values)
    empirical_cdf = np.arange(1, len(sorted_p) + 1, dtype=np.float64) / len(sorted_p)
    violation = float(np.max(empirical_cdf - sorted_p))
    # Two-sample bound: the reference is the empirical distribution of a finite
    # calibration sample, not a known CDF, so the one-sample DKW critical value
    # is too tight and rejects exchangeable traffic well above its nominal rate.
    calibration_size = len(np.asarray(calibration_scores).reshape(-1))
    dkw_bound = float(
        math.sqrt(
            0.5 * math.log(1.0 / audit_alpha) * (1.0 / calibration_size + 1.0 / len(p_values))
        )
    )
    audit_rejected = violation > dkw_bound
    diagnostics = {
        "known_test_size": float(len(p_values)),
        "superuniform_violation": violation,
        "superuniform_dkw_bound": dkw_bound,
        "superuniform_audit_alpha": audit_alpha,
        "superuniform_audit_rejected": audit_rejected,
        "superuniform_audit_status": "rejected" if audit_rejected else "not_rejected",
        "median_known_p": float(np.median(p_values)),
    }
    for level in levels:
        level = _validate_level(level, "level")
        diagnostics[f"known_p_le_{level:g}"] = float(np.mean(p_values <= level))
    return diagnostics

def mondrian_group_diagnostics(
    calibration_groups: np.ndarray,
    test_groups: np.ndarray,
    minimum_group_size: int = 30,
) -> dict[str, object]:
    """Report group support and pooled-fallback use for Mondrian calibration."""
    calibration_groups = np.asarray(calibration_groups).reshape(-1)
    test_groups = np.asarray(test_groups).reshape(-1)
    if minimum_group_size < 1:
        raise ValueError("minimum_group_size must be positive")
    groups = []
    fallback_test_count = 0
    for group in np.union1d(calibration_groups, test_groups):
        calibration_count = int(np.sum(calibration_groups == group))
        test_count = int(np.sum(test_groups == group))
        uses_group_calibration = calibration_count >= minimum_group_size
        if not uses_group_calibration:
            fallback_test_count += test_count
        groups.append(
            {
                "group": str(group),
                "calibration_count": calibration_count,
                "test_count": test_count,
                "uses_group_calibration": uses_group_calibration,
            }
        )
    return {
        "minimum_group_size": int(minimum_group_size),
        "group_count": len(groups),
        "fallback_test_count": fallback_test_count,
        "fallback_test_fraction": float(fallback_test_count / len(test_groups)) if len(test_groups) else 0.0,
        "groups": groups,
    }


def benjamini_hochberg(p_values: np.ndarray, q: float) -> np.ndarray:
    """Boolean rejection mask from the Benjamini-Hochberg step-up procedure."""
    p_values = _as_finite_vector(p_values, "p_values", allow_empty=True)
    q = _validate_level(q, "q")
    if np.any((p_values < 0.0) | (p_values > 1.0)):
        raise ValueError("p_values must lie in [0, 1]")
    count = len(p_values)
    if count == 0:
        return np.zeros(0, dtype=bool)
    order = np.argsort(p_values, kind="stable")
    ranked = p_values[order]
    passing = np.flatnonzero(ranked <= q * np.arange(1, count + 1) / count)
    rejected = np.zeros(count, dtype=bool)
    if len(passing):
        rejected[order[: passing[-1] + 1]] = True
    return rejected


def benjamini_yekutieli(p_values: np.ndarray, q: float) -> np.ndarray:
    """Dependency-robust BY procedure, implemented as BH at ``q / H_m``."""
    p_values = _as_finite_vector(p_values, "p_values", allow_empty=True)
    q = _validate_level(q, "q")
    if not len(p_values):
        return np.zeros(0, dtype=bool)
    harmonic = float(np.sum(1.0 / np.arange(1, len(p_values) + 1)))
    return benjamini_hochberg(p_values, q / harmonic)



def conformal_evalues(
    calibration_scores: np.ndarray, test_scores: np.ndarray, top_k: int = 1
) -> np.ndarray:
    """Rank-based conformal e-values, in the family that maximises the ceiling.

    Under exchangeability the rank ``R = 1 + #{i : S_i >= S}`` of a null test
    point is uniform on ``{1, ..., n+1}``, so ``E = (n+1)/k * 1{R <= k}`` has
    unit expectation for any fixed ``k`` and is a valid e-value.  ``top_k = 1``
    is the extreme member: it pays out ``n+1`` when the test point beats every
    calibration score and nothing otherwise.

    That extreme is deliberate.  Every rank-based conformal e-value obeys
    ``E[f(R)] = 1`` with ``R`` uniform, hence ``sum_r f(r) = n+1`` and, since
    ``f >= 0``, ``max_r f(r) <= n+1``.  The ceiling is therefore a property of
    the calibration sample size, not of which construction is chosen, and
    ``top_k = 1`` attains it.  Giving e-BH its most favourable e-value is the
    only fair way to test whether e-values escape the resolution barrier.
    """
    calibration = np.sort(_as_finite_vector(calibration_scores, "calibration_scores"))
    test = _as_finite_vector(test_scores, "test_scores", allow_empty=True)
    size = len(calibration)
    if not 1 <= top_k <= size + 1:
        raise ValueError(f"top_k must lie in [1, {size + 1}]")
    rank = 1 + size - np.searchsorted(calibration, test, side="left")
    return np.where(rank <= top_k, (size + 1.0) / top_k, 0.0)


def harmonic_conformal_evalues(
    calibration_scores: np.ndarray, test_scores: np.ndarray
) -> np.ndarray:
    """Smooth alternative: ``E = (n+1) / (R * H_{n+1})``, unit expectation.

    Included because the indicator family is all-or-nothing and a reviewer will
    reasonably ask whether a graded e-value does better.  Its ceiling is
    ``(n+1)/H_{n+1}``, which is *smaller* than the indicator's ``n+1`` -- the
    smoothness is bought from the same fixed budget of ``n+1``.
    """
    calibration = np.sort(_as_finite_vector(calibration_scores, "calibration_scores"))
    test = _as_finite_vector(test_scores, "test_scores", allow_empty=True)
    size = len(calibration)
    harmonic = float(np.sum(1.0 / np.arange(1, size + 2)))
    rank = 1 + size - np.searchsorted(calibration, test, side="left")
    return (size + 1.0) / (rank * harmonic)


def e_benjamini_hochberg(e_values: np.ndarray, q: float) -> np.ndarray:
    """e-BH (Wang and Ramdas, 2022): reject the ``k`` largest with ``e_(k) >= m/(qk)``."""
    e_values = _as_finite_vector(e_values, "e_values", allow_empty=True)
    q = _validate_level(q, "q")
    if np.any(e_values < 0.0):
        raise ValueError("e_values must be non-negative")
    count = len(e_values)
    if count == 0:
        return np.zeros(0, dtype=bool)
    order = np.argsort(-e_values, kind="stable")
    ranked = e_values[order]
    ranks = np.arange(1, count + 1)
    passing = np.flatnonzero(ranked >= count / (q * ranks))
    rejected = np.zeros(count, dtype=bool)
    if len(passing):
        rejected[order[: passing[-1] + 1]] = True
    return rejected


def storey_pi_zero(p_values: np.ndarray, threshold: float = 0.5) -> float:
    """Storey's null-proportion estimate, ``(1 + #{p > lambda}) / (m (1 - lambda))``."""
    p_values = _as_finite_vector(p_values, "p_values", allow_empty=True)
    threshold = _validate_level(threshold, "threshold")
    if not len(p_values):
        return 1.0
    estimate = (1.0 + np.sum(p_values > threshold)) / (len(p_values) * (1.0 - threshold))
    return float(min(1.0, estimate))


def storey_benjamini_hochberg(
    p_values: np.ndarray, q: float, threshold: float = 0.5
) -> np.ndarray:
    """Adaptive BH at ``q / pi_0``.

    Its whole advantage is knowing that some hypotheses are non-null, which at
    an attack prevalence of ``10^-3`` means a correction factor of
    ``1/pi_0 <= 1.001``.  Reported to make that arithmetic explicit rather than
    to give it a chance.
    """
    p_values = _as_finite_vector(p_values, "p_values", allow_empty=True)
    q = _validate_level(q, "q")
    pi_zero = storey_pi_zero(p_values, threshold)
    if pi_zero <= 0.0:
        return np.ones(len(p_values), dtype=bool)
    return benjamini_hochberg(p_values, min(0.999999, q / pi_zero))

def apply_fdr_procedure(p_values: np.ndarray, q: float, procedure: str) -> np.ndarray:
    procedures = {
        "bh": benjamini_hochberg,
        "by": benjamini_yekutieli,
        "storey_bh": storey_benjamini_hochberg,
    }
    try:
        function = procedures[procedure.lower()]
    except KeyError as error:
        raise ValueError(f"Unknown FDR procedure {procedure!r}; choose from {sorted(procedures)}") from error
    return function(p_values, q)


def realised_error_rates(rejected: np.ndarray, is_unknown: np.ndarray) -> dict[str, float]:
    """Return operator-facing error rates for one deployment batch."""
    rejected = np.asarray(rejected, dtype=bool).reshape(-1)
    is_unknown = np.asarray(is_unknown, dtype=bool).reshape(-1)
    if rejected.shape != is_unknown.shape:
        raise ValueError("rejected and is_unknown must have the same shape")
    alerts = int(rejected.sum())
    true_alerts = int((rejected & is_unknown).sum())
    false_alerts = alerts - true_alerts
    unknown_count = int(is_unknown.sum())
    known_count = len(is_unknown) - unknown_count
    return {
        "alerts": float(alerts),
        "true_discoveries": float(true_alerts),
        "false_discoveries": float(false_alerts),
        "false_discovery_proportion": float(false_alerts / alerts) if alerts else 0.0,
        "power": float(true_alerts / unknown_count) if unknown_count else 0.0,
        "false_alarm_rate": float(false_alerts / known_count) if known_count else 0.0,
        "alert_rate": float(alerts / len(rejected)) if len(rejected) else 0.0,
    }


def sample_batch_to_prevalence(
    is_unknown: np.ndarray,
    prevalence: float,
    batch_size: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Sample a fixed-size batch at the requested unknown prevalence."""
    is_unknown = np.asarray(is_unknown, dtype=bool).reshape(-1)
    prevalence = _validate_level(prevalence, "prevalence")
    if batch_size < 2:
        raise ValueError("batch_size must be at least two")
    unknown_count = max(1, min(batch_size - 1, round(batch_size * prevalence)))
    known_count = batch_size - unknown_count
    known = np.flatnonzero(~is_unknown)
    unknown = np.flatnonzero(is_unknown)
    if known_count > len(known) or unknown_count > len(unknown):
        raise ValueError(
            f"Cannot draw batch_size={batch_size} at prevalence={prevalence}: "
            f"need {known_count} known/{unknown_count} unknown, have {len(known)}/{len(unknown)}"
        )
    selected = np.concatenate(
        [rng.choice(known, known_count, replace=False), rng.choice(unknown, unknown_count, replace=False)]
    )
    rng.shuffle(selected)
    return selected


def subsample_to_prevalence(
    is_unknown: np.ndarray, prevalence: float, rng: np.random.Generator
) -> np.ndarray:
    """Compatibility helper that uses the largest feasible variable-size batch."""
    is_unknown = np.asarray(is_unknown, dtype=bool).reshape(-1)
    prevalence = _validate_level(prevalence, "prevalence")
    known_count = int((~is_unknown).sum())
    unknown_count = int(is_unknown.sum())
    maximum = min(int(known_count / (1.0 - prevalence)), int(unknown_count / prevalence))
    return sample_batch_to_prevalence(is_unknown, prevalence, max(2, maximum), rng)


def stratified_calibration_split(
    labels: np.ndarray,
    tuning_fraction: float,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Disjoint class-stratified indices for score tuning and final calibration."""
    labels = np.asarray(labels).reshape(-1)
    tuning_fraction = _validate_level(tuning_fraction, "tuning_fraction")
    rng = np.random.default_rng(seed)
    tuning: list[np.ndarray] = []
    calibration: list[np.ndarray] = []
    for label in np.unique(labels):
        indices = np.flatnonzero(labels == label)
        if len(indices) < 2:
            # A class seen once cannot be split; it goes to calibration, where a
            # single score still counts, rather than to the fusion-weight proxy,
            # which needs at least two rows of a class to use it at all.
            calibration.append(indices)
            continue
        shuffled = rng.permutation(indices)
        split = min(len(indices) - 1, max(1, round(len(indices) * tuning_fraction)))
        tuning.append(shuffled[:split])
        calibration.append(shuffled[split:])
    tuning_indices = np.concatenate(tuning)
    calibration_indices = np.concatenate(calibration)
    rng.shuffle(tuning_indices)
    rng.shuffle(calibration_indices)
    return tuning_indices, calibration_indices


def _summarise_trials(trials: list[dict[str, float]], nominal_q: float | None = None) -> dict[str, float]:
    arrays = {
        key: np.asarray([trial[key] for trial in trials], dtype=np.float64)
        for key in trials[0]
    }
    summary: dict[str, float] = {}
    for key, values in arrays.items():
        summary[f"mean_{key}"] = float(values.mean())
        summary[f"std_{key}"] = float(values.std(ddof=1)) if len(values) > 1 else 0.0
    fdp = arrays["false_discovery_proportion"]
    standard_error = float(fdp.std(ddof=1) / math.sqrt(len(fdp))) if len(fdp) > 1 else 0.0
    summary.update(
        empirical_fdr=float(fdp.mean()),
        empirical_fdr_se=standard_error,
        empirical_fdr_ci95_low=float(max(0.0, fdp.mean() - 1.96 * standard_error)),
        empirical_fdr_ci95_high=float(min(1.0, fdp.mean() + 1.96 * standard_error)),
        fdp_p90=float(np.quantile(fdp, 0.9)),
        probability_any_alert=float(np.mean(arrays["alerts"] > 0.0)),
    )
    if nominal_q is not None:
        summary["nominal_q"] = float(nominal_q)
        summary["fraction_fdp_above_q"] = float(np.mean(fdp > nominal_q))
    return summary


def minimum_bh_rejections(
    calibration_size: int,
    batch_size: int,
    q: float,
    procedure: str = "bh",
) -> int:
    """Minimum count of smallest-attainable p-values needed to cross the step-up line."""
    q = _validate_level(q, "q")
    if calibration_size < 1 or batch_size < 1:
        raise ValueError("calibration_size and batch_size must be positive")
    effective_q = q
    if procedure.lower() == "by":
        effective_q /= float(np.sum(1.0 / np.arange(1, batch_size + 1)))
    elif procedure.lower() != "bh":
        raise ValueError("procedure must be 'bh' or 'by'")
    return int(math.ceil(batch_size / (effective_q * (calibration_size + 1))))


def evaluate_fdr_curve(
    calibration_scores: np.ndarray,
    test_scores: np.ndarray,
    is_unknown: np.ndarray,
    prevalences: Iterable[float],
    q_levels: Iterable[float],
    batch_size: int,
    repeats: int,
    seed: int,
    procedures: Iterable[str] = ("bh", "by"),
    calibration_groups: np.ndarray | None = None,
    test_groups: np.ndarray | None = None,
    minimum_group_size: int = 30,
) -> dict[str, object]:
    """Estimate FDR and power by repeated fixed-size deployment batches."""
    calibration = _as_finite_vector(calibration_scores, "calibration_scores")
    test = _as_finite_vector(test_scores, "test_scores")
    is_unknown = np.asarray(is_unknown, dtype=bool).reshape(-1)
    if test.shape != is_unknown.shape:
        raise ValueError("test_scores and is_unknown must have the same shape")
    if repeats < 1:
        raise ValueError("repeats must be positive")
    prevalence_values = tuple(_validate_level(value, "prevalence") for value in prevalences)
    q_values = tuple(_validate_level(value, "q") for value in q_levels)
    procedure_names = tuple(name.lower() for name in procedures)
    p_values = calibrated_pvalues(
        calibration,
        test,
        calibration_groups,
        test_groups,
        minimum_group_size,
    )
    if calibration_groups is None:
        effective_calibration_sizes = np.full(len(test), len(calibration), dtype=np.int64)
        calibration_mode = "marginal"
    else:
        calibration_groups_array = np.asarray(calibration_groups).reshape(-1)
        test_groups_array = np.asarray(test_groups).reshape(-1)
        group_sizes = {
            group: int(np.sum(calibration_groups_array == group))
            for group in np.unique(calibration_groups_array)
        }
        effective_calibration_sizes = np.asarray(
            [
                group_sizes.get(group, 0)
                if group_sizes.get(group, 0) >= minimum_group_size
                else len(calibration)
                for group in test_groups_array
            ],
            dtype=np.int64,
        )
        calibration_mode = "predicted_group_mondrian"
    rng = np.random.default_rng(seed)
    batches = {
        prevalence: [sample_batch_to_prevalence(is_unknown, prevalence, batch_size, rng) for _ in range(repeats)]
        for prevalence in prevalence_values
    }
    results: dict[str, object] = {
        "calibration_size": len(calibration),
        "calibration_mode": calibration_mode,
        "batch_size": int(batch_size),
        "repeats": int(repeats),
        "minimum_attainable_p": float(np.min(1.0 / (effective_calibration_sizes + 1.0))),
        "maximum_minimum_attainable_p": float(np.max(1.0 / (effective_calibration_sizes + 1.0))),
        "procedures": {},
    }
    procedure_results: dict[str, object] = {}
    for procedure in procedure_names:
        prevalence_results: dict[str, object] = {}
        for prevalence, sampled_batches in batches.items():
            q_results: dict[str, object] = {}
            for q in q_values:
                trials = []
                for selected in sampled_batches:
                    rejected = apply_fdr_procedure(p_values[selected], q, procedure)
                    trials.append(realised_error_rates(rejected, is_unknown[selected]))
                summary = _summarise_trials(trials, q)
                summary["minimum_bh_rejections_at_pmin"] = float(
                    minimum_bh_rejections(len(calibration), batch_size, q, procedure)
                )
                q_results[str(q)] = summary
            prevalence_results[str(prevalence)] = q_results
        procedure_results[procedure] = prevalence_results
    results["procedures"] = procedure_results
    return results


def evaluate_fixed_far_curve(
    calibration_scores: np.ndarray,
    test_scores: np.ndarray,
    is_unknown: np.ndarray,
    prevalences: Iterable[float],
    batch_size: int,
    repeats: int,
    seed: int,
    false_alarm_budget: float = 0.01,
) -> dict[str, object]:
    """Repeated prevalence curve for the conventional fixed-FAR threshold."""
    calibration = _as_finite_vector(calibration_scores, "calibration_scores")
    test = _as_finite_vector(test_scores, "test_scores")
    is_unknown = np.asarray(is_unknown, dtype=bool).reshape(-1)
    if test.shape != is_unknown.shape:
        raise ValueError("test_scores and is_unknown must have the same shape")
    false_alarm_budget = _validate_level(false_alarm_budget, "false_alarm_budget")
    threshold = float(np.quantile(calibration, 1.0 - false_alarm_budget))
    rng = np.random.default_rng(seed)
    prevalence_results: dict[str, object] = {}
    for prevalence in prevalences:
        prevalence = _validate_level(prevalence, "prevalence")
        trials = []
        for _ in range(repeats):
            selected = sample_batch_to_prevalence(is_unknown, prevalence, batch_size, rng)
            trials.append(realised_error_rates(test[selected] >= threshold, is_unknown[selected]))
        prevalence_results[str(prevalence)] = _summarise_trials(trials)
    return {
        "false_alarm_budget": false_alarm_budget,
        "threshold": threshold,
        "prevalence": prevalence_results,
    }
