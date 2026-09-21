# Conformal FDR Prototype

- Dataset: `ciciomt2024` / `Z1`
- Alert window: 2000 flows
- Repeated batches: 200
- Tuning/FDR calibration: 9997 / 10003
- Every detector is conformalized with the same held-out calibration protocol.
- Empirical FDR is the mean realised FDP; `P(any)` separates control from a trivial no-alert result.

## BH at q=0.1

| Method | Prevalence | Empirical FDR | Power | Mean alerts | P(any) | Min rejections at p_min |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hedl | 0.5 | 0.0755 | 1.0000 | 1081.74 | 1.000 | 2 |
| hedl | 0.25 | 0.3652 | 0.0005 | 1.64 | 0.410 | 2 |
| hedl | 0.1 | 0.4893 | 0.0005 | 1.97 | 0.510 | 2 |
| hedl | 0.05 | 0.4617 | 0.0009 | 1.94 | 0.480 | 2 |
| hedl | 0.01 | 0.5037 | 0.0015 | 2.09 | 0.510 | 2 |
| hedl | 0.001 | 0.4900 | 0.0000 | 1.91 | 0.490 | 2 |
| closr | 0.5 | 0.0050 | 0.0000 | 0.01 | 0.005 | 2 |
| closr | 0.25 | 0.0200 | 0.0000 | 0.04 | 0.020 | 2 |
| closr | 0.1 | 0.0250 | 0.0000 | 0.06 | 0.025 | 2 |
| closr | 0.05 | 0.0250 | 0.0000 | 0.05 | 0.025 | 2 |
| closr | 0.01 | 0.0300 | 0.0000 | 0.06 | 0.030 | 2 |
| closr | 0.001 | 0.0350 | 0.0000 | 0.07 | 0.035 | 2 |
| efc | 0.5 | 0.0000 | 0.0000 | 0.00 | 0.000 | 2 |
| efc | 0.25 | 0.0000 | 0.0000 | 0.00 | 0.000 | 2 |
| efc | 0.1 | 0.0000 | 0.0000 | 0.00 | 0.000 | 2 |
| efc | 0.05 | 0.0000 | 0.0000 | 0.00 | 0.000 | 2 |
| efc | 0.01 | 0.0000 | 0.0000 | 0.00 | 0.000 | 2 |
| efc | 0.001 | 0.0000 | 0.0000 | 0.00 | 0.000 | 2 |
| renoir_dml | 0.5 | 0.0000 | 0.0000 | 0.00 | 0.000 | 2 |
| renoir_dml | 0.25 | 0.0000 | 0.0000 | 0.00 | 0.000 | 2 |
| renoir_dml | 0.1 | 0.0000 | 0.0000 | 0.00 | 0.000 | 2 |
| renoir_dml | 0.05 | 0.0000 | 0.0000 | 0.00 | 0.000 | 2 |
| renoir_dml | 0.01 | 0.0000 | 0.0000 | 0.00 | 0.000 | 2 |
| renoir_dml | 0.001 | 0.0000 | 0.0000 | 0.00 | 0.000 | 2 |
| ais_nids | 0.5 | 0.3100 | 0.0000 | 1.47 | 0.310 | 2 |
| ais_nids | 0.25 | 0.5250 | 0.0000 | 3.23 | 0.525 | 2 |
| ais_nids | 0.1 | 0.7700 | 0.0000 | 5.51 | 0.770 | 2 |
| ais_nids | 0.05 | 0.7350 | 0.0000 | 5.95 | 0.735 | 2 |
| ais_nids | 0.01 | 0.7400 | 0.0000 | 6.07 | 0.740 | 2 |
| ais_nids | 0.001 | 0.7550 | 0.0000 | 6.42 | 0.755 | 2 |
| usfad | 0.5 | 0.0000 | 0.0000 | 0.00 | 0.000 | 2 |
| usfad | 0.25 | 0.0050 | 0.0000 | 0.02 | 0.005 | 2 |
| usfad | 0.1 | 0.0050 | 0.0000 | 0.02 | 0.005 | 2 |
| usfad | 0.05 | 0.0150 | 0.0000 | 0.07 | 0.015 | 2 |
| usfad | 0.01 | 0.0000 | 0.0000 | 0.00 | 0.000 | 2 |
| usfad | 0.001 | 0.0050 | 0.0000 | 0.02 | 0.005 | 2 |

## Interpretation Guardrails

- BH control relies on the exchangeability/PRDS conditions studied by Bates et al. (2023).
- Network-flow dependence can violate those assumptions; BY is included as a conservative sensitivity analysis.
- FDR is an expectation, not a guarantee that every realised batch has FDP below q.
- Zero empirical FDR with near-zero `P(any)` is abstention, not useful detection.
- The minimum attainable p-value is finite; batch size and calibration size can force zero power.
