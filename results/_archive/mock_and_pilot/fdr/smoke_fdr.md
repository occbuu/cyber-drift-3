# Conformal FDR Prototype

- Dataset: `ciciomt2024` / `Z1`
- Alert window: 52 flows
- Repeated batches: 50
- Tuning/FDR calibration: 253 / 247
- Every detector is conformalized with the same held-out calibration protocol.
- Empirical FDR is the mean realised FDP; `P(any)` separates control from a trivial no-alert result.

## BH at q=0.1

| Method | Prevalence | Empirical FDR | Power | Mean alerts | P(any) | Min rejections at p_min |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hedl | 0.5 | 0.0000 | 0.0000 | 0.00 | 0.000 | 3 |
| hedl | 0.25 | 0.0000 | 0.0000 | 0.00 | 0.000 | 3 |
| hedl | 0.1 | 0.0000 | 0.0000 | 0.00 | 0.000 | 3 |
| hedl | 0.05 | 0.0000 | 0.0000 | 0.00 | 0.000 | 3 |
| hedl | 0.01 | 0.0000 | 0.0000 | 0.00 | 0.000 | 3 |
| hedl | 0.001 | 0.0000 | 0.0000 | 0.00 | 0.000 | 3 |
| closr | 0.5 | 0.0000 | 0.0000 | 0.00 | 0.000 | 3 |
| closr | 0.25 | 0.0000 | 0.0000 | 0.00 | 0.000 | 3 |
| closr | 0.1 | 0.0000 | 0.0000 | 0.00 | 0.000 | 3 |
| closr | 0.05 | 0.0000 | 0.0000 | 0.00 | 0.000 | 3 |
| closr | 0.01 | 0.0000 | 0.0000 | 0.00 | 0.000 | 3 |
| closr | 0.001 | 0.0000 | 0.0000 | 0.00 | 0.000 | 3 |

## Interpretation Guardrails

- BH control relies on the exchangeability/PRDS conditions studied by Bates et al. (2023).
- Network-flow dependence can violate those assumptions; BY is included as a conservative sensitivity analysis.
- FDR is an expectation, not a guarantee that every realised batch has FDP below q.
- Zero empirical FDR with near-zero `P(any)` is abstention, not useful detection.
- The minimum attainable p-value is finite; batch size and calibration size can force zero power.
