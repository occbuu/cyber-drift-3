"""PACT: prevalence-aware conformal triage for open-set intrusion detection.

The detector is not the hard part.  On CICIDS2017 the open-set scorer in this
repository separates held-out attack families from known traffic at AUROC
0.9985, and at that point every additional point of AUROC is worth nothing to
an operator who has to decide which flows enter an alert queue at an attack
prevalence of one in a thousand.  What binds there is not ranking but
*resolution*: how finely the p-value attached to a flow can be stated, and how
much of that statement survives the fact that a deployment calibrates once,
on one sample, and then lives with it.

PACT is the deployment half of that picture.  It takes a fixed score function
and a sample of verified-known flows and produces one of three outcomes, each
of which is a claim the deployment can defend:

``certified``   the calibration budget clears the barrier for the requested
                guarantee and the audits pass, so Benjamini-Hochberg runs and
                the false-discovery budget means what it says;
``degraded``    the budget clears the marginal barrier but not the
                training-conditional one, so alerts are emitted under the
                weaker guarantee and labelled as such;
``refuse``      no false-discovery claim is available -- because the
                calibration is too small, or because an audit says the
                calibration sample no longer looks like the traffic being
                scored -- and alerting falls back to a fixed alarm budget that
                promises a workload rather than a quality.

The refusal is the part that matters operationally.  An uncertified
Benjamini-Hochberg at low prevalence does not fail loudly; it either emits
nothing, which reads as "no attacks", or it fires off the p-value floor, where
the nulls outnumber the attacks and the queue is mostly false.  Both look like
a working detector from the outside.

Two design choices are worth stating because they are what the accompanying
measurements are about.

*Extrapolate inside the score, not inside the p-value.*  The fused conformal
score is bounded above by ``sum_i w_i log(n_tuning + 1)``, and on CICIDS2017
that ceiling ties 2,600 test flows at one value.  Replacing each component's
floored p-value with a tail-extended one (:mod:`tail`) removes the ceiling and
raises TPR at a 1e-4 false-alarm rate from 0.136 to 0.235 -- and costs nothing
in validity, because the score is only a function and the alert-stage p-value
is still an exact conformal rank against a disjoint calibration split.  The
same extrapolation applied to the alert-stage p-value *does* trade the
guarantee away, which is why it is off unless asked for and audited when used.

*Report the guarantee you can keep.*  Split-conformal validity is an average
over calibration draws.  At the floor, where low-prevalence alerting operates,
the realised tail mass beyond the calibration maximum has a standard deviation
of the same order as its mean, so the average is not what any single
deployment gets.  Measured at 1% prevalence with 12,592 calibration flows,
marginal BH sits at a mean FDR of 0.101 against a nominal 0.1 while the
training-conditional version sits at 0.093 with no draw above budget, for a
7% relative power cost.  PACT defaults to the guarantee an operator can
actually keep and prices the other one next to it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from .fdr import benjamini_hochberg, benjamini_yekutieli, conformal_pvalues
from .resolution import (
    OperatingPoint,
    conditional_barrier_calibration,
    distribution_free_floor,
    escape_routes,
    resolution_barrier_calibration,
    training_conditional_floor,
    training_conditional_pvalues,
)
from .tail import TailExtendedCalibration


GUARANTEES = ("conditional", "marginal")
TAIL_POLICIES = ("off", "audited")
STATES = ("certified", "degraded", "refuse")


@dataclass(frozen=True)
class AlertBudget:
    """What the operator asks for and what the traffic imposes.

    ``prevalence`` is an input, not a measurement: it is the rarest attack rate
    the deployment wants the guarantee to hold at.  Everything downstream is
    sizing against that number, so getting it wrong is the one modelling error
    PACT cannot audit for.
    """

    q: float = 0.1
    prevalence: float = 0.001
    window_size: int = 2000
    delta: float = 0.1
    # The Beta bound is pointwise: splitting delta across ``corrected_levels``
    # buys a guarantee for a decision that interrogates at most that many
    # thresholds.  Benjamini-Hochberg reads one threshold per rejection, so the
    # guarantee only covers the procedure if the procedure cannot make more
    # rejections than levels paid for.  ``max_alerts_per_window`` is that cap,
    # and it is enforced in ``alert`` rather than assumed.  Measured on
    # nf_cse_cic_ids2018_v3 at pi = 1e-2: at L = 5 the uncapped procedure
    # exceeded five rejections in 73% of windows, at L = 100 in none, and the
    # power cost of moving from 5 to 100 is 0.694 -> 0.324.
    corrected_levels: int = 100
    max_alerts_per_window: int = 100
    procedure: str = "bh"
    fallback_alerts_per_window: int = 5

    def operating_point(self, calibration_size: int) -> OperatingPoint:
        return OperatingPoint(calibration_size, self.window_size, self.q, self.prevalence)

    def required_calibration(self, guarantee: str) -> float:
        if guarantee == "marginal":
            return resolution_barrier_calibration(self.q, self.prevalence)
        if guarantee == "conditional":
            return conditional_barrier_calibration(
                self.q, self.prevalence, self.delta, self.corrected_levels
            )
        raise ValueError(f"Unknown guarantee {guarantee!r}; choose from {GUARANTEES}")


@dataclass
class Certificate:
    """Everything a deployment needs to defend the number it is about to quote."""

    state: str
    guarantee: str
    calibration_size: int
    required_marginal: float
    required_conditional: float
    floor_marginal: float
    floor_conditional: float
    exchangeability: dict[str, float | bool | str] = field(default_factory=dict)
    tail_audit: dict[str, float | bool | str] = field(default_factory=dict)
    reasons: tuple[str, ...] = ()
    remedies: dict[str, dict[str, float | str]] = field(default_factory=dict)

    @property
    def claims_fdr(self) -> bool:
        return self.state in ("certified", "degraded")

    def report(self) -> dict[str, object]:
        return {
            "state": self.state,
            "guarantee": self.guarantee,
            "claims_fdr": self.claims_fdr,
            "calibration_size": float(self.calibration_size),
            "required_calibration_marginal": self.required_marginal,
            "required_calibration_conditional": self.required_conditional,
            "pvalue_floor_marginal": self.floor_marginal,
            "pvalue_floor_conditional": self.floor_conditional,
            "reasons": list(self.reasons),
            "exchangeability_audit": self.exchangeability,
            "tail_audit": self.tail_audit,
            "remedies": self.remedies,
        }


@dataclass
class AlertDecision:
    """One window, scored and decided, with the claim attached."""

    rejected: np.ndarray
    pvalues: np.ndarray
    state: str
    guarantee: str
    claimed_fdr: float | None
    mechanism: str

    def summary(self) -> dict[str, object]:
        return {
            "alerts": int(self.rejected.sum()),
            "alert_rate": float(self.rejected.mean()) if len(self.rejected) else 0.0,
            "state": self.state,
            "guarantee": self.guarantee,
            "claimed_fdr": self.claimed_fdr,
            "mechanism": self.mechanism,
            "smallest_pvalue": float(self.pvalues.min()) if len(self.pvalues) else 1.0,
        }


def permutation_audit_threshold(
    calibration_scores: np.ndarray,
    held_out_known_scores: np.ndarray,
    audit_alpha: float = 0.05,
    permutations: int = 200,
    seed: int = 0,
) -> float:
    """The critical value the two-sample bound is trying to approximate.

    Under exchangeability the labels ``calibration`` and ``audit`` carry no
    information, so pooling the two samples and re-splitting them at the same
    sizes draws from the null distribution of the audit statistic itself.  The
    ``1 - alpha`` quantile of that distribution is the threshold with the
    intended size, and unlike the Smirnov form it needs no asymptotics and is
    unaffected by the conformal ``+1`` or by ties in the scores.
    """
    pooled = np.concatenate([
        np.asarray(calibration_scores).reshape(-1),
        np.asarray(held_out_known_scores).reshape(-1),
    ])
    n, m = len(calibration_scores), len(held_out_known_scores)
    grid = (np.arange(1, m + 1, dtype=np.float64)) / m
    rng = np.random.default_rng(seed)
    statistics = np.empty(permutations, dtype=np.float64)
    for index in range(permutations):
        shuffled = rng.permutation(pooled)
        reference = np.sort(shuffled[:n])
        sample = shuffled[n:]
        # conformal p-value of each audit point against the permuted reference
        exceedances = n - np.searchsorted(reference, sample, side="left")
        ordered = np.sort((1.0 + exceedances) / (n + 1.0))
        statistics[index] = np.max(grid - ordered)
    return float(np.quantile(statistics, 1.0 - audit_alpha))


def exchangeability_audit(
    calibration_scores: np.ndarray,
    held_out_known_scores: np.ndarray,
    audit_alpha: float = 0.05,
    threshold: str = "dkw",
    permutations: int = 200,
    seed: int = 0,
) -> dict[str, float | bool | str]:
    """One-sided DKW test that held-out known traffic still looks calibrated.

    Conformal validity needs the calibration sample and the known traffic being
    scored to be exchangeable.  Nothing about a deployment guarantees that --
    the network changes, the capture point moves, a new benign service appears
    -- and when it stops holding the p-values are anti-conservative in exactly
    the tail the alerting policy reads.  The test is one-sided because only one
    direction is dangerous: known traffic yielding *smaller* p-values than
    promised is a false-alarm budget being spent without anyone asking.

    The critical value is the *two-sample* bound.  The reference distribution
    here is not known -- it is the empirical distribution of a finite
    calibration sample -- so the usual one-sample DKW value is too tight and
    refuses traffic that is perfectly exchangeable.  Using
    ``sqrt(ln(1/alpha) (1/n + 1/m) / 2)`` puts the false-refusal rate back
    near ``alpha``, which matters for a gate whose only job is to be believed
    when it fires.  Measured over 300 exchangeable draws at n = 30,000 and
    m = 20,000 the rate is 0.070 against a nominal 0.05 -- the Smirnov bound is
    asymptotic and the conformal ``+1`` shifts it slightly -- while a mean
    shift of 0.05 standard deviations in the scored traffic is already caught.
    """
    calibration_scores = np.asarray(calibration_scores).reshape(-1)
    p_values = conformal_pvalues(calibration_scores, held_out_known_scores)
    ordered = np.sort(p_values)
    empirical = np.arange(1, len(ordered) + 1, dtype=np.float64) / len(ordered)
    violation = float(np.max(empirical - ordered))
    bound = float(
        math.sqrt(
            0.5
            * math.log(1.0 / audit_alpha)
            * (1.0 / len(calibration_scores) + 1.0 / len(ordered))
        )
    )
    if threshold == "permutation":
        bound = permutation_audit_threshold(
            calibration_scores, held_out_known_scores, audit_alpha, permutations, seed
        )
    elif threshold != "dkw":
        raise ValueError(f"unknown audit threshold {threshold!r}")
    return {
        "audit_size": float(len(ordered)),
        "calibration_size": float(len(calibration_scores)),
        "audit_threshold_rule": threshold,
        "superuniform_violation": violation,
        "superuniform_dkw_bound": bound,
        "superuniform_audit_rejected": bool(violation > bound),
        "superuniform_audit_status": "rejected" if violation > bound else "not_rejected",
        "median_known_pvalue": float(np.median(p_values)),
    }


@dataclass
class PactAlerting:
    """Certify a calibration budget, then alert only within what it supports."""

    budget: AlertBudget = field(default_factory=AlertBudget)
    guarantee: str = "conditional"
    tail_policy: str = "off"
    tail_anchor_exceedances: int = 250
    tail_confidence: float = 0.9
    audit_alpha: float = 0.05
    audit_threshold: str = "dkw"
    audit_permutations: int = 200
    calibration_scores: np.ndarray = field(default_factory=lambda: np.zeros(0))
    tail: TailExtendedCalibration | None = None
    certificate: Certificate | None = None

    def fit(
        self,
        calibration_scores: np.ndarray,
        held_out_known_scores: np.ndarray | None = None,
    ) -> "PactAlerting":
        if self.guarantee not in GUARANTEES:
            raise ValueError(f"guarantee must be one of {GUARANTEES}")
        if self.guarantee == "conditional" and (
            self.budget.corrected_levels < self.budget.max_alerts_per_window
        ):
            raise ValueError(
                "The training-conditional bound is pointwise: corrected_levels "
                f"({self.budget.corrected_levels}) must be at least "
                f"max_alerts_per_window ({self.budget.max_alerts_per_window}), or the "
                "guarantee does not cover every threshold the procedure reads"
            )
        if self.tail_policy not in TAIL_POLICIES:
            raise ValueError(f"tail_policy must be one of {TAIL_POLICIES}")
        self.calibration_scores = np.asarray(calibration_scores, dtype=np.float64).reshape(-1)
        if not len(self.calibration_scores):
            raise ValueError("calibration_scores must not be empty")

        size = len(self.calibration_scores)
        reasons: list[str] = []
        exchangeability: dict[str, float | bool | str] = {}
        tail_audit: dict[str, float | bool | str] = {}

        self.tail = None
        if self.tail_policy == "audited":
            if held_out_known_scores is None:
                raise ValueError(
                    "tail_policy='audited' needs held-out known scores; an unaudited "
                    "tail model is the thing this policy exists to prevent"
                )
            self.tail = TailExtendedCalibration(
                anchor_exceedances=min(self.tail_anchor_exceedances, max(10, size // 4)),
                confidence=self.tail_confidence,
            ).fit(self.calibration_scores)
            tail_audit = self.tail.audit(held_out_known_scores)
            if tail_audit["audit_rejected"]:
                reasons.append("tail_model_rejected_by_audit")
                self.tail = None

        if held_out_known_scores is not None:
            exchangeability = exchangeability_audit(
                self.calibration_scores, held_out_known_scores, self.audit_alpha,
                threshold=self.audit_threshold, permutations=self.audit_permutations
            )
            if exchangeability["superuniform_audit_rejected"]:
                reasons.append("calibration_not_exchangeable_with_scored_traffic")

        required_marginal = self.budget.required_calibration("marginal")
        required_conditional = self.budget.required_calibration("conditional")
        effective_size = self._effective_calibration_size()
        if effective_size < required_marginal:
            reasons.append("below_marginal_resolution_barrier")
        elif self.guarantee == "conditional" and effective_size < required_conditional:
            reasons.append("below_training_conditional_resolution_barrier")

        if "calibration_not_exchangeable_with_scored_traffic" in reasons or (
            "below_marginal_resolution_barrier" in reasons
        ):
            state = "refuse"
        elif "below_training_conditional_resolution_barrier" in reasons:
            state = "degraded"
        else:
            state = "certified"

        self.certificate = Certificate(
            state=state,
            guarantee=self.guarantee,
            calibration_size=size,
            required_marginal=required_marginal,
            required_conditional=required_conditional,
            floor_marginal=distribution_free_floor(size),
            floor_conditional=training_conditional_floor(
                size, self.budget.delta, self.budget.corrected_levels
            ),
            exchangeability=exchangeability,
            tail_audit=tail_audit,
            reasons=tuple(reasons),
            remedies=escape_routes(self.budget.operating_point(size)),
        )
        return self

    def _effective_calibration_size(self) -> int:
        """Calibration size after the tail model, if any, has been accepted.

        A tail model that survives its audit lifts the floor limit, so the
        barrier should be evaluated against the size that would produce the
        same floor rather than against the raw count.  Expressing the gain as
        an equivalent sample size keeps one number in the certificate instead
        of two parallel barriers.
        """
        size = len(self.calibration_scores)
        if self.tail is None:
            return size
        smallest = float(self.tail.anchor_pvalue) * 1e-3
        return max(size, int(round(1.0 / max(smallest, 1e-12))) - 1)

    def pvalues(self, scores: np.ndarray) -> np.ndarray:
        if self.certificate is None:
            raise RuntimeError("PactAlerting is not fitted")
        if self.tail is not None:
            return self.tail.pvalues(scores)
        if self.guarantee == "conditional":
            return training_conditional_pvalues(
                self.calibration_scores,
                scores,
                self.budget.delta,
                self.budget.corrected_levels,
            )
        return conformal_pvalues(self.calibration_scores, scores)

    def alert(self, window_scores: np.ndarray) -> AlertDecision:
        """Decide one window under whatever claim the certificate supports."""
        if self.certificate is None:
            raise RuntimeError("PactAlerting is not fitted")
        scores = np.asarray(window_scores, dtype=np.float64).reshape(-1)
        p_values = self.pvalues(scores)
        if not self.certificate.claims_fdr:
            # No defensible false-discovery claim: promise a workload instead.
            # A fixed count is honest in a way an uncertified q is not -- the
            # operator knows how many flows they will look at and is told
            # nothing about how many are real.
            budget = min(self.budget.fallback_alerts_per_window, len(scores))
            rejected = np.zeros(len(scores), dtype=bool)
            if budget:
                rejected[np.argsort(p_values, kind="stable")[:budget]] = True
            return AlertDecision(
                rejected=rejected,
                pvalues=p_values,
                state=self.certificate.state,
                guarantee="none",
                claimed_fdr=None,
                mechanism="fixed_alarm_budget",
            )
        procedure = benjamini_yekutieli if self.budget.procedure == "by" else benjamini_hochberg
        rejected = procedure(p_values, self.budget.q)
        # Enforce the cap the correction was bought for.  Dropping the weakest
        # rejections keeps the discovery set a subset of BH's, so the false
        # discovery proportion cannot rise.
        if rejected.sum() > self.budget.max_alerts_per_window:
            keep = np.argsort(p_values, kind="stable")[: self.budget.max_alerts_per_window]
            capped = np.zeros(len(p_values), dtype=bool)
            capped[keep] = True
            rejected = capped & rejected
        return AlertDecision(
            rejected=rejected,
            pvalues=p_values,
            state=self.certificate.state,
            guarantee=self.certificate.guarantee
            if self.certificate.state == "certified"
            else "marginal",
            claimed_fdr=float(self.budget.q),
            mechanism=f"{self.budget.procedure}_{'tail_extended' if self.tail else 'conformal'}",
        )

    def sizing_advice(self) -> dict[str, float | str]:
        """How many more verified-known flows would buy the requested claim."""
        if self.certificate is None:
            raise RuntimeError("PactAlerting is not fitted")
        certificate = self.certificate
        required = (
            certificate.required_conditional
            if self.guarantee == "conditional"
            else certificate.required_marginal
        )
        shortfall = max(0.0, math.ceil(required) - certificate.calibration_size)
        return {
            "guarantee": self.guarantee,
            "required_calibration": float(math.ceil(required)),
            "have": float(certificate.calibration_size),
            "shortfall": float(shortfall),
            "reachable_prevalence_now": float(
                distribution_free_floor(certificate.calibration_size) / self.budget.q
            ),
            "advice": (
                "calibration budget is sufficient"
                if shortfall <= 0
                else f"acquire {int(shortfall)} more verified-known flows, "
                "or raise q, or alert on a coarser unit than the flow"
            ),
        }
