import numpy as np
import torch
import yaml
from pathlib import Path

from experiments.open_set.data import (
    cap_open_set_data,
    derive_multi_unknown,
    hold_out_groups,
    load_rotation,
    source_fitted_cross_domain,
    source_fitted_leave_one_domain_out,
)
from experiments.open_set.direct_baselines import run_direct_baseline
from experiments.open_set.run import deployment_threshold, prevalence_metrics
from experiments.open_set.run_full import build_jobs, method_list
from experiments.open_set.metrics import evaluate_open_set, oscr
from experiments.open_set.models import HyperbolicEvidentialModel
from experiments.open_set.conformal import ConformalFusionScorer, conformal_pvalue
from experiments.open_set.anchor_transport import (
    DEFAULT_REFERENCE_POLICIES,
    ReferencePolicy,
    allocate_target_budget,
    build_reference,
    select_reference_policy,
)
from experiments.open_set.pact import AlertBudget, PactAlerting, exchangeability_audit
from experiments.open_set.resolution import (
    OperatingPoint,
    conformal_evalue_ceiling,
    contamination_floor,
    mondrian_break_even,
    evalue_barrier_rejections,
    conditional_barrier_calibration,
    distribution_free_floor,
    minimum_rejections,
    resolution_barrier_calibration,
    screening_invariance_report,
    training_conditional_floor,
    training_conditional_pvalues,
)
from experiments.open_set.tail import TailExtendedCalibration, fit_generalised_pareto
from experiments.open_set.fdr import (
    conformal_evalues,
    e_benjamini_hochberg,
    harmonic_conformal_evalues,
    storey_pi_zero,
)
from experiments.open_set.fdr import (
    benjamini_hochberg,
    benjamini_yekutieli,
    conformal_pvalues,
    evaluate_fdr_curve,
    minimum_bh_rejections,
    mondrian_group_diagnostics,
    mondrian_conformal_pvalues,
    null_pvalue_diagnostics,
    sample_batch_to_prevalence,
    stratified_calibration_split,
)
from experiments.open_set.features import FeaturePipeline, PiecewiseLinearEncoding, QuantileNormalizer
from experiments.open_set.models import PROFILES
from experiments.open_set.scorers import KnownOnlyHEDLScorer
from sklearn.metrics import roc_auc_score


MATRIX_PATH = Path(__file__).resolve().parents[1] / "experiments" / "open_set" / "rq_matrix.yaml"
CLONE_MANIFEST_PATH = Path(__file__).resolve().parents[1] / "baselines" / "SOTA_CLONE_MANIFEST.yaml"


def test_loao_rotation_has_no_unknown_leakage():
    data = load_rotation("cicids2017", "Z1")
    unknown = set(data.unknown_families)
    assert not unknown.intersection(data.train.families)
    assert not unknown.intersection(data.calibration.families)
    assert np.any(data.unknown_test_mask)


def test_multi_unknown_removes_families_from_train_and_calibration():
    data = load_rotation("cidds_001", "Z1")
    derived = derive_multi_unknown(data, ["bruteforce"])
    assert "bruteforce" in derived.unknown_families
    assert "bruteforce" not in set(derived.train.families)
    assert "bruteforce" not in set(derived.calibration.families)
    assert "bruteforce" in set(derived.test.families)


def test_holding_out_a_group_member_holds_out_its_twins():
    data = load_rotation("cicids2017", "Z3")
    grouped = hold_out_groups(data, [["web_attack_brute_force", "web_attack_xss"]])
    assert set(grouped.unknown_families) == {"web_attack_brute_force", "web_attack_xss"}
    assert "web_attack_brute_force" not in grouped.known_families
    assert "web_attack_brute_force" not in set(grouped.train.families)
    assert "web_attack_brute_force" not in set(grouped.calibration.families)
    assert len(grouped.test.x) == len(data.test.x)
    assert grouped.unknown_test_mask.sum() > data.unknown_test_mask.sum()


def test_holdout_groups_leave_untouched_rotations_identical():
    data = load_rotation("cicids2017", "Z1")
    grouped = hold_out_groups(data, [["web_attack_brute_force", "web_attack_xss"]])
    assert grouped is data


def test_oscr_is_bounded():
    labels = np.array([0, 1, 0, 1])
    predictions = np.array([0, 1, 1, 1])
    known_scores = np.array([0.1, 0.2, 0.7, 0.3])
    unknown_scores = np.array([0.8, 0.9, 0.6])
    value = oscr(labels, predictions, known_scores, unknown_scores)
    assert 0.0 <= value <= 1.0


def test_open_set_metrics_are_bounded():
    labels = np.array([0, 1, 0, -1, -1])
    predictions = np.array([0, 1, 1, 0, 1])
    scores = np.array([0.1, 0.2, 0.4, 0.8, 0.9])
    metrics = evaluate_open_set(labels, predictions, scores, threshold=0.7)
    for key, value in metrics.items():
        assert 0.0 <= value <= 1.0, key
    assert metrics["far"] == 0.0
    assert metrics["frr"] == 0.0


def test_cross_domain_uses_common_schema():
    train_x, train_y, calibration_x, calibration_y, target_x, target_y, shared = source_fitted_cross_domain(
        "nf_unsw_nb15_v3",
        "nf_ton_iot_v3",
        max_rows=500,
    )
    assert train_x.shape[1] == calibration_x.shape[1] == target_x.shape[1] == 49
    assert len(train_x) == len(train_y)
    assert len(calibration_x) == len(calibration_y)
    assert len(target_x) == len(target_y)
    assert "benign" in shared


def test_each_protocol_has_exactly_five_q1_primary_baselines():
    matrix = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))
    baseline_sets = []
    for protocol_name, rq in matrix["protocols"].items():
        baselines = rq["primary_sota"]
        baseline_sets.append(frozenset(baselines))
        assert len(baselines) == 5, protocol_name
        assert len(set(baselines)) == 5, protocol_name
        assert "hedl" not in baselines, protocol_name
        for method in baselines:
            assert matrix["methods"][method]["venue_tier"] == "Q1", (protocol_name, method)
    assert len(set(baseline_sets)) == 3
    assert set.intersection(*(set(baselines) for baselines in baseline_sets)) == {
        "closr",
        "efc",
        "renoir_dml",
    }



def test_research_questions_are_ordered_and_reference_real_protocols():
    matrix = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))
    questions = matrix["research_questions"]
    priorities = [config["priority"] for config in questions.values()]
    assert priorities == sorted(priorities) == list(range(1, len(questions) + 1))
    for name, config in questions.items():
        assert config["question"].endswith("?"), name
        assert config["claim_gate"], name
        for protocol in config["protocols"]:
            assert protocol in matrix["protocols"], (name, protocol)


def test_protocols_are_not_named_after_research_questions():
    # The whole point of version 4: a protocol identifier must say what it runs,
    # so that "RQ3" can never again mean both a paper section and a CLI flag.
    matrix = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))
    assert set(matrix["protocols"]) == {"loao", "shift", "prevalence"}
    assert matrix["version"] >= 4


def test_out_of_scope_claims_are_recorded_with_reasons():
    matrix = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))
    out_of_scope = matrix["out_of_scope"]
    assert "cross_dataset_open_set_transfer" in out_of_scope
    assert "hyperbolic_geometry_as_contribution" in out_of_scope
    for claim, reason in out_of_scope.items():
        assert len(reason) > 40, claim


def test_conformal_evalues_have_unit_expectation_under_the_null():
    rng = np.random.default_rng(11)
    for top_k in (1, 10, 100):
        means = [
            conformal_evalues(rng.normal(size=400), rng.normal(size=40), top_k=top_k).mean()
            for _ in range(3000)
        ]
        assert abs(float(np.mean(means)) - 1.0) < 0.12, top_k


def test_no_conformal_evalue_can_exceed_the_calibration_ceiling():
    rng = np.random.default_rng(13)
    calibration = rng.normal(size=500)
    extreme = np.array([1e6])
    ceiling = conformal_evalue_ceiling(len(calibration))
    assert conformal_evalues(calibration, extreme, top_k=1)[0] <= ceiling + 1e-9
    assert harmonic_conformal_evalues(calibration, extreme)[0] <= ceiling + 1e-9
    # The indicator family attains the ceiling; the smooth one cannot.
    assert conformal_evalues(calibration, extreme, top_k=1)[0] == ceiling
    assert harmonic_conformal_evalues(calibration, extreme)[0] < ceiling


def test_ebh_meets_the_same_barrier_as_bh():
    # The paper's sharpest form: switching from p-values to e-values does not
    # buy resolution, because both are limited by the same n exchangeable
    # observations.
    for size in (1000, 12592, 23932):
        for window in (500, 2000):
            for q in (0.05, 0.1, 0.2):
                assert evalue_barrier_rejections(size, window, q) == minimum_rejections(
                    size, window, q
                )


def test_ebh_cannot_fire_below_the_barrier_even_with_a_perfect_detector():
    rng = np.random.default_rng(17)
    calibration = rng.normal(size=1000)
    window, q, attacks = 2000, 0.1, 2
    required = evalue_barrier_rejections(len(calibration), window, q)
    assert attacks < required
    # Attacks so extreme that every one of them attains the e-value ceiling.
    scores = np.concatenate([rng.normal(size=window - attacks), np.full(attacks, 1e6)])
    rejected = e_benjamini_hochberg(conformal_evalues(calibration, scores, top_k=1), q)
    assert int(rejected.sum()) < required


def test_storey_correction_is_negligible_at_low_prevalence():
    rng = np.random.default_rng(19)
    # 2 non-nulls in 2000 hypotheses: pi_0 is essentially one, so the adaptive
    # correction has nothing to give back.
    p_values = np.concatenate([rng.uniform(size=1998), np.full(2, 1e-6)])
    assert storey_pi_zero(p_values) > 0.95



def test_mondrian_grouping_costs_resolution_unless_attacks_concentrate():
    # Predicted-class grouping spreads unknowns roughly evenly (c_g ~ 1), so the
    # calibration requirement inflates by the number of groups.  This is the
    # retrodiction of the CICIoMT2024 Mondrian failure.
    pooled = mondrian_break_even(9000, groups=1, q=0.1, prevalence=0.001)
    spread = mondrian_break_even(9000, groups=9, q=0.1, prevalence=0.001, attack_concentration=1.0)
    assert spread["grouped_required_calibration"] > 8 * pooled["grouped_required_calibration"]
    assert not spread["affordable"]
    assert not spread["grouping_is_free"]
    # A grouping variable that concentrates attacks G-fold breaks even exactly.
    concentrated = mondrian_break_even(9000, groups=9, q=0.1, prevalence=0.001, attack_concentration=9.0)
    assert concentrated["grouping_is_free"]
    assert abs(
        concentrated["grouped_required_calibration"] - pooled["pooled_required_calibration"]
    ) < 1e-6


def test_mondrian_break_even_threshold_is_the_group_count():
    report = mondrian_break_even(50000, groups=5, q=0.1, prevalence=0.01, attack_concentration=3.0)
    assert report["concentration_needed_to_break_even"] == 5.0
    assert not report["grouping_is_free"]


def test_smoke_tracks_write_to_separate_result_trees():
    matrix = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))
    ours = build_jobs(matrix, "loao", "ours", method_list(matrix, "loao", "ours", False), 30, True, None)
    baselines = build_jobs(
        matrix,
        "loao",
        "baselines",
        method_list(matrix, "loao", "baselines", False),
        30,
        True,
        None,
    )
    assert ours and baselines
    assert all("ours" in job.output.parts for job in ours)
    assert all("baselines" in job.output.parts for job in baselines)
    assert ours[0].command[ours[0].command.index("--methods") + 1] == "hedl"
    assert set(baselines[0].command[baselines[0].command.index("--methods") + 1].split(",")) == set(
        matrix["protocols"]["loao"]["primary_sota"]
    )


def test_each_protocol_executes_exactly_its_five_primary_baselines():
    matrix = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))
    for protocol_name, config in matrix["protocols"].items():
        methods = method_list(matrix, protocol_name, "baselines", False)
        assert len(methods) == 5
        assert methods == config["primary_sota"]
        assert "hedl" not in methods


def test_shift_smoke_entrypoint_covers_both_arms():
    matrix = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))
    jobs = build_jobs(matrix, "shift", "ours", method_list(matrix, "shift", "ours", False), 10, True, None)
    protocols = {job.command[job.command.index("--protocol") + 1] for job in jobs}
    assert protocols == {"difficulty", "cross_domain"}


def test_full_job_matrix_has_locked_counts():
    matrix = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))
    expected = {"loao": 135, "shift": 265, "prevalence": 55}
    for protocol_name, count in expected.items():
        for track in ("ours", "baselines"):
            methods = method_list(matrix, protocol_name, track, False)
            jobs = build_jobs(
                matrix, protocol_name, track, methods, 10 if track == "ours" else 30, False, None
            )
            assert len(jobs) == count

def test_fdr_audit_is_an_official_isolated_protocol():
    matrix = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))
    jobs = build_jobs(matrix, "prevalence", "ours", ["hedl"], 3, True, "conformal_fdr_audit")
    assert len(jobs) == 1
    job = jobs[0]
    assert "experiments.open_set.run_fdr" in job.command
    assert "results\\fdr\\official\\ours" in str(job.output)
    assert "--validity-audit-alpha" in job.command


def test_partition_cap_preserves_unknown_test_samples():
    data = cap_open_set_data(load_rotation("cicids2017", "Z1"), 300)
    assert len(data.train.x) <= 300
    assert len(data.calibration.x) <= 300
    assert len(data.test.x) <= 300
    assert np.any(data.unknown_test_mask)


def test_leave_one_domain_out_uses_common_schema():
    result = source_fitted_leave_one_domain_out(
        ["nf_unsw_nb15_v3", "nf_ton_iot_v3", "nf_bot_iot_v3"],
        "nf_cse_cic_ids2018_v3",
        max_rows=300,
    )
    train_x, train_y, calibration_x, calibration_y, target_x, target_y, shared = result
    assert train_x.shape[1] == calibration_x.shape[1] == target_x.shape[1] == 49
    assert len(train_x) == len(train_y)
    assert len(calibration_x) == len(calibration_y)
    assert len(target_x) == len(target_y)
    assert "benign" in shared

def test_prevalence_sampling_reaches_targets_above_and_below_available_rate():
    labels = np.array([0] * 900 + [-1] * 100)
    predictions = np.zeros_like(labels)
    scores = np.linspace(0.0, 1.0, len(labels))
    low = prevalence_metrics(labels, predictions, scores, threshold=0.5, prevalence=0.01, seed=13)
    high = prevalence_metrics(labels, predictions, scores, threshold=0.5, prevalence=0.5, seed=13)
    assert abs(low["realized_prevalence"] - 0.01) < 0.002
    assert abs(high["realized_prevalence"] - 0.5) < 0.002
    assert low["sampled_known"] == 900
    assert high["sampled_unknown"] == 100

def test_specialist_clone_manifest_matches_rq_matrix_and_local_sources():
    root = Path(__file__).resolve().parents[1]
    matrix = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))
    manifest = yaml.safe_load(CLONE_MANIFEST_PATH.read_text(encoding="utf-8"))
    for record in manifest["verified_clones"].values():
        assert (root / record["path"]).is_dir()
        if record.get("author_mirror"):
            assert (root / record["author_mirror"]["path"]).is_dir()
    for record in manifest["supporting_artifacts_only"].values():
        for artifact in record["artifacts"]:
            assert (root / artifact["path"]).is_dir()
    assert matrix["methods"]["docpp"]["commit"] == manifest["verified_clones"]["docpp"]["commit"]
    assert matrix["methods"]["foss"]["commit"] == manifest["verified_clones"]["foss"]["commit"]
    assert matrix["methods"]["ais_nids"]["source"] is None

def test_hedl_exposes_discriminative_and_evidential_outputs():
    model = HyperbolicEvidentialModel(input_dim=6, num_classes=3, hidden_dim=12, latent_dim=4)
    outputs = model(torch.randn(8, 6))
    assert outputs["logits"].shape == (8, 3)
    assert outputs["alpha"].shape == (8, 3)
    assert outputs["embedding"].shape == (8, 4)
    assert torch.all(outputs["vacuity"] >= 0)
    assert torch.all(outputs["vacuity"] <= 1)

def test_known_only_hedl_scorer_is_bounded_and_uses_no_unknown_labels():
    rng = np.random.default_rng(13)
    train_labels = np.repeat(np.arange(3), 20)
    calibration_labels = np.repeat(np.arange(3), 10)
    train_outputs = {
        "embedding": rng.normal(size=(60, 4)),
        "alpha": rng.uniform(1.0, 4.0, size=(60, 3)),
        "vacuity": rng.uniform(0.0, 1.0, size=60),
    }
    calibration_outputs = {
        "embedding": rng.normal(size=(30, 4)),
        "alpha": rng.uniform(1.0, 4.0, size=(30, 3)),
        "vacuity": rng.uniform(0.0, 1.0, size=30),
    }
    test_outputs = {
        "embedding": rng.normal(size=(12, 4)),
        "alpha": rng.uniform(1.0, 4.0, size=(12, 3)),
        "vacuity": rng.uniform(0.0, 1.0, size=12),
    }
    scorer = KnownOnlyHEDLScorer(max_reference=40).fit(
        train_outputs,
        train_labels,
        calibration_outputs,
        calibration_labels,
    )
    scores = scorer.score(test_outputs)
    assert scores.shape == (12,)
    assert np.all(scores >= 0.0)
    assert np.all(scores <= 1.0)
    assert scorer.selected_mode in {"density", "evidential", "fused"}


def test_specialist_baseline_contracts_on_synthetic_data():
    rng = np.random.default_rng(13)
    train_x = np.vstack([rng.normal(label, 0.5, (30, 8)) for label in range(3)]).astype(np.float32)
    train_y = np.repeat(np.arange(3), 30)
    calibration_x = np.vstack([rng.normal(label, 0.5, (10, 8)) for label in range(3)]).astype(np.float32)
    calibration_y = np.repeat(np.arange(3), 10)
    test_x = np.vstack(
        [*[rng.normal(label, 0.5, (10, 8)) for label in range(3)], rng.normal(5, 0.5, (15, 8))]
    ).astype(np.float32)
    for method in ("ori", "docpp", "foss", "cd_zd_srl", "ais_nids", "usfad"):
        torch.manual_seed(13)
        output = run_direct_baseline(
            method,
            train_x,
            train_y,
            calibration_x,
            calibration_y,
            test_x,
            3,
            torch.device("cpu"),
            1,
            32,
            13,
        )
        assert output.test_predictions.shape == (45,)
        assert output.test_scores.shape == (45,)
        assert np.isfinite(output.test_scores).all()
        assert np.isfinite(output.calibration_scores).all()
        assert output.diagnostics["adapter_provenance"] in {
            "source_derived_v7_adapter",
            "paper_reimplementation",
        }

def test_smoke_jobs_use_multiple_updates_per_epoch():
    matrix = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))
    job = build_jobs(matrix, "loao", "ours", ["hedl"], 30, True, None)[0]
    batch_index = job.command.index("--batch-size")
    assert job.command[batch_index + 1] == "64"


def test_conformal_pvalue_is_marginally_valid_under_exchangeability():
    rng = np.random.default_rng(13)
    calibration = rng.normal(size=4000)
    fresh_known = rng.normal(size=20000)
    p_values = conformal_pvalue(calibration, fresh_known)
    assert np.all(p_values > 0.0)
    assert np.all(p_values <= 1.0)
    # a level-alpha test on exchangeable data must not exceed alpha by much
    for alpha in (0.01, 0.05, 0.1):
        assert float((p_values <= alpha).mean()) <= alpha * 1.35


def test_conformal_pvalue_is_monotone_decreasing_in_the_statistic():
    calibration = np.arange(100.0)
    p_values = conformal_pvalue(calibration, np.array([-5.0, 25.0, 75.0, 500.0]))
    assert np.all(np.diff(p_values) <= 0.0)


def test_budget_roles_are_disjoint_and_never_consume_unknowns():
    labels = np.array([0] * 40 + [1] * 40 + [-1] * 10)
    split = allocate_target_budget(labels, family_shots_per_class=3, verified_known_flows=20, seed=13)
    roles = [split.geometry, split.selection, split.calibration, split.audit]
    assert all(np.all(labels[rows] >= 0) for rows in roles)
    assert len(np.unique(np.concatenate(roles))) == sum(len(rows) for rows in roles)
    assert np.all(np.isin(np.flatnonzero(labels < 0), split.test))
    assert split.total_budget() == 2 * 3 * 2 + 20


def test_budget_separates_family_labels_from_verified_known_status():
    labels = np.array([0] * 200 + [1] * 200 + [-1] * 50)
    split = allocate_target_budget(labels, family_shots_per_class=5, verified_known_flows=300, seed=7)
    # The expensive half stays small while the cheap half scales: that
    # asymmetry is the whole point of allocating them separately.
    assert len(split.family_labelled()) == 20
    assert len(split.verified_known()) == 300


def test_reference_alignment_moves_each_class_onto_its_anchors():
    source_labels = np.repeat(np.arange(2), 20)
    source = np.vstack([np.tile([0.0, 0.0], (20, 1)), np.tile([4.0, 0.0], (20, 1))])
    anchors = np.vstack([np.tile([2.0, 3.0], (4, 1)), np.tile([7.0, 3.0], (4, 1))])
    anchor_labels = np.array([0] * 4 + [1] * 4)
    features, labels, diagnostics = build_reference(
        ReferencePolicy("aligned_full", 1.0, True), source, source_labels, anchors, anchor_labels
    )
    for label, centre in ((0, [2.0, 3.0]), (1, [7.0, 3.0])):
        assert np.allclose(features[labels == label].mean(axis=0), centre)
    assert diagnostics["reference_retained_source_fraction"] == 1.0


def test_anchors_only_policy_discards_every_source_row():
    source_labels = np.repeat(np.arange(2), 20)
    source = np.zeros((40, 3))
    anchors = np.ones((6, 3))
    anchor_labels = np.array([0] * 3 + [1] * 3)
    features, labels, diagnostics = build_reference(
        ReferencePolicy("anchors_only", 0.0, False), source, source_labels, anchors, anchor_labels
    )
    assert len(features) == len(anchors)
    assert diagnostics["reference_retained_source_fraction"] == 0.0


def test_reference_drops_classes_the_target_never_anchored():
    source_labels = np.repeat(np.arange(3), 10)
    source = np.repeat(np.arange(3)[:, None], 10, axis=0).astype(float).repeat(2, axis=1)
    anchors = np.zeros((4, 2))
    anchor_labels = np.array([0, 0, 1, 1])
    _, labels, diagnostics = build_reference(
        ReferencePolicy("aligned_full", 1.0, True), source, source_labels, anchors, anchor_labels
    )
    assert set(np.unique(labels)) == {0, 1}
    assert diagnostics["reference_anchored_classes"] == 2.0


def test_known_only_selection_prefers_anchors_when_the_source_has_moved():
    rng = np.random.default_rng(13)
    source_labels = np.repeat(np.arange(3), 100)
    centers = np.array([[0.0, 0.0], [5.0, 0.0], [0.0, 5.0]])
    source = np.vstack([rng.normal(center, 0.25, size=(100, 2)) for center in centers])
    shifted = centers + np.array([[3.0, 2.0], [2.0, -2.0], [-2.0, 3.0]])
    geometry = np.vstack([rng.normal(center, 0.2, size=(10, 2)) for center in shifted])
    selection = np.vstack([rng.normal(center, 0.2, size=(10, 2)) for center in shifted])
    anchor_labels = np.repeat(np.arange(3), 10)
    selected = select_reference_policy(
        source, source_labels, geometry, anchor_labels, selection, anchor_labels
    )
    assert np.mean(selected.geometry.predict(selection) == anchor_labels) > 0.95
    assert selected.policy.name in {policy.name for policy in DEFAULT_REFERENCE_POLICIES}


def test_distribution_free_floor_bounds_every_conformal_pvalue():
    rng = np.random.default_rng(3)
    calibration = rng.normal(size=250)
    p_values = conformal_pvalues(calibration, rng.normal(size=500) + 10.0)
    assert p_values.min() >= distribution_free_floor(len(calibration)) - 1e-12


def test_resolution_barrier_matches_the_rejection_count_it_is_derived_from():
    for q in (0.05, 0.1, 0.2):
        for prevalence in (0.05, 0.01, 0.001):
            required = resolution_barrier_calibration(q, prevalence)
            window = 2000
            just_below = OperatingPoint(max(1, int(required) - 1), window, q, prevalence)
            just_above = OperatingPoint(int(required) + 1, window, q, prevalence)
            assert not just_below.resolution_feasible
            assert just_above.resolution_feasible


def test_contamination_floor_is_zero_above_the_barrier_and_positive_below():
    above = contamination_floor(100000, 2000, 0.1, 0.001)
    below = contamination_floor(4000, 2000, 0.1, 0.001)
    assert above == 0.0
    # Two attacks against five required rejections leaves three nulls.
    assert abs(below - 0.6) < 1e-9


def test_contamination_floor_matches_the_measured_operating_points():
    # Cells measured in results/resolution: the bound held on every one, and
    # these are the tightest of them.
    for size, window, q, prevalence, expected in (
        (1000, 2000, 0.2, 0.001, 0.8),
        (2000, 2000, 0.2, 0.001, 0.6),
        (3000, 2000, 0.2, 0.001, 0.5),
    ):
        assert abs(contamination_floor(size, window, q, prevalence) - expected) < 1e-9


def test_window_size_cancels_out_of_the_barrier():
    barriers = {
        OperatingPoint(5000, window, 0.1, 0.01).resolution_feasible
        for window in (100, 500, 2000, 10000)
    }
    assert len(barriers) == 1


def test_fixed_threshold_screening_does_not_move_the_barrier():
    report = screening_invariance_report(8000, 2000, 0.1, 0.01)
    assert report["screened_minimum_rejections"] == report["unscreened_minimum_rejections"]
    assert report["screened_conditional_floor"] > report["unscreened_floor"]


def test_training_conditional_pvalues_are_conservative_and_cost_a_log_factor():
    rng = np.random.default_rng(5)
    calibration = rng.normal(size=4000)
    scores = rng.normal(size=1000) + 2.0
    marginal = conformal_pvalues(calibration, scores)
    conditional = training_conditional_pvalues(calibration, scores, delta=0.1)
    assert np.all(conditional >= marginal - 1e-12)
    ratio = training_conditional_floor(4000, 0.1) / distribution_free_floor(4000)
    assert 2.2 < ratio < 2.4
    assert conditional_barrier_calibration(0.1, 0.001, 0.1) > resolution_barrier_calibration(
        0.1, 0.001
    )


def test_minimum_rejections_is_one_once_the_floor_clears_the_bh_line():
    assert minimum_rejections(100000, 2000, 0.1) == 1
    assert minimum_rejections(100, 2000, 0.1) > 1


def test_tail_extension_resolves_below_the_distribution_free_floor():
    rng = np.random.default_rng(11)
    calibration = rng.lognormal(0.0, 1.0, 6000)
    tail = TailExtendedCalibration(anchor_exceedances=250, confidence=0.0).fit(calibration)
    extreme = np.array([calibration.max() * 4.0])
    assert tail.pvalues(extreme)[0] < tail.floor_pvalue
    # Below the anchor the two constructions must agree exactly, or the
    # guarantee the empirical part carries has been quietly modified.
    body = np.quantile(calibration, [0.2, 0.5, 0.8])
    assert np.allclose(tail.pvalues(body), conformal_pvalues(calibration, body))


def test_tail_confidence_bound_is_more_conservative_than_the_point_fit():
    rng = np.random.default_rng(17)
    calibration = rng.lognormal(0.0, 1.0, 6000)
    point = TailExtendedCalibration(anchor_exceedances=250, confidence=0.0).fit(calibration)
    bounded = TailExtendedCalibration(
        anchor_exceedances=250, confidence=0.9, bootstrap=60
    ).fit(calibration)
    extreme = np.array([calibration.max() * 3.0])
    assert bounded.pvalues(extreme)[0] >= point.pvalues(extreme)[0]


def test_tail_audit_rejects_a_tail_model_fitted_to_the_wrong_distribution():
    rng = np.random.default_rng(23)
    light = rng.normal(0.0, 1.0, 4000)
    tail = TailExtendedCalibration(anchor_exceedances=250, confidence=0.0).fit(light)
    heavy_known_traffic = rng.lognormal(1.0, 1.2, 20000)
    assert tail.audit(heavy_known_traffic)["audit_rejected"]


def test_generalised_pareto_fit_recovers_a_known_shape():
    from scipy.stats import genpareto

    sample = genpareto.rvs(0.2, loc=0.0, scale=1.5, size=20000, random_state=29)
    scale, shape = fit_generalised_pareto(sample)
    assert abs(shape - 0.2) < 0.05
    assert abs(scale - 1.5) < 0.15


def test_pact_refuses_when_the_calibration_cannot_support_the_budget():
    rng = np.random.default_rng(31)
    calibration = rng.normal(size=300)
    alerting = PactAlerting(
        budget=AlertBudget(q=0.1, prevalence=0.001, window_size=2000)
    ).fit(calibration)
    assert alerting.certificate.state == "refuse"
    assert not alerting.certificate.claims_fdr
    decision = alerting.alert(rng.normal(size=2000))
    assert decision.mechanism == "fixed_alarm_budget"
    assert decision.claimed_fdr is None
    assert alerting.sizing_advice()["shortfall"] > 0


def test_pact_certifies_a_budget_that_clears_the_conditional_barrier():
    # The exchangeability gate is a hypothesis test, so a handful of honest
    # draws are refused by design; what has to hold is that certification is
    # the rule and refusal the exception.
    #
    # 80,000 rather than 30,000: the level correction that makes the bound cover
    # every threshold BH reads costs ln(L/delta) instead of ln(1/delta), which
    # at q = 0.1 and pi = 1e-3 moves the requirement from 23,026 to 69,078
    # calibration flows.  Paying for a sound guarantee is what that looks like.
    states = []
    for seed in range(20):
        rng = np.random.default_rng(seed)
        alerting = PactAlerting(
            budget=AlertBudget(q=0.1, prevalence=0.001, window_size=2000)
        ).fit(rng.normal(size=80000), rng.normal(size=20000))
        states.append(alerting.certificate.state)
        assert alerting.sizing_advice()["shortfall"] == 0
    assert states.count("certified") >= 17


def test_level_correction_raises_the_calibration_requirement():
    """The sound budget costs ln(L/delta) where the pointwise one cost ln(1/delta)."""
    pointwise = AlertBudget(q=0.1, prevalence=0.001, corrected_levels=1,
                            max_alerts_per_window=1).required_calibration("conditional")
    covered = AlertBudget(q=0.1, prevalence=0.001).required_calibration("conditional")
    assert 22_000 < pointwise < 24_000
    assert 68_000 < covered < 70_000
    assert covered / pointwise > 2.9


def test_pact_refuses_when_scored_traffic_is_no_longer_exchangeable():
    rng = np.random.default_rng(41)
    calibration = rng.normal(size=30000)
    drifted_known_traffic = rng.normal(size=20000) + 1.5
    alerting = PactAlerting(
        budget=AlertBudget(q=0.1, prevalence=0.001, window_size=2000)
    ).fit(calibration, drifted_known_traffic)
    assert alerting.certificate.state == "refuse"
    assert "calibration_not_exchangeable_with_scored_traffic" in alerting.certificate.reasons


def test_exchangeability_audit_passes_on_traffic_from_the_same_source():
    rng = np.random.default_rng(43)
    audit = exchangeability_audit(rng.normal(size=20000), rng.normal(size=20000))
    assert not audit["superuniform_audit_rejected"]


def test_permutation_threshold_holds_its_size_on_a_discrete_score():
    """The asymptotic bound is the part of the gate that can be miscalibrated.

    Scores from a real detector are tied and discrete, which is where the
    Smirnov form drifts away from its nominal level; the permutation threshold
    is calibrated on the scores themselves and should not.
    """
    from experiments.open_set.pact import permutation_audit_threshold

    fired = {"dkw": 0, "permutation": 0}
    draws = 60
    for index in range(draws):
        rng = np.random.default_rng(900 + index)
        pooled = np.round(rng.normal(size=5000), 1)  # heavy ties, as scores have
        rng.shuffle(pooled)
        calibration, held_out = pooled[:3000], pooled[3000:]
        for rule in fired:
            audit = exchangeability_audit(
                calibration, held_out, 0.05, threshold=rule, permutations=120, seed=index
            )
            fired[rule] += bool(audit["superuniform_audit_rejected"])
    # Both must stay in the neighbourhood of alpha; the permutation rule is the
    # one that is allowed to be claimed as calibrated.
    assert fired["permutation"] / draws <= 0.15
    assert permutation_audit_threshold(
        np.arange(1000.0), np.arange(500.0), 0.05, 50, 0
    ) > 0.0


def test_tail_extended_scorer_removes_the_fusion_ceiling():
    rng = np.random.default_rng(47)
    centers = np.array([[0.0, 0.0, 0.0, 0.0], [4.0, 0.0, 0.0, 0.0], [0.0, 4.0, 0.0, 0.0]])
    train_labels = np.repeat(np.arange(3), 400)
    calibration_labels = np.repeat(np.arange(3), 200)
    train = {"tangent": centers[train_labels] + rng.normal(scale=0.4, size=(1200, 4))}
    calibration = {
        "tangent": centers[calibration_labels] + rng.normal(scale=0.4, size=(600, 4))
    }
    far = {"tangent": np.linspace(20.0, 60.0, 50)[:, None] * np.ones((1, 4))}
    floored = ConformalFusionScorer().fit(
        train, train_labels, calibration, calibration_labels
    )
    lifted = ConformalFusionScorer(tail_extension=True, tail_confidence=0.0).fit(
        train, train_labels, calibration, calibration_labels
    )
    # Every far-away point saturates the floored score and none of them
    # saturate the lifted one.
    assert len(np.unique(floored.score(far))) == 1
    assert len(np.unique(lifted.score(far))) == len(far["tangent"])
    assert np.all(np.diff(lifted.score(far)) > 0.0)


def test_conformal_fusion_scorer_separates_shifted_traffic_without_unknown_labels():
    rng = np.random.default_rng(13)
    centers = np.array([[0.0, 0.0, 0.0, 0.0], [4.0, 0.0, 0.0, 0.0], [0.0, 4.0, 0.0, 0.0]])
    train_labels = np.repeat(np.arange(3), 400)
    calibration_labels = np.repeat(np.arange(3), 200)
    train = {"tangent": centers[train_labels] + rng.normal(scale=0.4, size=(1200, 4))}
    calibration = {"tangent": centers[calibration_labels] + rng.normal(scale=0.4, size=(600, 4))}
    known_test = centers[rng.integers(0, 3, 300)] + rng.normal(scale=0.4, size=(300, 4))
    unknown_test = np.full((300, 4), 9.0) + rng.normal(scale=0.4, size=(300, 4))

    scorer = ConformalFusionScorer(max_reference=600, proxy_reference=600).fit(
        train, train_labels, calibration, calibration_labels
    )
    known_scores = scorer.score({"tangent": known_test})
    unknown_scores = scorer.score({"tangent": unknown_test})
    assert np.all(np.isfinite(known_scores)) and np.all(np.isfinite(unknown_scores))
    assert unknown_scores.mean() > known_scores.mean()
    assert roc_auc_score(
        np.concatenate([np.zeros(300, dtype=np.int64), np.ones(300, dtype=np.int64)]),
        np.concatenate([known_scores, unknown_scores]),
    ) > 0.95
    diagnostics = scorer.diagnostics()
    assert diagnostics["score_mode"] == "conformal_fisher_md_rmd_knn"
    for component in ("md", "rmd", "knn"):
        assert diagnostics[f"fusion_weight_{component}"] >= 0.0


def test_conformal_fusion_threshold_respects_the_calibration_budget():
    rng = np.random.default_rng(29)
    train_labels = np.repeat(np.arange(2), 500)
    centers = np.array([[0.0, 0.0, 0.0], [5.0, 0.0, 0.0]])
    train = {"tangent": centers[train_labels] + rng.normal(scale=0.5, size=(1000, 3))}
    calibration_labels = np.repeat(np.arange(2), 500)
    calibration = {"tangent": centers[calibration_labels] + rng.normal(scale=0.5, size=(1000, 3))}
    held_out_labels = rng.integers(0, 2, 4000)
    held_out = {"tangent": centers[held_out_labels] + rng.normal(scale=0.5, size=(4000, 3))}

    scorer = ConformalFusionScorer(max_reference=1000, proxy_reference=1000).fit(
        train, train_labels, calibration, calibration_labels
    )
    threshold = float(np.quantile(scorer.score(calibration), 0.99))
    false_alarm_rate = float((scorer.score(held_out) >= threshold).mean())
    assert false_alarm_rate <= 0.05


def _skewed_flow_features(rows: int = 4000, columns: int = 6, seed: int = 13) -> np.ndarray:
    """Log-normal magnitudes with a large point mass at zero, like real flow counters."""
    rng = np.random.default_rng(seed)
    values = rng.lognormal(mean=0.0, sigma=3.0, size=(rows, columns))
    values[rng.random((rows, columns)) < 0.35] = 0.0
    return values.astype(np.float32)


def test_quantile_normalizer_matches_scikit_learn():
    from sklearn.preprocessing import QuantileTransformer

    train = _skewed_flow_features()
    test = _skewed_flow_features(800, seed=29)
    reference = QuantileTransformer(
        output_distribution="normal", n_quantiles=512, subsample=1_000_000, random_state=0
    ).fit(train)
    expected = reference.transform(test)
    actual = QuantileNormalizer.fit(train, 512)(torch.from_numpy(test)).numpy()
    difference = np.abs(expected - actual)
    # scikit-learn works in float64 and the torch port in float32, so the two
    # separate only in the far tails of the inverse normal CDF, where the output
    # already saturates around +/-5.2.
    assert difference.max() < 0.05
    assert difference.mean() < 1e-3
    assert np.corrcoef(expected.ravel(), actual.ravel())[0, 1] > 0.9999


def test_quantile_normalizer_is_monotone_per_feature():
    train = _skewed_flow_features()
    normalizer = QuantileNormalizer.fit(train, 256)
    probe = np.sort(np.abs(_skewed_flow_features(500, seed=7)), axis=0)
    transformed = normalizer(torch.from_numpy(probe)).numpy()
    assert np.all(np.diff(transformed, axis=0) >= -1e-5)


def test_piecewise_linear_encoding_is_bounded_and_expands_width():
    train = _skewed_flow_features()
    encoding = PiecewiseLinearEncoding.fit(train, bins=8)
    out = encoding(torch.from_numpy(train[:64]))
    assert out.shape == (64, train.shape[1] * 8)
    assert float(out.min()) >= 0.0 and float(out.max()) <= 1.0


def test_feature_pipeline_has_no_trainable_parameters():
    pipeline = FeaturePipeline.fit(_skewed_flow_features(), quantile=True, piecewise_bins=8)
    assert sum(parameter.numel() for parameter in pipeline.parameters()) == 0
    assert pipeline.state_floats() > 0


def test_every_backbone_profile_builds_and_runs():
    train = _skewed_flow_features(rows=600, columns=9)
    for profile in PROFILES:
        model = HyperbolicEvidentialModel.build(train, num_classes=4, profile=profile)
        model.eval()
        with torch.no_grad():
            outputs = model(torch.from_numpy(train[:32]))
        assert outputs["alpha"].shape == (32, 4)
        assert outputs["tangent"].shape[0] == 32
        assert torch.all(torch.isfinite(outputs["tangent"]))
        assert model.state_floats() > 0


def test_conformal_scorer_skips_the_neighbour_index_when_knn_is_dropped():
    rng = np.random.default_rng(13)
    labels = np.repeat(np.arange(3), 300)
    centers = np.array([[0.0, 0.0, 0.0], [4.0, 0.0, 0.0], [0.0, 4.0, 0.0]])
    train = {"tangent": centers[labels] + rng.normal(scale=0.4, size=(900, 3))}
    calibration = {"tangent": centers[labels] + rng.normal(scale=0.4, size=(900, 3))}
    probe = {"tangent": rng.normal(scale=0.4, size=(50, 3))}

    reduced = ConformalFusionScorer(components=("md", "rmd"), proxy_reference=900).fit(
        train, labels, calibration, labels
    )
    assert reduced.reference is None
    assert set(reduced.calibration_statistics) == {"md", "rmd"}
    assert reduced.score(probe).shape == (50,)

    full = ConformalFusionScorer(proxy_reference=900).fit(train, labels, calibration, labels)
    assert full.reference is not None
    assert set(full.calibration_statistics) == {"md", "rmd", "knn"}


def test_predict_fast_matches_forward_predictions_and_tangent():
    torch.manual_seed(13)
    train = _skewed_flow_features(rows=800, columns=9)
    model = HyperbolicEvidentialModel.build(train, num_classes=5, profile="balanced").eval()
    with torch.no_grad():
        # move prototypes off the origin so the arg-min is not trivially shared
        model.prototypes.data = model.manifold.projx(model.prototypes.data * 60)
        batch = torch.from_numpy(train[:256])
        reference = model(batch)
    tangent, predictions = model.predict_fast(batch)
    assert torch.allclose(tangent, reference["tangent"])
    assert torch.equal(predictions, reference["prototype_logits"].argmax(dim=1))


def test_torch_conformal_scorer_reproduces_numpy_scores():
    rng = np.random.default_rng(13)
    centers = rng.normal(0.0, 3.0, size=(4, 6))
    labels = rng.integers(0, 4, 3000)
    calibration_labels = rng.integers(0, 4, 1200)
    train = {"tangent": (centers[labels] + rng.normal(size=(3000, 6))).astype(np.float32)}
    calibration = {"tangent": (centers[calibration_labels] + rng.normal(size=(1200, 6))).astype(np.float32)}
    probe = np.concatenate([centers[rng.integers(0, 4, 300)] + rng.normal(size=(300, 6)),
                            rng.normal(0.0, 6.0, size=(100, 6))]).astype(np.float32)
    for components in (("md", "rmd", "knn"), ("md", "rmd")):
        scorer = ConformalFusionScorer(components=components, proxy_reference=3000).fit(
            train, labels, calibration, calibration_labels
        )
        expected = scorer.score({"tangent": probe})
        actual = scorer.to_torch("cpu").score(torch.from_numpy(probe)).numpy()
        assert np.corrcoef(expected, actual)[0, 1] > 0.9999
        assert np.abs(expected - actual).max() < 0.05


def test_deployment_threshold_keeps_the_calibrated_value_in_distribution():
    rng = np.random.default_rng(13)
    calibration = rng.normal(size=5000)
    test = rng.normal(size=5000)
    threshold, diagnostics = deployment_threshold(calibration, test)
    assert diagnostics["threshold_mode"] == "calibrated"
    assert abs(float(np.mean(test >= threshold)) - 0.01) < 0.01


def test_deployment_threshold_survives_a_high_unknown_prevalence():
    """Most of the batch being genuinely anomalous must NOT trip the fallback:
    RQ1 rotations put up to ~70% unknown traffic in the test split."""
    rng = np.random.default_rng(29)
    calibration = rng.normal(size=5000)
    test = np.concatenate([rng.normal(size=3000), rng.normal(loc=8.0, size=7000)])
    threshold, diagnostics = deployment_threshold(calibration, test)
    assert diagnostics["threshold_mode"] == "calibrated"
    assert float(np.mean(test[7000:] >= threshold)) > 0.9  # unknowns still detected


def test_deployment_threshold_falls_back_when_the_whole_batch_looks_alien():
    rng = np.random.default_rng(7)
    calibration = rng.normal(size=5000)
    shifted = rng.normal(loc=12.0, size=5000)  # a different network: nothing resembles calibration
    threshold, diagnostics = deployment_threshold(calibration, shifted)
    assert diagnostics["threshold_mode"] == "alarm_budget_fallback"
    assert diagnostics["threshold_accepted_fraction"] < 0.2
    alarm_rate = float(np.mean(shifted >= threshold))
    assert alarm_rate <= 0.02, f"alarm rate {alarm_rate:.3f} must stay inside the 1% budget"


def test_fdr_conformal_pvalues_use_upper_tail_and_plus_one_correction():
    calibration = np.array([1.0, 2.0, 3.0, 4.0])
    scores = np.array([0.0, 3.0, 5.0])
    assert np.allclose(conformal_pvalues(calibration, scores), [1.0, 0.6, 0.2])


def test_bh_step_up_and_by_dependency_correction():
    p_values = np.array([0.001, 0.01, 0.03, 0.2, 0.8])
    bh = benjamini_hochberg(p_values, 0.05)
    by = benjamini_yekutieli(p_values, 0.05)
    assert bh.tolist() == [True, True, True, False, False]
    assert np.all(~by | bh)


def test_fdr_calibration_split_is_disjoint_and_stratified():
    labels = np.repeat(np.arange(4), 20)
    tuning, calibration = stratified_calibration_split(labels, 0.5, seed=13)
    assert not set(tuning).intersection(calibration)
    assert sorted(np.concatenate([tuning, calibration]).tolist()) == list(range(len(labels)))
    assert np.bincount(labels[tuning]).tolist() == [10, 10, 10, 10]
    assert np.bincount(labels[calibration]).tolist() == [10, 10, 10, 10]


def test_fixed_size_prevalence_batches_do_not_change_the_bh_problem_size():
    is_unknown = np.array([False] * 900 + [True] * 100)
    selected = sample_batch_to_prevalence(is_unknown, 0.1, 500, np.random.default_rng(13))
    assert len(selected) == 500
    assert int(is_unknown[selected].sum()) == 50


def test_fdr_curve_reports_power_and_finite_calibration_resolution():
    calibration = np.linspace(0.0, 1.0, 5000)
    known_scores = np.linspace(0.0, 0.8, 900)
    unknown_scores = np.linspace(5.0, 10.0, 100)
    test_scores = np.concatenate([known_scores, unknown_scores])
    is_unknown = np.array([False] * len(known_scores) + [True] * len(unknown_scores))
    results = evaluate_fdr_curve(
        calibration,
        test_scores,
        is_unknown,
        prevalences=(0.1,),
        q_levels=(0.1,),
        batch_size=100,
        repeats=5,
        seed=13,
        procedures=("bh", "by"),
    )
    metrics = results["procedures"]["bh"]["0.1"]["0.1"]
    assert results["minimum_attainable_p"] < 0.001
    assert metrics["empirical_fdr"] < 0.05
    assert metrics["mean_power"] == 1.0
    assert metrics["probability_any_alert"] == 1.0
    assert minimum_bh_rejections(5000, 100, 0.1) == 1


def test_null_pvalue_diagnostics_detects_a_shifted_known_distribution():
    calibration = np.linspace(0.0, 1.0, 5000)
    in_distribution = np.linspace(0.0, 1.0, 5000)
    shifted = np.linspace(0.8, 1.8, 5000)
    valid = null_pvalue_diagnostics(calibration, in_distribution)
    invalid = null_pvalue_diagnostics(calibration, shifted)
    assert valid["superuniform_violation"] < 0.01
    assert not valid["superuniform_audit_rejected"]
    assert invalid["superuniform_violation"] > 0.4
    assert invalid["superuniform_audit_rejected"]
    assert invalid["known_p_le_0.05"] > 0.4


def test_mondrian_pvalues_remove_a_group_mixture_shift():
    calibration_scores = np.concatenate([np.linspace(0.0, 1.0, 500), np.linspace(10.0, 11.0, 500)])
    calibration_groups = np.array([0] * 500 + [1] * 500)
    test_scores = np.concatenate([np.linspace(0.0, 1.0, 100), np.linspace(10.0, 11.0, 900)])
    test_groups = np.array([0] * 100 + [1] * 900)
    pooled = conformal_pvalues(calibration_scores, test_scores)
    mondrian = mondrian_conformal_pvalues(
        calibration_scores,
        test_scores,
        calibration_groups,
        test_groups,
    )
    pooled_violation = np.max(np.arange(1, 1001) / 1000 - np.sort(pooled))
    mondrian_violation = np.max(np.arange(1, 1001) / 1000 - np.sort(mondrian))
    assert pooled_violation > 0.3
    assert mondrian_violation < 0.01

def test_mondrian_group_diagnostics_reports_pooled_fallback():
    diagnostics = mondrian_group_diagnostics(
        np.array([0] * 40 + [1] * 10),
        np.array([0] * 50 + [1] * 25 + [2] * 25),
        minimum_group_size=30,
    )
    assert diagnostics["group_count"] == 3
    assert diagnostics["fallback_test_count"] == 50
    assert diagnostics["fallback_test_fraction"] == 0.5
