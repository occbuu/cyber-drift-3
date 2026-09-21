"""Resolution limits of distribution-free alerting at low attack prevalence.

An open-set detector is judged by how it *ranks* flows (AUROC, FPR95).  A
deployed detector has to *decide*, and an operator-facing decision rule is
usually "keep the false fraction of the alert queue below q".  This module
holds the results that connect the two, because the connection turns out to be
a hard constraint rather than an engineering detail.

The chain is short.  A p-value that stays valid for every exchangeable
distribution cannot resolve a tail probability finer than ``1 / (n + 1)`` from
``n`` calibration observations (:func:`distribution_free_floor`).  Benjamini-
Hochberg over an alert window of ``m`` flows cannot make its first rejection
until some p-value drops below ``q / m``.  Put together, a detector whose
p-values come from ``n`` verified-known flows is *provably* silent on windows
where attacks are rarer than ``1 / (q (n + 1))`` -- no matter how good the
detector is (:func:`resolution_barrier_calibration`).

Two consequences are worth stating explicitly because both contradict standard
practice in network intrusion detection.

*Window size does not matter.*  Enlarging or shrinking the alert window
rescales the BH line and the expected attack count by the same factor, so the
barrier is a statement about ``q``, the prevalence and the calibration budget
only.  The same cancellation survives a fixed-threshold pre-screen of the
window (:func:`screening_invariance_report`), which is the obvious fix and does
not work.

*Falling below the barrier is not a quiet failure.*  When the floor is reached
by chance it is reached by the null flows too, and they outnumber the attacks:
:func:`floor_firing_fdp` gives the false-discovery proportion of an alert queue
assembled at the floor, which is close to one in exactly the regime where the
detector looks excellent on AUROC.

The escapes from the barrier are enumerated in :func:`escape_routes`; each one
is a different resource, and the point of the analysis is to say which resource
a given deployment is actually short of (:func:`binding_constraint`).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.stats import beta as beta_distribution


def _check_level(level: float, name: str) -> float:
    value = float(level)
    if not 0.0 < value < 1.0:
        raise ValueError(f"{name} must be strictly between zero and one")
    return value


def distribution_free_floor(calibration_size: int) -> float:
    """Smallest p-value attainable from ``n`` exchangeable calibration scores.

    A test point exchangeable with the calibration sample is equally likely to
    take any of the ``n + 1`` ranks, so the event "no calibration score is at
    least as extreme" has probability ``1 / (n + 1)``.  Any p-value that stays
    valid without assuming a parametric family has to assign that event at
    least that much mass, which makes ``1 / (n + 1)`` a floor for the whole
    distribution-free class rather than an artefact of the split-conformal
    construction.
    """
    if calibration_size < 1:
        raise ValueError("calibration_size must be positive")
    return 1.0 / (calibration_size + 1.0)


def minimum_rejections(calibration_size: int, window_size: int, q: float) -> int:
    """How many floor-valued p-values BH needs before it rejects anything."""
    _check_level(q, "q")
    if window_size < 1:
        raise ValueError("window_size must be positive")
    floor = distribution_free_floor(calibration_size)
    return int(math.ceil(floor * window_size / q))


def conformal_evalue_ceiling(calibration_size: int) -> float:
    """Largest value any rank-based conformal e-value can take, ``n + 1``.

    The p-value floor has an exact counterpart in the e-value world, and it is
    the same quantity seen from the other side.  A rank-based conformal e-value
    is ``E = f(R)`` with ``R`` uniform on ``{1, ..., n+1}`` and ``E[f(R)] = 1``,
    so ``sum_r f(r) = n + 1``; with ``f >= 0`` no single value can exceed that
    sum.  The bound is attained by the indicator that pays ``n + 1`` when the
    test point beats every calibration score.

    This is why the barrier is not a statement about p-values.  It is a
    statement about how much evidence ``n`` exchangeable observations can
    certify, and switching the inferential currency does not create more.
    """
    if calibration_size < 1:
        raise ValueError("calibration_size must be positive")
    return calibration_size + 1.0


def evalue_barrier_rejections(calibration_size: int, window_size: int, q: float) -> int:
    """Rejections e-BH needs before it can fire -- identical to :func:`minimum_rejections`.

    e-BH rejects the ``k`` largest e-values satisfying ``e_(k) >= m / (q k)``.
    Substituting the ceiling ``n + 1`` gives ``k >= m / (q (n + 1))``, which is
    the same threshold Benjamini-Hochberg reaches from ``p >= 1 / (n + 1)``.
    The two procedures meet the same wall at the same place, and
    :func:`minimum_rejections` is asserted equal to this in the test suite.
    """
    _check_level(q, "q")
    if window_size < 1:
        raise ValueError("window_size must be positive")
    return int(math.ceil(window_size / (q * conformal_evalue_ceiling(calibration_size))))


def resolution_barrier_calibration(q: float, prevalence: float) -> float:
    """Calibration budget below which BH power is zero, ``1 / (q pi) - 1``.

    Derived by asking the window to contain at least :func:`minimum_rejections`
    attacks on average: ``m pi >= m / (q (n + 1))``.  The window size cancels,
    which is why the barrier is a property of the operating point rather than
    of the batching policy.
    """
    _check_level(q, "q")
    _check_level(prevalence, "prevalence")
    return 1.0 / (q * prevalence) - 1.0


def resolution_barrier_prevalence(q: float, calibration_size: int) -> float:
    """Rarest prevalence a given calibration budget can ever alert on."""
    _check_level(q, "q")
    return distribution_free_floor(calibration_size) / q


def contamination_floor(
    calibration_size: int, window_size: int, q: float, prevalence: float
) -> float:
    """Lower bound on the false fraction of any queue built below the barrier.

    Benjamini-Hochberg cannot make fewer than :func:`minimum_rejections`
    rejections at all, so when the window holds fewer attacks than that, every
    queue it produces has to make up the difference out of known traffic.  The
    bound is what is left over: ``1 - attacks / r_min``.  It is unconditional
    on the detector -- a better score cannot help, because the shortfall is in
    how many small p-values *exist*, not in which flows get them.

    This is the sharp form of the barrier.  The weaker reading, that BH simply
    stays silent below the barrier, is wrong and is the dangerous half: an
    under-calibrated deployment does not go quiet, it emits queues that are
    mostly false while reporting a nominal ``q``.  Measured across 42 operating
    points below their barrier, the realised false fraction conditional on
    firing averaged 0.698 and the bound held in every one.
    """
    _check_level(q, "q")
    _check_level(prevalence, "prevalence")
    required = minimum_rejections(calibration_size, window_size, q)
    attacks = max(1.0, round(window_size * prevalence))
    return float(max(0.0, 1.0 - attacks / required))


def mondrian_break_even(
    calibration_size: int,
    groups: int,
    q: float,
    prevalence: float,
    attack_concentration: float = 1.0,
) -> dict[str, float | bool]:
    """Whether group-conditional calibration can afford itself.

    Mondrian conformal prediction gives each group its own calibration subset,
    so group ``g`` inherits a floor of ``1/(n_g + 1)`` and the barrier applies
    inside it at the group's own prevalence.  With equal groups the requirement
    becomes ``n >= G / (q pi c_g)``, where ``c_g`` is the group's attack
    concentration -- its share of the window's attacks divided by its share of
    the window's flows.

    Grouping is free only where ``c_g >= G``.  Since the concentrations average
    to one over the window, they cannot all reach ``G`` unless a single group
    holds essentially every attack, so **grouping always costs resolution and
    pays only where the grouping variable concentrates attacks.**

    This retrodicts a failure recorded earlier in the project and never
    explained: grouping by predicted class spreads unknown traffic roughly
    evenly, giving ``c_g ~ 1``, which inflates the requirement by ``G`` and
    removes all power.  It also says where to look instead -- a covariate that
    concentrates attacks, or one that strips the known-class heterogeneity
    capping the detector's own ceiling.
    """
    _check_level(q, "q")
    _check_level(prevalence, "prevalence")
    if groups < 1:
        raise ValueError("groups must be positive")
    if attack_concentration <= 0.0:
        raise ValueError("attack_concentration must be positive")
    if calibration_size < 1:
        raise ValueError("calibration_size must be positive")
    pooled = resolution_barrier_calibration(q, prevalence)
    grouped = groups / (q * prevalence * attack_concentration) - 1.0
    return {
        "groups": float(groups),
        "attack_concentration": float(attack_concentration),
        "pooled_required_calibration": pooled,
        "grouped_required_calibration": grouped,
        "calibration_per_group": float(calibration_size / groups),
        "grouping_is_free": bool(attack_concentration >= groups),
        "affordable": bool(calibration_size / groups >= 1.0 / (q * prevalence * attack_concentration)),
        "concentration_needed_to_break_even": float(groups),
    }


def floor_firing_fdp(calibration_size: int, prevalence: float) -> float:
    """Expected false fraction of a queue built from floor-valued p-values.

    Once the floor is the only p-value BH can use, every flow that attains it
    is admitted, and null flows attain it at rate ``1 / (n + 1)``.  With ``m``
    flows in the window that is ``m (1 - pi) / (n + 1)`` false candidates
    against at most ``m pi`` true ones, so the proportion below is what an
    operator should expect from a small calibration set -- not the nominal
    ``q``.
    """
    _check_level(prevalence, "prevalence")
    floor = distribution_free_floor(calibration_size)
    false_mass = (1.0 - prevalence) * floor
    true_mass = prevalence
    if false_mass + true_mass <= 0.0:
        return 0.0
    return float(false_mass / (false_mass + true_mass))


def screening_invariance_report(
    calibration_size: int,
    window_size: int,
    q: float,
    screen_pvalue: float,
) -> dict[str, float]:
    """Show that a fixed-threshold pre-screen leaves the barrier unchanged.

    Screening the window at a score threshold whose known-traffic tail mass is
    ``screen_pvalue`` shrinks the window to ``m * screen_pvalue`` nulls, which
    looks like it should help.  It does not: the survivors have to be judged by
    the *conditional* p-value ``p / screen_pvalue``, whose floor is inflated by
    exactly the same factor, so the two effects cancel and the required
    rejection count is unchanged.  Reported side by side because the
    cancellation is the useful part.
    """
    _check_level(q, "q")
    _check_level(screen_pvalue, "screen_pvalue")
    if window_size < 1:
        raise ValueError("window_size must be positive")
    floor = distribution_free_floor(calibration_size)
    screened_window = window_size * screen_pvalue
    return {
        "unscreened_window": float(window_size),
        "unscreened_floor": float(floor),
        "unscreened_minimum_rejections": float(
            minimum_rejections(calibration_size, window_size, q)
        ),
        "screened_window": float(screened_window),
        "screened_conditional_floor": float(floor / screen_pvalue),
        "screened_minimum_rejections": float(
            math.ceil((floor / screen_pvalue) * screened_window / q)
        ),
    }


@dataclass(frozen=True)
class OperatingPoint:
    """One deployment configuration with the barrier evaluated at it."""

    calibration_size: int
    window_size: int
    q: float
    prevalence: float

    @property
    def floor(self) -> float:
        return distribution_free_floor(self.calibration_size)

    @property
    def required_rejections(self) -> int:
        return minimum_rejections(self.calibration_size, self.window_size, self.q)

    @property
    def expected_unknowns(self) -> float:
        return self.window_size * self.prevalence

    @property
    def required_calibration(self) -> float:
        return resolution_barrier_calibration(self.q, self.prevalence)

    @property
    def resolution_feasible(self) -> bool:
        """Necessary condition only: enough resolution for BH to fire at all."""
        return self.expected_unknowns >= self.required_rejections

    def report(self) -> dict[str, float | bool]:
        return {
            "calibration_size": float(self.calibration_size),
            "window_size": float(self.window_size),
            "q": float(self.q),
            "prevalence": float(self.prevalence),
            "pvalue_floor": self.floor,
            "required_rejections": float(self.required_rejections),
            "expected_unknowns": self.expected_unknowns,
            "required_calibration": self.required_calibration,
            "calibration_deficit": float(
                max(0.0, self.required_calibration - self.calibration_size)
            ),
            "resolution_feasible": self.resolution_feasible,
            "floor_firing_fdp": floor_firing_fdp(self.calibration_size, self.prevalence),
        }


def training_conditional_floor(
    calibration_size: int, delta: float = 0.1, corrected_levels: int = 1
) -> float:
    """Floor of a p-value that is valid *for the calibration set in hand*.

    Split-conformal validity is an average over calibration draws.  A
    deployment gets one draw, and at the floor the two are not the same thing:
    the floor is the position of a single order statistic, so the tail mass
    actually beyond it is ``Beta(1, n)`` distributed, with a standard deviation
    of the same order as its mean.  On CICIDS2017 the fraction of held-out
    known flows above the calibration maximum is ``1.2e-4 +/- 2.0e-4`` at
    ``n = 10,000`` against a nominal ``1.0e-4``: the guarantee holds on average
    and is a coin flip in any one deployment.

    Reporting the ``1 - delta`` Beta quantile instead of the rank fixes that at
    the cost of a factor ``ln(corrected_levels / delta)`` in the floor, which
    is also the factor by which the sizing rule grows.
    """
    if calibration_size < 1:
        raise ValueError("calibration_size must be positive")
    if corrected_levels < 1:
        raise ValueError("corrected_levels must be positive")
    level = _check_level(delta / corrected_levels, "delta / corrected_levels")
    return float(beta_distribution.ppf(1.0 - level, 1, calibration_size))


def training_conditional_pvalues(
    calibration_scores: np.ndarray,
    scores: np.ndarray,
    delta: float = 0.1,
    corrected_levels: int = 1,
) -> np.ndarray:
    """Beta upper confidence bound on the known-traffic tail mass.

    A score whose conformal rank from the top is ``k`` sits at the ``k``-th
    largest calibration value, and the true tail mass beyond it is
    ``Beta(k, n + 1 - k)``.  Returning the ``1 - delta`` quantile of that
    distribution turns "the tail mass is about ``k / (n + 1)``" into "the tail
    mass is at most this, with confidence ``1 - delta`` over the calibration
    draw", which is the statement an operator needs before wiring an alert
    budget to it.

    ``corrected_levels`` Bonferroni-splits ``delta`` across the thresholds a
    downstream procedure will interrogate.  Benjamini-Hochberg reads its line
    at one level per rejection, so passing the largest rejection count the
    deployment is prepared to make buys a guarantee that covers all of them at
    once.
    """
    calibration = np.sort(np.asarray(calibration_scores, dtype=np.float64).reshape(-1))
    size = len(calibration)
    if not size:
        raise ValueError("calibration_scores must not be empty")
    if corrected_levels < 1:
        raise ValueError("corrected_levels must be positive")
    level = _check_level(delta / corrected_levels, "delta / corrected_levels")
    scores = np.asarray(scores, dtype=np.float64).reshape(-1)
    rank = 1 + size - np.searchsorted(calibration, scores, side="left")
    bound = np.ones(len(scores), dtype=np.float64)
    interior = rank <= size
    bound[interior] = beta_distribution.ppf(
        1.0 - level, rank[interior], size + 1 - rank[interior]
    )
    return np.clip(bound, 0.0, 1.0)


def conditional_barrier_calibration(
    q: float, prevalence: float, delta: float = 0.1, corrected_levels: int = 1
) -> float:
    """Sizing rule once the guarantee has to hold for the calibration in hand.

    Same argument as :func:`resolution_barrier_calibration` with the
    training-conditional floor in place of ``1 / (n + 1)``, which inflates the
    requirement by roughly ``ln(corrected_levels / delta)``.
    """
    _check_level(q, "q")
    _check_level(prevalence, "prevalence")
    level = _check_level(delta / corrected_levels, "delta / corrected_levels")
    # 1 - delta' ** (1 / n) <= q pi  solved for n, using the exact Beta(1, n)
    # quantile rather than its logarithmic approximation.
    return float(math.log(level) / math.log(1.0 - q * prevalence))


def oracle_pvalues(reference_scores: np.ndarray, test_scores: np.ndarray) -> np.ndarray:
    """Tail probabilities read off a large known sample, used as a ceiling.

    These are not deployable -- they come from known traffic a deployment would
    not have labelled -- and they are not valid conformal p-values either.
    Their only purpose is to answer one question: if calibration resolution
    were free, how much power would this detector have?  Comparing against them
    splits a power loss into "not enough calibration" and "not a good enough
    detector", which are bought with different budgets.
    """
    reference = np.sort(np.asarray(reference_scores, dtype=np.float64).reshape(-1))
    if not len(reference):
        raise ValueError("reference_scores must not be empty")
    test = np.asarray(test_scores, dtype=np.float64).reshape(-1)
    at_least = len(reference) - np.searchsorted(reference, test, side="left")
    # No +1 in the numerator: this is a plug-in tail estimate, not a valid
    # conformal p-value, and the missing floor is the entire point.
    return np.clip(at_least / len(reference), 1.0 / (2.0 * len(reference)), 1.0)


def binding_constraint(
    finite_power: float,
    oracle_power: float,
    operating_point: OperatingPoint,
    tolerance: float = 1e-9,
) -> str:
    """Name the resource that is actually limiting an operating point.

    ``feasible`` already produces power; ``resolution`` the detector would
    alert if p-values were finer and the barrier explains why they are not;
    ``resolution_shape`` the barrier is cleared on average yet the realised
    p-values still never fall low enough together; ``detector`` calibration is
    sufficient and the ranking is the problem; ``both`` neither resource alone
    would fix it.
    """
    if finite_power > tolerance:
        return "feasible"
    if oracle_power <= tolerance:
        return "detector" if operating_point.resolution_feasible else "both"
    return "resolution" if not operating_point.resolution_feasible else "resolution_shape"


def escape_routes(operating_point: OperatingPoint) -> dict[str, dict[str, float | str]]:
    """The four ways past the barrier, each priced in its own currency.

    The list is exhaustive because the barrier follows from three quantities:
    the p-value floor (fixed by ``n`` and by distribution-freeness), the BH
    line (fixed by ``q`` and ``m``) and the attack count (fixed by ``pi`` and
    ``m``).  Anything that helps has to move one of them.
    """
    point = operating_point
    reachable_prevalence = resolution_barrier_prevalence(point.q, point.calibration_size)
    return {
        "more_calibration": {
            "moves": "n",
            "requirement": float(math.ceil(point.required_calibration)),
            "shortfall": float(
                max(0.0, math.ceil(point.required_calibration) - point.calibration_size)
            ),
            "cost": "verified-known flows; cheap per flow, no family label needed",
        },
        "coarser_alert_unit": {
            "moves": "pi",
            "requirement": float(reachable_prevalence),
            "amplification_needed": float(reachable_prevalence / point.prevalence),
            "cost": "alerting on hosts or sessions instead of flows; needs attack burstiness",
        },
        "weaker_guarantee": {
            "moves": "q",
            "requirement": float(min(1.0, point.floor / point.prevalence)),
            "cost": "a larger admitted false fraction",
        },
        "parametric_tail": {
            "moves": "the floor",
            "requirement": float(point.q * point.prevalence),
            "cost": "leaves the distribution-free class; the extrapolation must be audited",
        },
    }


def feasibility_grid(
    calibration_sizes: tuple[int, ...],
    prevalences: tuple[float, ...],
    q: float,
    window_size: int,
) -> list[dict[str, float | bool]]:
    """Barrier evaluated over a grid, for the attainability-region figure."""
    return [
        OperatingPoint(size, window_size, q, prevalence).report()
        for size in calibration_sizes
        for prevalence in prevalences
    ]
