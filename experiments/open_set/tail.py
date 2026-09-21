"""Parametric tail extension of a conformal score, and the audit that prices it.

:mod:`resolution` shows that no distribution-free p-value can go below
``1 / (n + 1)``, and that the floor is what silences Benjamini-Hochberg at low
attack prevalence.  Leaving the distribution-free class is therefore not a
shortcut but the only escape that does not need more data, a coarser alert unit
or a weaker guarantee.  This module implements that escape in the least
committal way available: the empirical distribution is kept wherever it has
data, and a generalised Pareto tail is fitted only past the point where the
empirical distribution has nothing left to say.

The construction is the classical peaks-over-threshold model (Balkema-de Haan,
Pickands) wired to a conformal anchor.  Pick an anchor ``u`` at the ``k``-th
largest calibration score.  Its exceedance probability is known exactly and
distribution-freely: ``p_u = (k + 1) / (n + 1)``.  Above ``u`` the exceedances
are modelled as ``GPD(sigma, xi)`` and the reported p-value is
``p_u * (1 + xi (s - u) / sigma) ^ (-1 / xi)``.  The two pieces agree at ``u``
by construction, so the result is a continuous, monotone p-value that equals
the split-conformal one everywhere the split-conformal one is informative and
extrapolates only beyond it.

What the extension buys is resolution; what it costs is that validity now
depends on a tail model.  Three things keep that cost visible.  ``confidence``
replaces the fitted tail probability with a bootstrap upper bound, which trades
power for a margin against misspecification.  :meth:`TailExtendedCalibration.audit`
re-checks the extrapolated levels against held-out known traffic and reports
whether they are exceeded more often than promised.  And
:attr:`TailExtendedCalibration.floor_pvalue` records where the distribution-free
guarantee stopped, so a paper or a deployment can state which alerts rest on
the model and which do not.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.stats import binomtest, genpareto


def _as_scores(values: np.ndarray, name: str) -> np.ndarray:
    vector = np.asarray(values, dtype=np.float64).reshape(-1)
    if not len(vector):
        raise ValueError(f"{name} must not be empty")
    if not np.all(np.isfinite(vector)):
        raise ValueError(f"{name} must contain only finite values")
    return vector


def fit_generalised_pareto(
    exceedances: np.ndarray, shape_cap: float = 0.5
) -> tuple[float, float]:
    """Maximum-likelihood GPD fit with a moment fallback and a capped shape.

    ``scipy`` optimises the two-parameter GPD well when the exceedances are
    well behaved and returns nonsense when they are not -- a heavy-tailed
    intrusion score with repeated values at the top is exactly the case where
    it can wander off.  The moment estimator is used as the starting point and
    as the fallback, and the shape is capped: ``xi >= 1`` is an infinite-mean
    tail, which for an anomaly score means the fit has latched onto a handful
    of outliers rather than the tail shape.
    """
    exceedances = _as_scores(exceedances, "exceedances")
    if np.any(exceedances < 0.0):
        raise ValueError("exceedances must be non-negative offsets above the anchor")
    mean = float(exceedances.mean())
    variance = float(exceedances.var(ddof=1)) if len(exceedances) > 1 else 0.0
    if mean <= 0.0:
        return 1e-12, 0.0
    if variance > 0.0:
        moment_shape = 0.5 * (1.0 - mean * mean / variance)
        moment_scale = 0.5 * mean * (mean * mean / variance + 1.0)
    else:
        moment_shape, moment_scale = 0.0, mean
    moment_shape = float(np.clip(moment_shape, -0.5, shape_cap))
    moment_scale = float(max(moment_scale, 1e-12))
    try:
        shape, _, scale = genpareto.fit(exceedances, moment_shape, floc=0.0, scale=moment_scale)
    except Exception:  # pragma: no cover - scipy raises several unrelated types
        return moment_scale, moment_shape
    if not np.isfinite(shape) or not np.isfinite(scale) or scale <= 0.0:
        return moment_scale, moment_shape
    return float(scale), float(np.clip(shape, -0.5, shape_cap))


def generalised_pareto_survival(
    excess: np.ndarray, scale: float, shape: float
) -> np.ndarray:
    """``P(X - u > excess | X > u)`` under ``GPD(scale, shape)``."""
    excess = np.maximum(np.asarray(excess, dtype=np.float64), 0.0)
    if scale <= 0.0:
        return np.where(excess > 0.0, 0.0, 1.0)
    if abs(shape) < 1e-8:
        return np.exp(-excess / scale)
    argument = 1.0 + shape * excess / scale
    if shape < 0.0:
        # Bounded tail: everything past the upper end point has zero mass.
        argument = np.maximum(argument, 0.0)
    else:
        argument = np.maximum(argument, 1e-300)
    return np.power(argument, -1.0 / shape)


@dataclass
class TailExtendedCalibration:
    """Empirical below the anchor, generalised Pareto above it.

    ``anchor_exceedances`` is the number of calibration scores kept for the
    tail fit.  It sets the trade-off that every peaks-over-threshold analysis
    has: a low anchor uses more data and biases the shape towards the body, a
    high anchor is asymptotically right and has nothing to fit.  A few hundred
    is the usual compromise and is also where the conformal anchor probability
    ``p_u`` is still comfortably above its own floor.

    ``confidence`` of zero reports the fitted tail probability.  A value in
    ``(0, 1)`` reports instead a bootstrap upper bound at that level, which is
    the version to deploy: it is the parametric analogue of the ``+1`` in a
    conformal p-value, and it keeps the reported alert quality on the safe side
    of the fit uncertainty.
    """

    anchor_exceedances: int = 250
    confidence: float = 0.0
    bootstrap: int = 200
    shape_cap: float = 0.5
    grid_size: int = 512
    seed: int = 13
    calibration_size: int = 0
    anchor: float = 0.0
    anchor_pvalue: float = 1.0
    scale: float = 0.0
    shape: float = 0.0
    sorted_calibration: np.ndarray = field(default_factory=lambda: np.zeros(0))
    _grid: np.ndarray = field(default_factory=lambda: np.zeros(0))
    _grid_survival: np.ndarray = field(default_factory=lambda: np.zeros(0))

    @property
    def floor_pvalue(self) -> float:
        """Where the distribution-free guarantee stops and the model starts."""
        return 1.0 / (self.calibration_size + 1.0)

    def fit(self, calibration_scores: np.ndarray) -> "TailExtendedCalibration":
        scores = np.sort(_as_scores(calibration_scores, "calibration_scores"))
        size = len(scores)
        if self.anchor_exceedances < 10:
            raise ValueError("anchor_exceedances must be at least ten for a usable fit")
        exceedance_count = min(self.anchor_exceedances, max(10, size // 4))
        if size <= exceedance_count:
            raise ValueError(
                f"calibration_scores has {size} rows, too few for {exceedance_count} exceedances"
            )
        anchor = float(scores[size - exceedance_count - 1])
        excess = scores[scores > anchor] - anchor
        if not len(excess):
            raise ValueError("The anchor sits at the maximum; the score has no usable tail")
        self.calibration_size = size
        self.sorted_calibration = scores
        self.anchor = anchor
        # Exact and distribution-free: the anchor is the (k+1)-th largest of
        # n + 1 exchangeable values, so its exceedance mass is (k+1)/(n+1).
        self.anchor_pvalue = float((len(excess) + 1.0) / (size + 1.0))
        self.scale, self.shape = fit_generalised_pareto(excess, self.shape_cap)
        self._build_bound(excess)
        return self

    def _build_bound(self, excess: np.ndarray) -> None:
        """Pre-compute a bootstrap upper bound for the tail survival function.

        Evaluated on a log-spaced grid of excesses rather than per query: the
        bound is a smooth monotone curve, the grid resolves it to well under a
        percent, and a deployment scores far more flows than the grid has
        points.
        """
        if not 0.0 <= self.confidence < 1.0:
            raise ValueError("confidence must lie in [0, 1)")
        upper = float(excess.max())
        # Extrapolate two decades past the largest observed exceedance; beyond
        # that the model is reported but flagged by ``extrapolation_decades``.
        grid = np.concatenate(
            [[0.0], np.geomspace(max(upper, 1e-9) * 1e-3, max(upper, 1e-9) * 100.0, self.grid_size)]
        )
        self._grid = grid
        if self.confidence <= 0.0 or self.bootstrap < 2:
            self._grid_survival = generalised_pareto_survival(grid, self.scale, self.shape)
            return
        rng = np.random.default_rng(self.seed)
        draws = np.empty((self.bootstrap, len(grid)), dtype=np.float64)
        for index in range(self.bootstrap):
            resample = rng.choice(excess, len(excess), replace=True)
            scale, shape = fit_generalised_pareto(resample, self.shape_cap)
            draws[index] = generalised_pareto_survival(grid, scale, shape)
        self._grid_survival = np.quantile(draws, self.confidence, axis=0)
        # Monotonicity can be lost by taking a pointwise quantile of curves.
        self._grid_survival = np.minimum.accumulate(self._grid_survival)

    def _tail_survival(self, excess: np.ndarray) -> np.ndarray:
        if not len(self._grid):
            raise RuntimeError("TailExtendedCalibration is not fitted")
        if self.confidence <= 0.0 or self.bootstrap < 2:
            return generalised_pareto_survival(excess, self.scale, self.shape)
        # Interpolate the bound in log space; survival spans many decades.
        log_survival = np.log(np.maximum(self._grid_survival, 1e-300))
        return np.exp(np.interp(excess, self._grid, log_survival))

    def pvalues(self, scores: np.ndarray) -> np.ndarray:
        """Conformal p-values below the anchor, extrapolated above it."""
        if not self.calibration_size:
            raise RuntimeError("TailExtendedCalibration is not fitted")
        scores = np.asarray(scores, dtype=np.float64).reshape(-1)
        at_least = self.calibration_size - np.searchsorted(
            self.sorted_calibration, scores, side="left"
        )
        empirical = (1.0 + at_least) / (self.calibration_size + 1.0)
        above = scores > self.anchor
        if np.any(above):
            survival = self._tail_survival(scores[above] - self.anchor)
            empirical[above] = self.anchor_pvalue * survival
        return np.clip(empirical, 0.0, 1.0)

    def extrapolation_decades(self, scores: np.ndarray) -> float:
        """How far past the largest calibration score the worst query sits."""
        scores = np.asarray(scores, dtype=np.float64).reshape(-1)
        largest = float(self.sorted_calibration[-1])
        span = max(largest - self.anchor, 1e-12)
        beyond = float(np.max(scores, initial=largest) - largest)
        return float(max(0.0, beyond / span))

    def audit(
        self,
        held_out_known_scores: np.ndarray,
        levels: tuple[float, ...] = (1e-2, 1e-3, 1e-4, 1e-5),
        familywise_alpha: float = 0.05,
    ) -> dict[str, float | bool | str]:
        """Test the extrapolated levels against known traffic that was held out.

        Each level gets an exact one-sided binomial test of "known flows fall
        below this reported p-value no more often than the p-value claims".
        Levels below the distribution-free floor are the ones that matter:
        those are the claims the empirical distribution could not have made,
        and the only ones where the tail model is doing work.  Levels that the
        held-out sample is too small to resolve are reported as
        ``underpowered`` rather than as a pass, because an audit that could not
        have failed is not evidence.
        """
        scores = _as_scores(held_out_known_scores, "held_out_known_scores")
        if not 0.0 < familywise_alpha < 1.0:
            raise ValueError("familywise_alpha must lie strictly between zero and one")
        p_values = self.pvalues(scores)
        corrected = familywise_alpha / len(levels)
        report: dict[str, float | bool | str] = {
            "audit_size": float(len(scores)),
            "audit_corrected_alpha": float(corrected),
            "distribution_free_floor": self.floor_pvalue,
            "anchor_pvalue": self.anchor_pvalue,
            "tail_scale": float(self.scale),
            "tail_shape": float(self.shape),
            "tail_confidence": float(self.confidence),
        }
        rejected = False
        for level in levels:
            exceedances = int(np.sum(p_values <= level))
            test = binomtest(exceedances, len(scores), level, alternative="greater")
            level_rejected = bool(test.pvalue < corrected)
            rejected |= level_rejected
            expected = len(scores) * level
            report[f"audit_observed_le_{level:g}"] = float(exceedances)
            report[f"audit_expected_le_{level:g}"] = float(expected)
            report[f"audit_test_p_{level:g}"] = float(test.pvalue)
            report[f"audit_rejected_{level:g}"] = level_rejected
            report[f"audit_below_floor_{level:g}"] = bool(level < self.floor_pvalue)
            # With m held-out flows an audit at level alpha can only fire if
            # m * alpha is large enough for a binomial excess to be detectable.
            report[f"audit_underpowered_{level:g}"] = bool(expected < 3.0)
        report["audit_rejected"] = rejected
        report["audit_status"] = "rejected" if rejected else "not_rejected"
        return report

    def diagnostics(self) -> dict[str, float]:
        return {
            "tail_calibration_size": float(self.calibration_size),
            "tail_anchor": float(self.anchor),
            "tail_anchor_pvalue": float(self.anchor_pvalue),
            "tail_scale": float(self.scale),
            "tail_shape": float(self.shape),
            "tail_confidence": float(self.confidence),
            "tail_bootstrap": float(self.bootstrap),
            "distribution_free_floor": self.floor_pvalue,
        }
