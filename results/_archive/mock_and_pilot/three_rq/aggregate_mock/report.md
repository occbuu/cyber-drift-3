# Three-RQ full experiment report

## Completeness

- Aggregated scalar rows: 1043
- Completeness warnings: 7

### Warnings

- incomplete C:\Users\AnThiwn\Desktop\PACT\results\three_rq\rq1\baselines\loao\cicids2017\Z1\seed_13.json: missing ['docpp', 'ori']
- incomplete C:\Users\AnThiwn\Desktop\PACT\results\three_rq\rq2\baselines\cross_domain\leave_one_environment_out\nf_unsw_nb15_v3\seed_13.json: missing ['cd_zd_srl', 'foss']
- incomplete C:\Users\AnThiwn\Desktop\PACT\results\three_rq\rq2\baselines\cross_domain\source_target\nf_unsw_nb15_v3_to_nf_ton_iot_v3\seed_13.json: missing ['cd_zd_srl', 'foss']
- incomplete C:\Users\AnThiwn\Desktop\PACT\results\three_rq\rq2\baselines\difficulty\near_far\far\cicids2017\Z2\seed_13.json: missing ['cd_zd_srl', 'foss']
- incomplete C:\Users\AnThiwn\Desktop\PACT\results\three_rq\rq2\baselines\difficulty\near_far\near\cicids2017\Z1\seed_13.json: missing ['cd_zd_srl', 'foss']
- incomplete C:\Users\AnThiwn\Desktop\PACT\results\three_rq\rq2\baselines\difficulty\openness\cicids2017\O1\seed_13.json: missing ['cd_zd_srl', 'foss']
- incomplete C:\Users\AnThiwn\Desktop\PACT\results\three_rq\rq3\baselines\prevalence\ciciomt2024\Z1\seed_13.json: missing ['ais_nids', 'usfad']

## Mean and 95% confidence intervals

| rq | method | metric | n | mean_ci95 |
| --- | --- | --- | --- | --- |
| rq1 | closr | aupr_out | 1 | 0.406253 [0.406253, 0.406253] |
| rq1 | closr | far | 1 | 0.021978 [0.021978, 0.021978] |
| rq1 | closr | fpr95 | 1 | 0.595604 [0.595604, 0.595604] |
| rq1 | closr | frr | 1 | 0.644444 [0.644444, 0.644444] |
| rq1 | closr | known_accuracy | 1 | 0.630769 [0.630769, 0.630769] |
| rq1 | closr | known_macro_f1 | 1 | 0.582225 [0.582225, 0.582225] |
| rq1 | closr | known_weighted_f1 | 1 | 0.581342 [0.581342, 0.581342] |
| rq1 | closr | open_world_macro_f1 | 1 | 0.556259 [0.556259, 0.556259] |
| rq1 | closr | oscr | 1 | 0.527912 [0.527912, 0.527912] |
| rq1 | closr | tpr_at_0_1_fpr | 1 | 0.000000 [0.000000, 0.000000] |
| rq1 | closr | tpr_at_1_fpr | 1 | 0.288889 [0.288889, 0.288889] |
| rq1 | closr | tpr_at_5_fpr | 1 | 0.355556 [0.355556, 0.355556] |
| rq1 | closr | unknown_auroc | 1 | 0.789451 [0.789451, 0.789451] |
| rq1 | closr | unknown_f1 | 1 | 0.450704 [0.450704, 0.450704] |
| rq1 | closr | unknown_precision | 1 | 0.615385 [0.615385, 0.615385] |
| rq1 | closr | unknown_recall | 1 | 0.355556 [0.355556, 0.355556] |
| rq1 | efc | aupr_out | 1 | 0.364457 [0.364457, 0.364457] |
| rq1 | efc | far | 1 | 0.004396 [0.004396, 0.004396] |
| rq1 | efc | fpr95 | 1 | 0.810989 [0.810989, 0.810989] |
| rq1 | efc | frr | 1 | 0.933333 [0.933333, 0.933333] |
| rq1 | efc | known_accuracy | 1 | 0.756044 [0.756044, 0.756044] |
| rq1 | efc | known_macro_f1 | 1 | 0.727304 [0.727304, 0.727304] |
| rq1 | efc | known_weighted_f1 | 1 | 0.727558 [0.727558, 0.727558] |
| rq1 | efc | open_world_macro_f1 | 1 | 0.656711 [0.656711, 0.656711] |
| rq1 | efc | oscr | 1 | 0.493529 [0.493529, 0.493529] |
| rq1 | efc | tpr_at_0_1_fpr | 1 | 0.000000 [0.000000, 0.000000] |
| rq1 | efc | tpr_at_1_fpr | 1 | 0.088889 [0.088889, 0.088889] |
| rq1 | efc | tpr_at_5_fpr | 1 | 0.577778 [0.577778, 0.577778] |
| rq1 | efc | unknown_auroc | 1 | 0.659023 [0.659023, 0.659023] |
| rq1 | efc | unknown_f1 | 1 | 0.120000 [0.120000, 0.120000] |
| rq1 | efc | unknown_precision | 1 | 0.600000 [0.600000, 0.600000] |
| rq1 | efc | unknown_recall | 1 | 0.066667 [0.066667, 0.066667] |
| rq1 | renoir_dml | aupr_out | 1 | 0.604233 [0.604233, 0.604233] |
| rq1 | renoir_dml | far | 1 | 0.021978 [0.021978, 0.021978] |
| rq1 | renoir_dml | fpr95 | 1 | 0.580220 [0.580220, 0.580220] |
| rq1 | renoir_dml | frr | 1 | 0.466667 [0.466667, 0.466667] |
| rq1 | renoir_dml | known_accuracy | 1 | 0.654945 [0.654945, 0.654945] |
| rq1 | renoir_dml | known_macro_f1 | 1 | 0.621991 [0.621991, 0.621991] |
| rq1 | renoir_dml | known_weighted_f1 | 1 | 0.621678 [0.621678, 0.621678] |
| rq1 | renoir_dml | open_world_macro_f1 | 1 | 0.601000 [0.601000, 0.601000] |
| rq1 | renoir_dml | oscr | 1 | 0.592674 [0.592674, 0.592674] |
| rq1 | renoir_dml | tpr_at_0_1_fpr | 1 | 0.000000 [0.000000, 0.000000] |
| rq1 | renoir_dml | tpr_at_1_fpr | 1 | 0.466667 [0.466667, 0.466667] |
| rq1 | renoir_dml | tpr_at_5_fpr | 1 | 0.711111 [0.711111, 0.711111] |
| rq1 | renoir_dml | unknown_auroc | 1 | 0.883663 [0.883663, 0.883663] |
| rq1 | renoir_dml | unknown_f1 | 1 | 0.607595 [0.607595, 0.607595] |
| rq1 | renoir_dml | unknown_precision | 1 | 0.705882 [0.705882, 0.705882] |
| rq1 | renoir_dml | unknown_recall | 1 | 0.533333 [0.533333, 0.533333] |
| rq1 | closed_backbone | delta_f1 | 3 | 0.000000 [0.000000, 0.000000] |
| rq1 | closed_backbone | known_accuracy | 3 | 0.950470 [0.815597, 1.085343] |
| rq1 | closed_backbone | known_macro_f1 | 3 | 0.865939 [0.794951, 0.936926] |
| rq1 | closed_backbone | known_weighted_f1 | 3 | 0.947976 [0.809225, 1.086726] |
| rq1 | hedl | aupr_out | 4 | 0.830151 [0.494919, 1.165383] |
| rq1 | hedl | delta_f1 | 3 | -0.004215 [-0.085036, 0.076605] |
| rq1 | hedl | far | 4 | 0.015445 [0.006155, 0.024734] |
| rq1 | hedl | fpr95 | 4 | 0.395204 [0.072221, 0.718186] |
| rq1 | hedl | frr | 4 | 0.555873 [0.369995, 0.741752] |
| rq1 | hedl | known_accuracy | 4 | 0.828752 [0.376243, 1.281260] |
| rq1 | hedl | known_macro_f1 | 4 | 0.728192 [0.303198, 1.153186] |
| rq1 | hedl | known_weighted_f1 | 4 | 0.809404 [0.299898, 1.318909] |
| rq1 | hedl | open_world_macro_f1 | 4 | 0.654798 [0.320064, 0.989532] |
| rq1 | hedl | oscr | 4 | 0.761967 [0.336959, 1.186975] |
| rq1 | hedl | scorer_density_reference_size | 4 | 3197.000000 [335.980772, 6058.019228] |
| rq1 | hedl | scorer_density_selection_margin | 4 | 0.175000 [0.095439, 0.254561] |
| rq1 | hedl | scorer_proxy_density_auroc | 4 | 0.843631 [0.736981, 0.950281] |
| rq1 | hedl | scorer_proxy_evidential_auroc | 4 | 0.864084 [0.477262, 1.250907] |
| rq1 | hedl | tpr_at_0_1_fpr | 4 | 0.000000 [0.000000, 0.000000] |
| rq1 | hedl | tpr_at_1_fpr | 4 | 0.327672 [0.022052, 0.633293] |
| rq1 | hedl | tpr_at_5_fpr | 4 | 0.625253 [0.365998, 0.884509] |
| rq1 | hedl | unknown_auroc | 4 | 0.909883 [0.837662, 0.982104] |
| rq1 | hedl | unknown_f1 | 4 | 0.582651 [0.395172, 0.770130] |
| rq1 | hedl | unknown_precision | 4 | 0.898395 [0.641298, 1.155493] |
| rq1 | hedl | unknown_recall | 4 | 0.444127 [0.258248, 0.630005] |
| rq2 | closr | aupr_out | 5 | 0.321970 [0.166941, 0.476999] |
| rq2 | closr | far | 5 | 0.010979 [-0.002665, 0.024624] |
| rq2 | closr | fpr95 | 5 | 0.671842 [0.364159, 0.979525] |
| rq2 | closr | frr | 5 | 0.846578 [0.615712, 1.077443] |
| rq2 | closr | known_accuracy | 5 | 0.424423 [0.053177, 0.795670] |
| rq2 | closr | known_macro_f1 | 5 | 0.361542 [-0.024376, 0.747460] |
| rq2 | closr | known_weighted_f1 | 5 | 0.384879 [0.035610, 0.734148] |
| rq2 | closr | open_world_macro_f1 | 5 | 0.337039 [-0.018907, 0.692985] |
| rq2 | closr | oscr | 5 | 0.333260 [0.014631, 0.651888] |
| rq2 | closr | tpr_at_0_1_fpr | 5 | 0.012800 [-0.022738, 0.048338] |
| rq2 | closr | tpr_at_1_fpr | 5 | 0.132356 [-0.047385, 0.312096] |
| rq2 | closr | tpr_at_5_fpr | 5 | 0.183822 [-0.018944, 0.386589] |
| rq2 | closr | unknown_auroc | 5 | 0.707343 [0.575956, 0.838729] |
| rq2 | closr | unknown_f1 | 5 | 0.201494 [-0.086052, 0.489039] |
| rq2 | closr | unknown_precision | 5 | 0.446154 [-0.095833, 0.988141] |
| rq2 | closr | unknown_recall | 5 | 0.153422 [-0.077443, 0.384288] |
| rq2 | efc | aupr_out | 5 | 0.363357 [0.236680, 0.490035] |
| rq2 | efc | far | 5 | 0.022759 [-0.022910, 0.068429] |
| rq2 | efc | fpr95 | 5 | 0.736327 [0.333379, 1.139275] |
| rq2 | efc | frr | 5 | 0.956682 [0.919187, 0.994177] |
| rq2 | efc | known_accuracy | 5 | 0.467402 [-0.023679, 0.958484] |
| rq2 | efc | known_macro_f1 | 5 | 0.441112 [-0.049766, 0.931990] |
| rq2 | efc | known_weighted_f1 | 5 | 0.453581 [-0.016003, 0.923165] |
| rq2 | efc | open_world_macro_f1 | 5 | 0.397924 [-0.042422, 0.838270] |
| rq2 | efc | oscr | 5 | 0.351921 [-0.046775, 0.750618] |
| rq2 | efc | tpr_at_0_1_fpr | 5 | 0.001600 [-0.002842, 0.006042] |
| rq2 | efc | tpr_at_1_fpr | 5 | 0.072356 [-0.022779, 0.167491] |
| rq2 | efc | tpr_at_5_fpr | 5 | 0.395186 [0.101980, 0.688392] |
| rq2 | efc | unknown_auroc | 5 | 0.663750 [0.472625, 0.854875] |
| rq2 | efc | unknown_f1 | 5 | 0.072714 [0.007346, 0.138081] |
| rq2 | efc | unknown_precision | 5 | 0.291491 [-0.064571, 0.647552] |
| rq2 | efc | unknown_recall | 5 | 0.043318 [0.005823, 0.080813] |
| rq2 | renoir_dml | aupr_out | 5 | 0.409699 [0.186180, 0.633218] |
| rq2 | renoir_dml | far | 5 | 0.024450 [-0.003746, 0.052647] |
| rq2 | renoir_dml | fpr95 | 5 | 0.679768 [0.354418, 1.005118] |
| rq2 | renoir_dml | frr | 5 | 0.763467 [0.423760, 1.103173] |
| rq2 | renoir_dml | known_accuracy | 5 | 0.449772 [0.108059, 0.791485] |
| rq2 | renoir_dml | known_macro_f1 | 5 | 0.387496 [-0.001858, 0.776849] |
| rq2 | renoir_dml | known_weighted_f1 | 5 | 0.424267 [0.097046, 0.751488] |
| rq2 | renoir_dml | open_world_macro_f1 | 5 | 0.363747 [-0.003465, 0.730959] |
| rq2 | renoir_dml | oscr | 5 | 0.368369 [0.014548, 0.722190] |
| rq2 | renoir_dml | tpr_at_0_1_fpr | 5 | 0.001600 [-0.002842, 0.006042] |
| rq2 | renoir_dml | tpr_at_1_fpr | 5 | 0.199467 [-0.103914, 0.502848] |
| rq2 | renoir_dml | tpr_at_5_fpr | 5 | 0.397468 [-0.015742, 0.810677] |
| rq2 | renoir_dml | unknown_auroc | 5 | 0.741753 [0.536800, 0.946707] |
| rq2 | renoir_dml | unknown_f1 | 5 | 0.278918 [-0.099888, 0.657723] |
| rq2 | renoir_dml | unknown_precision | 5 | 0.472829 [0.077841, 0.867817] |
| rq2 | renoir_dml | unknown_recall | 5 | 0.236533 [-0.103173, 0.576240] |
| rq2 | hedl | aupr_out | 5 | 0.322237 [0.095440, 0.549034] |
| rq2 | hedl | far | 5 | 0.041547 [0.001681, 0.081412] |
| rq2 | hedl | fpr95 | 5 | 0.674618 [0.321988, 1.027248] |
| rq2 | hedl | frr | 5 | 0.782933 [0.494804, 1.071062] |
| rq2 | hedl | known_accuracy | 5 | 0.246109 [-0.020927, 0.513145] |
| rq2 | hedl | known_macro_f1 | 5 | 0.200554 [-0.019830, 0.420939] |
| rq2 | hedl | known_weighted_f1 | 5 | 0.204655 [-0.011294, 0.420603] |
| rq2 | hedl | open_world_macro_f1 | 5 | 0.202353 [-0.011258, 0.415964] |
| rq2 | hedl | oscr | 5 | 0.201193 [-0.025769, 0.428155] |
| rq2 | hedl | scorer_density_reference_size | 5 | 500.000000 [500.000000, 500.000000] |
| rq2 | hedl | scorer_density_selection_margin | 5 | 0.100000 [0.100000, 0.100000] |
| rq2 | hedl | scorer_proxy_density_auroc | 5 | 0.681869 [0.570466, 0.793272] |
| rq2 | hedl | scorer_proxy_evidential_auroc | 5 | 0.499430 [0.498911, 0.499949] |
| rq2 | hedl | tpr_at_0_1_fpr | 5 | 0.000000 [0.000000, 0.000000] |
| rq2 | hedl | tpr_at_1_fpr | 5 | 0.035556 [-0.024897, 0.096008] |
| rq2 | hedl | tpr_at_5_fpr | 5 | 0.235333 [-0.103848, 0.574514] |
| rq2 | hedl | unknown_auroc | 5 | 0.691236 [0.437465, 0.945007] |
| rq2 | hedl | unknown_f1 | 5 | 0.261081 [-0.068939, 0.591101] |
| rq2 | hedl | unknown_precision | 5 | 0.351664 [-0.011761, 0.715089] |
| rq2 | hedl | unknown_recall | 5 | 0.217067 [-0.071062, 0.505196] |
| rq3 | closr | aupr_out | 7 | 0.205730 [-0.041971, 0.453431] |
| rq3 | closr | far | 7 | 0.004822 [0.000650, 0.008994] |
| rq3 | closr | fpr95 | 7 | 0.296039 [0.219927, 0.372150] |
| rq3 | closr | frr | 7 | 1.000000 [1.000000, 1.000000] |
| rq3 | closr | known_accuracy | 7 | 0.488887 [0.442428, 0.535346] |
| rq3 | closr | known_macro_f1 | 7 | 0.453535 [0.399165, 0.507904] |
| rq3 | closr | known_weighted_f1 | 7 | 0.452828 [0.406526, 0.499130] |
| rq3 | closr | latency_ms_per_flow | 1 | 0.053319 [0.053319, 0.053319] |
| rq3 | closr | open_world_macro_f1 | 7 | 0.412061 [0.356005, 0.468118] |
| rq3 | closr | oscr | 7 | 0.296952 [0.283217, 0.310687] |
| rq3 | closr | parameters | 1 | 226112.000000 [226112.000000, 226112.000000] |
| rq3 | closr | realized_prevalence | 6 | 0.152107 [-0.050466, 0.354680] |
| rq3 | closr | requested_prevalence | 6 | 0.151833 [-0.050999, 0.354666] |
| rq3 | closr | sampled_known | 6 | 293.333333 [73.563703, 513.102964] |
| rq3 | closr | sampled_unknown | 6 | 18.166667 [5.759929, 30.573405] |
| rq3 | closr | throughput_fps | 1 | 18754.970067 [18754.970067, 18754.970067] |
| rq3 | closr | tpr_at_0_1_fpr | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | closr | tpr_at_1_fpr | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | closr | tpr_at_5_fpr | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | closr | unknown_auroc | 7 | 0.717084 [0.645655, 0.788513] |
| rq3 | closr | unknown_f1 | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | closr | unknown_precision | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | closr | unknown_recall | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | efc | aupr_out | 7 | 0.232050 [0.011203, 0.452897] |
| rq3 | efc | far | 7 | 0.001206 [0.000163, 0.002248] |
| rq3 | efc | fpr95 | 7 | 0.373503 [0.334180, 0.412825] |
| rq3 | efc | frr | 7 | 1.000000 [1.000000, 1.000000] |
| rq3 | efc | known_accuracy | 7 | 0.651404 [0.630759, 0.672049] |
| rq3 | efc | known_macro_f1 | 7 | 0.578528 [0.527688, 0.629368] |
| rq3 | efc | known_weighted_f1 | 7 | 0.593977 [0.573136, 0.614818] |
| rq3 | efc | latency_ms_per_flow | 1 | 16.866255 [16.866255, 16.866255] |
| rq3 | efc | open_world_macro_f1 | 7 | 0.527591 [0.471370, 0.583813] |
| rq3 | efc | oscr | 7 | 0.515935 [0.476083, 0.555787] |
| rq3 | efc | parameters | 1 | 0.000000 [0.000000, 0.000000] |
| rq3 | efc | realized_prevalence | 6 | 0.152107 [-0.050466, 0.354680] |
| rq3 | efc | requested_prevalence | 6 | 0.151833 [-0.050999, 0.354666] |
| rq3 | efc | sampled_known | 6 | 293.333333 [73.563703, 513.102964] |
| rq3 | efc | sampled_unknown | 6 | 18.166667 [5.759929, 30.573405] |
| rq3 | efc | throughput_fps | 1 | 59.289986 [59.289986, 59.289986] |
| rq3 | efc | tpr_at_0_1_fpr | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | efc | tpr_at_1_fpr | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | efc | tpr_at_5_fpr | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | efc | unknown_auroc | 7 | 0.630147 [0.591842, 0.668452] |
| rq3 | efc | unknown_f1 | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | efc | unknown_precision | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | efc | unknown_recall | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | renoir_dml | aupr_out | 7 | 0.090213 [-0.025385, 0.205811] |
| rq3 | renoir_dml | far | 7 | 0.005433 [0.001723, 0.009142] |
| rq3 | renoir_dml | fpr95 | 7 | 0.889391 [0.863329, 0.915454] |
| rq3 | renoir_dml | frr | 7 | 1.000000 [1.000000, 1.000000] |
| rq3 | renoir_dml | known_accuracy | 7 | 0.519273 [0.499554, 0.538992] |
| rq3 | renoir_dml | known_macro_f1 | 7 | 0.488206 [0.461061, 0.515351] |
| rq3 | renoir_dml | known_weighted_f1 | 7 | 0.484156 [0.463774, 0.504538] |
| rq3 | renoir_dml | latency_ms_per_flow | 1 | 0.066812 [0.066812, 0.066812] |
| rq3 | renoir_dml | open_world_macro_f1 | 7 | 0.443985 [0.410049, 0.477921] |
| rq3 | renoir_dml | oscr | 7 | 0.065042 [0.047717, 0.082367] |
| rq3 | renoir_dml | parameters | 1 | 58111.000000 [58111.000000, 58111.000000] |
| rq3 | renoir_dml | realized_prevalence | 6 | 0.152107 [-0.050466, 0.354680] |
| rq3 | renoir_dml | requested_prevalence | 6 | 0.151833 [-0.050999, 0.354666] |
| rq3 | renoir_dml | sampled_known | 6 | 293.333333 [73.563703, 513.102964] |
| rq3 | renoir_dml | sampled_unknown | 6 | 18.166667 [5.759929, 30.573405] |
| rq3 | renoir_dml | throughput_fps | 1 | 14967.415938 [14967.415938, 14967.415938] |
| rq3 | renoir_dml | tpr_at_0_1_fpr | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | renoir_dml | tpr_at_1_fpr | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | renoir_dml | tpr_at_5_fpr | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | renoir_dml | unknown_auroc | 7 | 0.131307 [0.116420, 0.146195] |
| rq3 | renoir_dml | unknown_f1 | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | renoir_dml | unknown_precision | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | renoir_dml | unknown_recall | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | hedl | aupr_out | 7 | 0.108260 [-0.029477, 0.245997] |
| rq3 | hedl | far | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | hedl | fpr95 | 7 | 0.724162 [0.690420, 0.757904] |
| rq3 | hedl | frr | 7 | 1.000000 [1.000000, 1.000000] |
| rq3 | hedl | known_accuracy | 7 | 0.328967 [0.302811, 0.355124] |
| rq3 | hedl | known_macro_f1 | 7 | 0.227834 [0.207538, 0.248130] |
| rq3 | hedl | known_weighted_f1 | 7 | 0.225728 [0.202158, 0.249297] |
| rq3 | hedl | latency_ms_per_flow | 1 | 0.217461 [0.217461, 0.217461] |
| rq3 | hedl | open_world_macro_f1 | 7 | 0.213660 [0.190685, 0.236635] |
| rq3 | hedl | oscr | 7 | 0.097558 [0.091481, 0.103634] |
| rq3 | hedl | parameters | 1 | 4404.000000 [4404.000000, 4404.000000] |
| rq3 | hedl | realized_prevalence | 6 | 0.152107 [-0.050466, 0.354680] |
| rq3 | hedl | requested_prevalence | 6 | 0.151833 [-0.050999, 0.354666] |
| rq3 | hedl | sampled_known | 6 | 293.333333 [73.563703, 513.102964] |
| rq3 | hedl | sampled_unknown | 6 | 18.166667 [5.759929, 30.573405] |
| rq3 | hedl | scorer_density_reference_size | 1 | 500.000000 [500.000000, 500.000000] |
| rq3 | hedl | scorer_density_selection_margin | 1 | 0.100000 [0.100000, 0.100000] |
| rq3 | hedl | scorer_proxy_density_auroc | 1 | 0.622316 [0.622316, 0.622316] |
| rq3 | hedl | scorer_proxy_evidential_auroc | 1 | 0.501791 [0.501791, 0.501791] |
| rq3 | hedl | throughput_fps | 1 | 4598.521483 [4598.521483, 4598.521483] |
| rq3 | hedl | tpr_at_0_1_fpr | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | hedl | tpr_at_1_fpr | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | hedl | tpr_at_5_fpr | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | hedl | unknown_auroc | 7 | 0.309774 [0.272077, 0.347472] |
| rq3 | hedl | unknown_f1 | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | hedl | unknown_precision | 7 | 0.000000 [0.000000, 0.000000] |
| rq3 | hedl | unknown_recall | 7 | 0.000000 [0.000000, 0.000000] |

## Paired H-EDL comparisons

| rq | metric | proposed | baseline | n_pairs | mean_oriented_improvement | wins | ties | losses | wilcoxon_one_sided_p | cohens_dz | holm_adjusted_p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rq1 | aupr_out | hedl | closr | 1 | 0.11108575785876479 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | aupr_out | hedl | efc | 1 | 0.15288263341372071 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | aupr_out | hedl | renoir_dml | 1 | -0.08689410081370885 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | far | hedl | closr | 1 | -0.002197802197802197 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | far | hedl | efc | 1 | -0.01978021978021978 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | far | hedl | renoir_dml | 1 | -0.002197802197802197 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | fpr95 | hedl | closr | 1 | 0.17142857142857143 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | fpr95 | hedl | efc | 1 | 0.3868131868131868 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | fpr95 | hedl | renoir_dml | 1 | 0.1560439560439561 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | frr | hedl | closr | 1 | 0.11111111111111116 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | frr | hedl | efc | 1 | 0.4 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | frr | hedl | renoir_dml | 1 | -0.06666666666666665 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | known_accuracy | hedl | closr | 1 | -0.22857142857142854 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | known_accuracy | hedl | efc | 1 | -0.3538461538461538 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | known_accuracy | hedl | renoir_dml | 1 | -0.25274725274725274 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | known_macro_f1 | hedl | closr | 1 | -0.25462641917582823 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | known_macro_f1 | hedl | efc | 1 | -0.39970508803655475 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | known_macro_f1 | hedl | renoir_dml | 1 | -0.2943921180668371 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | known_weighted_f1 | hedl | closr | 1 | -0.25222297722262044 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | known_weighted_f1 | hedl | efc | 1 | -0.3984390109999666 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | known_weighted_f1 | hedl | renoir_dml | 1 | -0.2925590325950429 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | open_world_macro_f1 | hedl | closr | 1 | -0.21508490687357995 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | open_world_macro_f1 | hedl | efc | 1 | -0.31553731567500853 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | open_world_macro_f1 | hedl | renoir_dml | 1 | -0.25982552693077887 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | oscr | hedl | closr | 1 | -0.16134310134310131 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | oscr | hedl | efc | 1 | -0.12695970695970699 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | oscr | hedl | renoir_dml | 1 | -0.2261050061050061 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_0_1_fpr | hedl | closr | 1 | 0.0 | 0 | 1 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_0_1_fpr | hedl | efc | 1 | 0.0 | 0 | 1 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_0_1_fpr | hedl | renoir_dml | 1 | 0.0 | 0 | 1 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_1_fpr | hedl | closr | 1 | -0.19999999999999996 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_1_fpr | hedl | efc | 1 | 0.0 | 0 | 1 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_1_fpr | hedl | renoir_dml | 1 | -0.37777777777777777 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_5_fpr | hedl | closr | 1 | 0.17777777777777776 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_5_fpr | hedl | efc | 1 | -0.0444444444444444 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_5_fpr | hedl | renoir_dml | 1 | -0.1777777777777778 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_auroc | hedl | closr | 1 | 0.1135531135531137 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_auroc | hedl | efc | 1 | 0.24398046398046414 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_auroc | hedl | renoir_dml | 1 | 0.019340659340659427 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_f1 | hedl | closr | 1 | 0.09475032010243273 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_f1 | hedl | efc | 1 | 0.4254545454545454 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_f1 | hedl | renoir_dml | 1 | -0.062140391254315364 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_precision | hedl | closr | 1 | 0.04086538461538458 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_precision | hedl | efc | 1 | 0.05625000000000002 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_precision | hedl | renoir_dml | 1 | -0.049632352941176516 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_recall | hedl | closr | 1 | 0.1111111111111111 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_recall | hedl | efc | 1 | 0.4 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_recall | hedl | renoir_dml | 1 | -0.06666666666666665 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq2 | aupr_out | hedl | closr | 5 | 0.00026705188915274734 | 3 | 0 | 2 | 0.5 | 0.0021039937205900605 | 1.0 |
| rq2 | aupr_out | hedl | efc | 5 | -0.04112018977956835 | 3 | 0 | 2 | 0.6875 | -0.18782794590549956 | 1.0 |
| rq2 | aupr_out | hedl | renoir_dml | 5 | -0.08746150292557271 | 0 | 0 | 5 | 1.0 | -1.484334731571465 | 1.0 |
| rq2 | far | hedl | closr | 5 | -0.030567304686560704 | 0 | 0 | 5 | 1.0 | -0.7545864724204658 | 1.0 |
| rq2 | far | hedl | efc | 5 | -0.01878736143506384 | 0 | 0 | 5 | 1.0 | -1.3842310595087053 | 1.0 |
| rq2 | far | hedl | renoir_dml | 5 | -0.017096334591739405 | 0 | 0 | 5 | 1.0 | -0.9695901357983824 | 1.0 |
| rq2 | fpr95 | hedl | closr | 5 | -0.0027761279566531185 | 2 | 0 | 3 | 0.5625 | -0.015869443844254805 | 1.0 |
| rq2 | fpr95 | hedl | efc | 5 | 0.06170871746779845 | 2 | 0 | 3 | 0.5625 | 0.1858312006746936 | 1.0 |
| rq2 | fpr95 | hedl | renoir_dml | 5 | 0.005149602840631306 | 2 | 0 | 3 | 0.5625 | 0.03259081516757931 | 1.0 |
| rq2 | frr | hedl | closr | 5 | 0.06364444444444446 | 3 | 1 | 1 | 0.125 | 0.9135447676256532 | 0.25 |
| rq2 | frr | hedl | efc | 5 | 0.17374883720930231 | 4 | 0 | 1 | 0.0625 | 0.8325320804589936 | 0.1875 |
| rq2 | frr | hedl | renoir_dml | 5 | -0.019466666666666653 | 2 | 1 | 2 | 0.8125 | -0.44513022632294574 | 0.8125 |
| rq2 | known_accuracy | hedl | closr | 5 | -0.1783148588100448 | 1 | 0 | 4 | 0.96875 | -1.7053394780397746 | 1.0 |
| rq2 | known_accuracy | hedl | efc | 5 | -0.2212936767098693 | 1 | 0 | 4 | 0.96875 | -1.2113573214218882 | 1.0 |
| rq2 | known_accuracy | hedl | renoir_dml | 5 | -0.2036636713396013 | 0 | 0 | 5 | 1.0 | -3.1436181707541135 | 1.0 |
| rq2 | known_macro_f1 | hedl | closr | 5 | -0.16098813777640492 | 1 | 0 | 4 | 0.96875 | -1.2014978069045683 | 1.0 |
| rq2 | known_macro_f1 | hedl | efc | 5 | -0.24055760233871534 | 1 | 0 | 4 | 0.96875 | -1.1029156376980505 | 1.0 |
| rq2 | known_macro_f1 | hedl | renoir_dml | 5 | -0.18694139505379379 | 0 | 0 | 5 | 1.0 | -1.3701118316354104 | 1.0 |
| rq2 | known_weighted_f1 | hedl | closr | 5 | -0.18022444980525848 | 1 | 0 | 4 | 0.96875 | -1.5369315716914298 | 1.0 |
| rq2 | known_weighted_f1 | hedl | efc | 5 | -0.2489264617044423 | 1 | 0 | 4 | 0.96875 | -1.2014420887063033 | 1.0 |
| rq2 | known_weighted_f1 | hedl | renoir_dml | 5 | -0.21961272732344234 | 0 | 0 | 5 | 1.0 | -2.437074764596038 | 1.0 |
| rq2 | open_world_macro_f1 | hedl | closr | 5 | -0.13468655115647202 | 0 | 0 | 5 | 1.0 | -1.1672913821819106 | 1.0 |
| rq2 | open_world_macro_f1 | hedl | efc | 5 | -0.1955712738021467 | 1 | 0 | 4 | 0.9375 | -1.0609366092929597 | 1.0 |
| rq2 | open_world_macro_f1 | hedl | renoir_dml | 5 | -0.16139425428482274 | 0 | 0 | 5 | 1.0 | -1.303856049609751 | 1.0 |
| rq2 | oscr | hedl | closr | 5 | -0.1320667474834519 | 1 | 0 | 4 | 0.96875 | -1.4354729524865157 | 1.0 |
| rq2 | oscr | hedl | efc | 5 | -0.15072839330412774 | 1 | 0 | 4 | 0.96875 | -0.7820390782658853 | 1.0 |
| rq2 | oscr | hedl | renoir_dml | 5 | -0.16717596284266056 | 0 | 0 | 5 | 1.0 | -1.4863059545879065 | 1.0 |
| rq2 | tpr_at_0_1_fpr | hedl | closr | 5 | -0.0128 | 0 | 4 | 1 | 1.0 | -0.44721359549995787 | 1.0 |
| rq2 | tpr_at_0_1_fpr | hedl | efc | 5 | -0.0016 | 0 | 4 | 1 | 1.0 | -0.44721359549995787 | 1.0 |
| rq2 | tpr_at_0_1_fpr | hedl | renoir_dml | 5 | -0.0016 | 0 | 4 | 1 | 1.0 | -0.44721359549995787 | 1.0 |
| rq2 | tpr_at_1_fpr | hedl | closr | 5 | -0.09679999999999998 | 0 | 1 | 4 | 1.0 | -0.9978214964934019 | 1.0 |
| rq2 | tpr_at_1_fpr | hedl | efc | 5 | -0.0368 | 0 | 4 | 1 | 1.0 | -0.4472135954999579 | 1.0 |
| rq2 | tpr_at_1_fpr | hedl | renoir_dml | 5 | -0.16391111111111112 | 0 | 1 | 4 | 1.0 | -0.8373448915445696 | 1.0 |
| rq2 | tpr_at_5_fpr | hedl | closr | 5 | 0.051511111111111105 | 2 | 1 | 2 | 0.25 | 0.428564507345809 | 0.75 |
| rq2 | tpr_at_5_fpr | hedl | efc | 5 | -0.15985219638242892 | 1 | 0 | 4 | 0.90625 | -0.7311884312050196 | 1.0 |
| rq2 | tpr_at_5_fpr | hedl | renoir_dml | 5 | -0.1621343669250646 | 1 | 1 | 3 | 0.9375 | -0.8423125273509987 | 1.0 |
| rq2 | unknown_auroc | hedl | closr | 5 | -0.016106162747974086 | 3 | 0 | 2 | 0.5 | -0.11216854619718218 | 1.0 |
| rq2 | unknown_auroc | hedl | efc | 5 | 0.0274865741135501 | 3 | 0 | 2 | 0.5 | 0.11912741260471195 | 1.0 |
| rq2 | unknown_auroc | hedl | renoir_dml | 5 | -0.05051699540746089 | 3 | 0 | 2 | 0.65625 | -0.510650766596162 | 1.0 |
| rq2 | unknown_f1 | hedl | closr | 5 | 0.05958719741016166 | 3 | 1 | 1 | 0.125 | 0.7120139890500277 | 0.25 |
| rq2 | unknown_f1 | hedl | efc | 5 | 0.18836742447507557 | 4 | 0 | 1 | 0.0625 | 0.85394943390076 | 0.1875 |
| rq2 | unknown_f1 | hedl | renoir_dml | 5 | -0.017836595550045985 | 2 | 1 | 2 | 0.8125 | -0.43135413041482656 | 0.8125 |
| rq2 | unknown_precision | hedl | closr | 5 | -0.09448975946653966 | 3 | 1 | 1 | 0.375 | -0.23671861975287503 | 0.75 |
| rq2 | unknown_precision | hedl | efc | 5 | 0.060173571782157466 | 4 | 0 | 1 | 0.1875 | 0.5237267815564027 | 0.5625 |
| rq2 | unknown_precision | hedl | renoir_dml | 5 | -0.12116504496535456 | 0 | 1 | 4 | 1.0 | -0.6427873893865623 | 1.0 |
| rq2 | unknown_recall | hedl | closr | 5 | 0.06364444444444443 | 3 | 1 | 1 | 0.125 | 0.9135447676256531 | 0.25 |
| rq2 | unknown_recall | hedl | efc | 5 | 0.17374883720930234 | 4 | 0 | 1 | 0.0625 | 0.8325320804589939 | 0.1875 |
| rq2 | unknown_recall | hedl | renoir_dml | 5 | -0.019466666666666663 | 2 | 1 | 2 | 0.8125 | -0.445130226322946 | 0.8125 |
| rq3 | aupr_out | hedl | closr | 7 | -0.09746990340789893 | 0 | 0 | 7 | 1.0 | -0.8183497858135025 | 1.0 |
| rq3 | aupr_out | hedl | efc | 7 | -0.12378983647738384 | 0 | 0 | 7 | 1.0 | -1.2252649286505606 | 1.0 |
| rq3 | aupr_out | hedl | renoir_dml | 7 | 0.01804705787518729 | 7 | 0 | 0 | 0.0078125 | 0.7525693256365882 | 0.0234375 |
| rq3 | far | hedl | closr | 7 | 0.004822182037371911 | 4 | 3 | 0 | 0.0625 | 1.0690449676496978 | 0.125 |
| rq3 | far | hedl | efc | 7 | 0.0012055455093429777 | 4 | 3 | 0 | 0.0625 | 1.0690449676496978 | 0.125 |
| rq3 | far | hedl | renoir_dml | 7 | 0.005432682647872521 | 5 | 2 | 0 | 0.03125 | 1.354512852581 | 0.09375 |
| rq3 | fpr95 | hedl | closr | 7 | -0.4281232129333395 | 0 | 0 | 7 | 1.0 | -7.556804550767658 | 1.0 |
| rq3 | fpr95 | hedl | efc | 7 | -0.3506591861022241 | 0 | 0 | 7 | 1.0 | -4.839632696679696 | 1.0 |
| rq3 | fpr95 | hedl | renoir_dml | 7 | 0.16522928548245006 | 7 | 0 | 0 | 0.0078125 | 8.612937767062176 | 0.0234375 |
| rq3 | frr | hedl | closr | 7 | 0.0 | 0 | 7 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | frr | hedl | efc | 7 | 0.0 | 0 | 7 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | frr | hedl | renoir_dml | 7 | 0.0 | 0 | 7 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | known_accuracy | hedl | closr | 7 | -0.15992024852784348 | 0 | 0 | 7 | 1.0 | -6.920111635810557 | 1.0 |
| rq3 | known_accuracy | hedl | efc | 7 | -0.3224370566142718 | 0 | 0 | 7 | 1.0 | -10.749644197295135 | 1.0 |
| rq3 | known_accuracy | hedl | renoir_dml | 7 | -0.19030617764794983 | 0 | 0 | 7 | 1.0 | -9.466879690377816 | 1.0 |
| rq3 | known_macro_f1 | hedl | closr | 7 | -0.22570100966337633 | 0 | 0 | 7 | 1.0 | -5.368355622697612 | 1.0 |
| rq3 | known_macro_f1 | hedl | efc | 7 | -0.35069437030172773 | 0 | 0 | 7 | 1.0 | -9.14738499562385 | 1.0 |
| rq3 | known_macro_f1 | hedl | renoir_dml | 7 | -0.26037201087163797 | 0 | 0 | 7 | 1.0 | -13.366935098297413 | 1.0 |
| rq3 | known_weighted_f1 | hedl | closr | 7 | -0.2271002027088592 | 0 | 0 | 7 | 1.0 | -8.73374892473993 | 1.0 |
| rq3 | known_weighted_f1 | hedl | efc | 7 | -0.3682492445390618 | 0 | 0 | 7 | 1.0 | -11.796438277649735 | 1.0 |
| rq3 | known_weighted_f1 | hedl | renoir_dml | 7 | -0.25842832149092093 | 0 | 0 | 7 | 1.0 | -19.607540682896673 | 1.0 |
| rq3 | latency_ms_per_flow | hedl | closr | 1 | -0.1641420000087237 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq3 | latency_ms_per_flow | hedl | efc | 1 | 16.64879339998879 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | latency_ms_per_flow | hedl | renoir_dml | 1 | -0.15064940002048388 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq3 | open_world_macro_f1 | hedl | closr | 7 | -0.19840122343339653 | 0 | 0 | 7 | 1.0 | -5.4203322742376745 | 1.0 |
| rq3 | open_world_macro_f1 | hedl | efc | 7 | -0.31393134479098356 | 0 | 0 | 7 | 1.0 | -8.384035259520507 | 1.0 |
| rq3 | open_world_macro_f1 | hedl | renoir_dml | 7 | -0.2303249367320384 | 0 | 0 | 7 | 1.0 | -14.945127249774242 | 1.0 |
| rq3 | oscr | hedl | closr | 7 | -0.1993941242139879 | 0 | 0 | 7 | 1.0 | -15.159632804411942 | 1.0 |
| rq3 | oscr | hedl | efc | 7 | -0.41837722160993823 | 0 | 0 | 7 | 1.0 | -9.937483264753803 | 1.0 |
| rq3 | oscr | hedl | renoir_dml | 7 | 0.0325157499646302 | 7 | 0 | 0 | 0.0078125 | 1.6015401878253506 | 0.0234375 |
| rq3 | parameters | hedl | closr | 1 | 221708.0 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | parameters | hedl | efc | 1 | -4404.0 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq3 | parameters | hedl | renoir_dml | 1 | 53707.0 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | realized_prevalence | hedl | closr | 6 | 0.0 | 0 | 6 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | realized_prevalence | hedl | efc | 6 | 0.0 | 0 | 6 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | realized_prevalence | hedl | renoir_dml | 6 | 0.0 | 0 | 6 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | requested_prevalence | hedl | closr | 6 | 0.0 | 0 | 6 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | requested_prevalence | hedl | efc | 6 | 0.0 | 0 | 6 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | requested_prevalence | hedl | renoir_dml | 6 | 0.0 | 0 | 6 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | sampled_known | hedl | closr | 6 | 0.0 | 0 | 6 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | sampled_known | hedl | efc | 6 | 0.0 | 0 | 6 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | sampled_known | hedl | renoir_dml | 6 | 0.0 | 0 | 6 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | sampled_unknown | hedl | closr | 6 | 0.0 | 0 | 6 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | sampled_unknown | hedl | efc | 6 | 0.0 | 0 | 6 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | sampled_unknown | hedl | renoir_dml | 6 | 0.0 | 0 | 6 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | throughput_fps | hedl | closr | 1 | -14156.448583793615 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq3 | throughput_fps | hedl | efc | 1 | 4539.2314971297055 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | throughput_fps | hedl | renoir_dml | 1 | -10368.894454902013 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq3 | tpr_at_0_1_fpr | hedl | closr | 7 | 0.0 | 0 | 7 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | tpr_at_0_1_fpr | hedl | efc | 7 | 0.0 | 0 | 7 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | tpr_at_0_1_fpr | hedl | renoir_dml | 7 | 0.0 | 0 | 7 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | tpr_at_1_fpr | hedl | closr | 7 | 0.0 | 0 | 7 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | tpr_at_1_fpr | hedl | efc | 7 | 0.0 | 0 | 7 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | tpr_at_1_fpr | hedl | renoir_dml | 7 | 0.0 | 0 | 7 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | tpr_at_5_fpr | hedl | closr | 7 | 0.0 | 0 | 7 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | tpr_at_5_fpr | hedl | efc | 7 | 0.0 | 0 | 7 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | tpr_at_5_fpr | hedl | renoir_dml | 7 | 0.0 | 0 | 7 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | unknown_auroc | hedl | closr | 7 | -0.40730979071777507 | 0 | 0 | 7 | 1.0 | -9.767731057454066 | 1.0 |
| rq3 | unknown_auroc | hedl | efc | 7 | -0.3203725777630354 | 0 | 0 | 7 | 1.0 | -4.129552868010976 | 1.0 |
| rq3 | unknown_auroc | hedl | renoir_dml | 7 | 0.17846716196278026 | 7 | 0 | 0 | 0.0078125 | 5.48914664227342 | 0.0234375 |
| rq3 | unknown_f1 | hedl | closr | 7 | 0.0 | 0 | 7 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | unknown_f1 | hedl | efc | 7 | 0.0 | 0 | 7 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | unknown_f1 | hedl | renoir_dml | 7 | 0.0 | 0 | 7 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | unknown_precision | hedl | closr | 7 | 0.0 | 0 | 7 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | unknown_precision | hedl | efc | 7 | 0.0 | 0 | 7 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | unknown_precision | hedl | renoir_dml | 7 | 0.0 | 0 | 7 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | unknown_recall | hedl | closr | 7 | 0.0 | 0 | 7 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | unknown_recall | hedl | efc | 7 | 0.0 | 0 | 7 | 0 | 1.0 | 0.0 | 1.0 |
| rq3 | unknown_recall | hedl | renoir_dml | 7 | 0.0 | 0 | 7 | 0 | 1.0 | 0.0 | 1.0 |

## Average ranks

No complete rank blocks available.
