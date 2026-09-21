# Conformal FDR Prototype

- Dataset: `cicids2017` / `Z1`
- Alert window: 2000 flows
- Repeated batches: 200
- Tuning/FDR calibration: 8384 / 8388
- Every detector is conformalized with the same held-out calibration protocol.
- Empirical FDR is the mean realised FDP; `P(any)` separates control from a trivial no-alert result.
- Marginal conformal calibration is primary; predicted-class Mondrian is a sensitivity analysis.
- A rejected held-out-known validity audit blocks any formal FDR claim.

## BH at q=0.1

| Method | Prevalence | Empirical FDR | Power | Mean alerts | P(any) | Min rejections at p_min |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hedl | 0.5 | 0.0414 | 0.9163 | 955.93 | 1.000 | 3 |
| hedl | 0.25 | 0.0580 | 0.3634 | 193.00 | 1.000 | 3 |
| hedl | 0.1 | 0.0797 | 0.2870 | 62.44 | 1.000 | 3 |
| hedl | 0.05 | 0.0730 | 0.1844 | 20.54 | 0.720 | 3 |
| hedl | 0.01 | 0.0000 | 0.0000 | 0.00 | 0.000 | 3 |
| hedl | 0.001 | 0.0000 | 0.0000 | 0.00 | 0.000 | 3 |

## Validity and Deployment Gate

| Method | Calibration | Violation | DKW bound | Audit | Deployment status | Blockers |
| --- | --- | ---: | ---: | --- | --- | --- |
| hedl | marginal | 0.0035 | 0.0110 | not_rejected | not_deployable | zero_unknown_detection_power, mostly_abstains |
| hedl | mondrian | 0.0095 | 0.0110 | not_rejected | not_deployable | zero_unknown_detection_power, mostly_abstains |

## Interpretation Guardrails

- BH control relies on the exchangeability/PRDS conditions studied by Bates et al. (2023).
- Network-flow dependence can violate those assumptions; BY is included as a conservative sensitivity analysis.
- BY cannot repair invalid marginal p-values; inspect `null_pvalue_diagnostics` before interpreting FDR.
- FDR is an expectation, not a guarantee that every realised batch has FDP below q.
- Zero empirical FDR with near-zero `P(any)` is abstention, not useful detection.
- The minimum attainable p-value is finite; batch size and calibration size can force zero power.
