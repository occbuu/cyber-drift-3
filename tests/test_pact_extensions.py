import numpy as np
import torch

from experiments.open_set.conformal import ConformalFusionScorer
from experiments.open_set.data import load_holdout_groups
from experiments.open_set.run_mondrian import mondrian_pvalues
from experiments.open_set.run_shift_gate import target_weights
from experiments.open_set.separability import holdout_groups


def _toy_outputs(rng, n, centres):
    labels = rng.integers(0, len(centres), n)
    tangent = centres[labels] + rng.normal(0.0, 1.0, (n, centres.shape[1]))
    return {"tangent": tangent.astype(np.float32)}, labels


def test_torch_scorer_reproduces_tail_lifted_numpy_scores():
    rng = np.random.default_rng(3)
    centres = rng.normal(0.0, 4.0, (3, 6))
    train, train_y = _toy_outputs(rng, 1500, centres)
    tuning, tuning_y = _toy_outputs(rng, 1200, centres)
    test = {"tangent": np.concatenate([
        _toy_outputs(rng, 400, centres)[0]["tangent"],
        (rng.normal(0.0, 1.0, (100, 6)) * 6.0).astype(np.float32),
    ])}
    for confidence in (0.0, 0.9):
        scorer = ConformalFusionScorer(
            tail_extension=True, tail_anchor_exceedances=100, tail_confidence=confidence
        ).fit(train, train_y, tuning, tuning_y)
        reference = scorer.score(test)
        device = scorer.to_torch("cpu").score(torch.from_numpy(test["tangent"])).numpy()
        assert np.corrcoef(np.argsort(np.argsort(reference)), np.argsort(np.argsort(device)))[0, 1] > 0.999
        # The device statistics are float32, so a flow sitting on a calibration
        # rank can move by one step; the tail region itself must agree closely.
        relative = np.abs(device - reference) / np.maximum(np.abs(reference), 1e-9)
        assert np.quantile(relative, 0.99) < 5e-3
        far = reference > np.quantile(reference, 0.9)
        assert np.allclose(device[far], reference[far], rtol=1e-4)


def test_floored_torch_scorer_is_unchanged_float32():
    rng = np.random.default_rng(5)
    centres = rng.normal(0.0, 4.0, (3, 6))
    train, train_y = _toy_outputs(rng, 800, centres)
    tuning, tuning_y = _toy_outputs(rng, 600, centres)
    scorer = ConformalFusionScorer().fit(train, train_y, tuning, tuning_y)
    scores = scorer.to_torch("cpu").score(torch.from_numpy(tuning["tangent"]))
    assert scores.dtype == torch.float32


def test_separability_groups_are_connected_components_and_never_benign():
    pairs = [
        {"family_a": "a", "family_b": "b", "balanced_accuracy": 0.6},
        {"family_a": "b", "family_b": "c", "balanced_accuracy": 0.75},
        {"family_a": "benign", "family_b": "d", "balanced_accuracy": 0.5},
        {"family_a": "c", "family_b": "e", "balanced_accuracy": 0.95},
    ]
    assert holdout_groups(pairs, 0.8) == [["a", "b", "c"]]
    assert holdout_groups(pairs, 0.7) == [["a", "b"]]


def test_holdout_threshold_reads_sensitivity_groups():
    registered = load_holdout_groups("nf_cse_cic_ids2018_v3")
    strict = load_holdout_groups("nf_cse_cic_ids2018_v3", 0.9)
    assert ["brute_force_web", "sql_injection"] in registered
    assert any({"brute_force_web", "brute_force_xss", "sql_injection"} <= set(g) for g in strict)


def test_shift_weights_interpolate_between_calibration_mix_and_focus_class():
    labels = np.array([0] * 50 + [1] * 50)
    mix = {0: 0.8, 1: 0.2}
    unshifted = target_weights(labels, mix, focus=1, magnitude=0.0)
    shifted = target_weights(labels, mix, focus=1, magnitude=1.0)
    assert np.isclose(unshifted[labels == 0].sum(), 0.8)
    assert np.isclose(shifted[labels == 1].sum(), 1.0)


def test_stratified_split_sends_singleton_classes_to_calibration():
    from experiments.open_set.fdr import stratified_calibration_split

    labels = np.array([0] * 20 + [1] * 20 + [2])
    tuning, calibration = stratified_calibration_split(labels, 0.2, 7)
    assert 40 in set(calibration.tolist())
    assert 40 not in set(tuning.tolist())
    assert len(set(tuning.tolist()) & set(calibration.tolist())) == 0
    assert len(tuning) + len(calibration) == len(labels)


def test_mondrian_pvalues_use_the_group_calibration():
    calibration = np.r_[np.zeros(100), np.ones(100) * 10.0]
    calibration_groups = np.r_[np.zeros(100, int), np.ones(100, int)]
    p = mondrian_pvalues(calibration, calibration_groups, np.array([5.0, 5.0]), np.array([0, 1]), 50)
    assert p[0] == 1.0 / 101.0
    assert p[1] == 1.0


def test_alert_cap_matches_the_level_correction_it_paid_for():
    """The Beta bound is pointwise, so BH must not read more levels than bought."""
    from experiments.open_set.pact import AlertBudget, PactAlerting

    rng = np.random.default_rng(11)
    calibration = rng.normal(size=20_000)
    budget = AlertBudget(q=0.5, prevalence=0.01, window_size=2000,
                         corrected_levels=10, max_alerts_per_window=10)
    alerting = PactAlerting(budget=budget).fit(calibration, rng.normal(size=5_000))
    window = np.r_[rng.normal(size=1900), rng.normal(6.0, 1.0, 100)]
    decision = alerting.alert(window)
    assert decision.rejected.sum() <= 10
    # Capping keeps the discovery set inside BH's, so it cannot add a false one.
    from experiments.open_set.fdr import benjamini_hochberg
    uncapped = benjamini_hochberg(alerting.pvalues(window), budget.q)
    assert np.all(decision.rejected <= uncapped)


def test_conditional_guarantee_refuses_an_uncovered_level_budget():
    from experiments.open_set.pact import AlertBudget, PactAlerting

    calibration = np.random.default_rng(3).normal(size=5_000)
    budget = AlertBudget(corrected_levels=5, max_alerts_per_window=100)
    try:
        PactAlerting(budget=budget).fit(calibration, calibration[:200])
    except ValueError as error:
        assert "corrected_levels" in str(error)
    else:
        raise AssertionError("an uncovered level budget must be refused")


def _tiny_open_set(rng, n):
    centres = rng.normal(0.0, 4.0, (3, 8))
    labels = rng.integers(0, 3, n)
    return (centres[labels] + rng.normal(0.0, 1.0, (n, 8))).astype(np.float32), labels


def test_training_flags_actually_reach_the_model():
    """An ablation flag that changes nothing is worse than no flag at all.

    This caught a real defect: --evidential-weight was accepted by the CLI,
    recorded in the capture metadata, and silently dropped one call below, so
    six GPU captures produced numbers identical to the arm they were meant to
    ablate.  Any flag whose whole purpose is to change the model belongs here.
    """
    from experiments.open_set.run import seed_everything
    from experiments.open_set.run_fdr import _score_method

    rng = np.random.default_rng(0)
    train_x, train_y = _tiny_open_set(rng, 400)
    tuning_x, tuning_y = _tiny_open_set(rng, 200)
    calibration_x, _ = _tiny_open_set(rng, 120)
    test_x, _ = _tiny_open_set(rng, 120)

    def scores(evidential_weight=1.0, margin_weight=1.0, curvature=0.0):
        seed_everything(13)
        _, test_scores, *_ = _score_method(
            "hedl", train_x, train_y, tuning_x, tuning_y, calibration_x, test_x, 3,
            torch.device("cpu"), 1, 256, 13, "balanced", ("md", "rmd", "knn"),
            curvature, False, 250, 0.0, evidential_weight, margin_weight,
        )
        return test_scores

    reference = scores()
    assert not np.allclose(reference, scores(evidential_weight=0.0)), "evidential weight is inert"
    assert not np.allclose(reference, scores(margin_weight=0.0)), "margin weight is inert"
    assert not np.allclose(reference, scores(curvature=0.5)), "curvature is inert"
