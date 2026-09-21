# Conformal FDR Prototype

- Dataset: `ciciomt2024` / `Z1`
- Alert window: 2000 flows
- Repeated batches: 200
- Tuning/FDR calibration: 9260 / 9264
- Every detector is conformalized with the same held-out calibration protocol.
- Empirical FDR is the mean realised FDP; `P(any)` separates control from a trivial no-alert result.

## BH at q=0.1

| Method | Prevalence | Empirical FDR | Power | Mean alerts | P(any) | Min rejections at p_min |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hedl | 0.5 | 0.0778 | 1.0000 | 1084.49 | 1.000 | 3 |
| hedl | 0.25 | 0.1383 | 0.0005 | 1.19 | 0.170 | 3 |
| hedl | 0.1 | 0.1751 | 0.0004 | 1.04 | 0.185 | 3 |
| hedl | 0.05 | 0.2259 | 0.0003 | 1.33 | 0.230 | 3 |
| hedl | 0.01 | 0.2294 | 0.0003 | 1.36 | 0.230 | 3 |
| hedl | 0.001 | 0.2200 | 0.0000 | 1.29 | 0.220 | 3 |

## Interpretation Guardrails

- BH control relies on the exchangeability/PRDS conditions studied by Bates et al. (2023).
- Network-flow dependence can violate those assumptions; BY is included as a conservative sensitivity analysis.
- BY cannot repair invalid marginal p-values; inspect `null_pvalue_diagnostics` before interpreting FDR.
- FDR is an expectation, not a guarantee that every realised batch has FDP below q.
- Zero empirical FDR with near-zero `P(any)` is abstention, not useful detection.
- The minimum attainable p-value is finite; batch size and calibration size can force zero power.
