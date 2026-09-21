# Conformal FDR Prototype

- Dataset: `ciciomt2024` / `Z1`
- Alert window: 2000 flows
- Repeated batches: 200
- Tuning/FDR calibration: 9997 / 10003
- Every detector is conformalized with the same held-out calibration protocol.
- Empirical FDR is the mean realised FDP; `P(any)` separates control from a trivial no-alert result.
- Marginal conformal calibration is primary; predicted-class Mondrian is a sensitivity analysis.
- A rejected held-out-known validity audit blocks any formal FDR claim.

## BH at q=0.1

| Method | Prevalence | Empirical FDR | Power | Mean alerts | P(any) | Min rejections at p_min |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hedl | 0.5 | 0.0755 | 1.0000 | 1081.74 | 1.000 | 2 |
| hedl | 0.25 | 0.3652 | 0.0005 | 1.64 | 0.410 | 2 |
| hedl | 0.1 | 0.4893 | 0.0005 | 1.97 | 0.510 | 2 |
| hedl | 0.05 | 0.4617 | 0.0009 | 1.94 | 0.480 | 2 |
| hedl | 0.01 | 0.5037 | 0.0015 | 2.09 | 0.510 | 2 |
| hedl | 0.001 | 0.4900 | 0.0000 | 1.91 | 0.490 | 2 |

## Validity and Deployment Gate

| Method | Calibration | Violation | DKW bound | Audit | Deployment status | Blockers |
| --- | --- | ---: | ---: | --- | --- | --- |
| hedl | marginal | 0.0661 | 0.0089 | rejected | not_deployable | held_out_known_superuniformity_rejected, empirical_fdr_upper_ci_exceeds_nominal_q, zero_unknown_detection_power, mostly_abstains |
| hedl | mondrian | 0.1768 | 0.0089 | rejected | not_deployable | held_out_known_superuniformity_rejected, zero_unknown_detection_power, mostly_abstains |

## Interpretation Guardrails

- BH control relies on the exchangeability/PRDS conditions studied by Bates et al. (2023).
- Network-flow dependence can violate those assumptions; BY is included as a conservative sensitivity analysis.
- BY cannot repair invalid marginal p-values; inspect `null_pvalue_diagnostics` before interpreting FDR.
- FDR is an expectation, not a guarantee that every realised batch has FDP below q.
- Zero empirical FDR with near-zero `P(any)` is abstention, not useful detection.
- The minimum attainable p-value is finite; batch size and calibration size can force zero power.
