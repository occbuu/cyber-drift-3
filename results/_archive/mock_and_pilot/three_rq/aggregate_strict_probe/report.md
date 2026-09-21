# Three-RQ full experiment report

## Completeness

- Aggregated scalar rows: 187
- Completeness warnings: 2

### Warnings

- rq1/ours: 134/135 full jobs missing or incomplete
- rq1/baselines: 134/135 full jobs missing or incomplete

## Mean and 95% confidence intervals

| rq | method | metric | n | mean_ci95 |
| --- | --- | --- | --- | --- |
| rq1 | closr | aupr_out | 1 | 0.317582 [0.317582, 0.317582] |
| rq1 | closr | closed_reference_macro_f1 | 1 | 0.238625 [0.238625, 0.238625] |
| rq1 | closr | delta_f1 | 1 | 0.389295 [0.389295, 0.389295] |
| rq1 | closr | far | 1 | 0.015385 [0.015385, 0.015385] |
| rq1 | closr | fpr95 | 1 | 0.567033 [0.567033, 0.567033] |
| rq1 | closr | frr | 1 | 0.800000 [0.800000, 0.800000] |
| rq1 | closr | known_accuracy | 1 | 0.665934 [0.665934, 0.665934] |
| rq1 | closr | known_macro_f1 | 1 | 0.627919 [0.627919, 0.627919] |
| rq1 | closr | known_weighted_f1 | 1 | 0.627429 [0.627429, 0.627429] |
| rq1 | closr | open_world_macro_f1 | 1 | 0.578063 [0.578063, 0.578063] |
| rq1 | closr | oscr | 1 | 0.547546 [0.547546, 0.547546] |
| rq1 | closr | tpr_at_0_1_fpr | 1 | 0.000000 [0.000000, 0.000000] |
| rq1 | closr | tpr_at_1_fpr | 1 | 0.022222 [0.022222, 0.022222] |
| rq1 | closr | tpr_at_5_fpr | 1 | 0.355556 [0.355556, 0.355556] |
| rq1 | closr | unknown_auroc | 1 | 0.777631 [0.777631, 0.777631] |
| rq1 | closr | unknown_f1 | 1 | 0.295082 [0.295082, 0.295082] |
| rq1 | closr | unknown_precision | 1 | 0.562500 [0.562500, 0.562500] |
| rq1 | closr | unknown_recall | 1 | 0.200000 [0.200000, 0.200000] |
| rq1 | docpp | aupr_out | 1 | 0.124429 [0.124429, 0.124429] |
| rq1 | docpp | closed_reference_macro_f1 | 1 | 0.238625 [0.238625, 0.238625] |
| rq1 | docpp | delta_f1 | 1 | -0.213629 [-0.213629, -0.213629] |
| rq1 | docpp | far | 1 | 0.021978 [0.021978, 0.021978] |
| rq1 | docpp | fpr95 | 1 | 0.872527 [0.872527, 0.872527] |
| rq1 | docpp | frr | 1 | 0.911111 [0.911111, 0.911111] |
| rq1 | docpp | known_accuracy | 1 | 0.094505 [0.094505, 0.094505] |
| rq1 | docpp | known_macro_f1 | 1 | 0.024996 [0.024996, 0.024996] |
| rq1 | docpp | known_weighted_f1 | 1 | 0.025180 [0.025180, 0.025180] |
| rq1 | docpp | open_world_macro_f1 | 1 | 0.033068 [0.033068, 0.033068] |
| rq1 | docpp | oscr | 1 | 0.064469 [0.064469, 0.064469] |
| rq1 | docpp | tpr_at_0_1_fpr | 1 | 0.022222 [0.022222, 0.022222] |
| rq1 | docpp | tpr_at_1_fpr | 1 | 0.066667 [0.066667, 0.066667] |
| rq1 | docpp | tpr_at_5_fpr | 1 | 0.111111 [0.111111, 0.111111] |
| rq1 | docpp | unknown_auroc | 1 | 0.300366 [0.300366, 0.300366] |
| rq1 | docpp | unknown_f1 | 1 | 0.135593 [0.135593, 0.135593] |
| rq1 | docpp | unknown_precision | 1 | 0.285714 [0.285714, 0.285714] |
| rq1 | docpp | unknown_recall | 1 | 0.088889 [0.088889, 0.088889] |
| rq1 | efc | aupr_out | 1 | 0.364457 [0.364457, 0.364457] |
| rq1 | efc | closed_reference_macro_f1 | 1 | 0.238625 [0.238625, 0.238625] |
| rq1 | efc | delta_f1 | 1 | 0.488679 [0.488679, 0.488679] |
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
| rq1 | ori | aupr_out | 1 | 0.573254 [0.573254, 0.573254] |
| rq1 | ori | closed_reference_macro_f1 | 1 | 0.238625 [0.238625, 0.238625] |
| rq1 | ori | delta_f1 | 1 | 0.659416 [0.659416, 0.659416] |
| rq1 | ori | far | 1 | 0.010989 [0.010989, 0.010989] |
| rq1 | ori | fpr95 | 1 | 0.116484 [0.116484, 0.116484] |
| rq1 | ori | frr | 1 | 0.911111 [0.911111, 0.911111] |
| rq1 | ori | known_accuracy | 1 | 0.903297 [0.903297, 0.903297] |
| rq1 | ori | known_macro_f1 | 1 | 0.898040 [0.898040, 0.898040] |
| rq1 | ori | known_weighted_f1 | 1 | 0.898779 [0.898779, 0.898779] |
| rq1 | ori | open_world_macro_f1 | 1 | 0.806850 [0.806850, 0.806850] |
| rq1 | ori | oscr | 1 | 0.876264 [0.876264, 0.876264] |
| rq1 | ori | tpr_at_0_1_fpr | 1 | 0.000000 [0.000000, 0.000000] |
| rq1 | ori | tpr_at_1_fpr | 1 | 0.044444 [0.044444, 0.044444] |
| rq1 | ori | tpr_at_5_fpr | 1 | 0.733333 [0.733333, 0.733333] |
| rq1 | ori | unknown_auroc | 1 | 0.958681 [0.958681, 0.958681] |
| rq1 | ori | unknown_f1 | 1 | 0.148148 [0.148148, 0.148148] |
| rq1 | ori | unknown_precision | 1 | 0.444444 [0.444444, 0.444444] |
| rq1 | ori | unknown_recall | 1 | 0.088889 [0.088889, 0.088889] |
| rq1 | renoir_dml | aupr_out | 1 | 0.584469 [0.584469, 0.584469] |
| rq1 | renoir_dml | closed_reference_macro_f1 | 1 | 0.238625 [0.238625, 0.238625] |
| rq1 | renoir_dml | delta_f1 | 1 | 0.389822 [0.389822, 0.389822] |
| rq1 | renoir_dml | far | 1 | 0.019780 [0.019780, 0.019780] |
| rq1 | renoir_dml | fpr95 | 1 | 0.540659 [0.540659, 0.540659] |
| rq1 | renoir_dml | frr | 1 | 0.666667 [0.666667, 0.666667] |
| rq1 | renoir_dml | known_accuracy | 1 | 0.665934 [0.665934, 0.665934] |
| rq1 | renoir_dml | known_macro_f1 | 1 | 0.628446 [0.628446, 0.628446] |
| rq1 | renoir_dml | known_weighted_f1 | 1 | 0.628220 [0.628220, 0.628220] |
| rq1 | renoir_dml | open_world_macro_f1 | 1 | 0.595400 [0.595400, 0.595400] |
| rq1 | renoir_dml | oscr | 1 | 0.604933 [0.604933, 0.604933] |
| rq1 | renoir_dml | tpr_at_0_1_fpr | 1 | 0.044444 [0.044444, 0.044444] |
| rq1 | renoir_dml | tpr_at_1_fpr | 1 | 0.333333 [0.333333, 0.333333] |
| rq1 | renoir_dml | tpr_at_5_fpr | 1 | 0.777778 [0.777778, 0.777778] |
| rq1 | renoir_dml | unknown_auroc | 1 | 0.881416 [0.881416, 0.881416] |
| rq1 | renoir_dml | unknown_f1 | 1 | 0.434783 [0.434783, 0.434783] |
| rq1 | renoir_dml | unknown_precision | 1 | 0.625000 [0.625000, 0.625000] |
| rq1 | renoir_dml | unknown_recall | 1 | 0.333333 [0.333333, 0.333333] |
| rq1 | closed_backbone | delta_f1 | 3 | 0.000000 [0.000000, 0.000000] |
| rq1 | closed_backbone | known_accuracy | 3 | 0.950470 [0.815597, 1.085343] |
| rq1 | closed_backbone | known_macro_f1 | 3 | 0.865939 [0.794951, 0.936926] |
| rq1 | closed_backbone | known_weighted_f1 | 3 | 0.947976 [0.809225, 1.086726] |
| rq1 | hedl | aupr_out | 4 | 0.849862 [0.576580, 1.123145] |
| rq1 | hedl | closed_reference_macro_f1 | 1 | 0.238625 [0.238625, 0.238625] |
| rq1 | hedl | delta_f1 | 4 | -0.011686 [-0.060183, 0.036812] |
| rq1 | hedl | far | 4 | 0.015445 [0.006155, 0.024734] |
| rq1 | hedl | fpr95 | 4 | 0.392457 [0.070189, 0.714725] |
| rq1 | hedl | frr | 4 | 0.544762 [0.351133, 0.738391] |
| rq1 | hedl | known_accuracy | 4 | 0.790839 [0.217681, 1.363998] |
| rq1 | hedl | known_macro_f1 | 4 | 0.697424 [0.174520, 1.220328] |
| rq1 | hedl | known_weighted_f1 | 4 | 0.778455 [0.170457, 1.386452] |
| rq1 | hedl | open_world_macro_f1 | 4 | 0.627201 [0.205065, 1.049338] |
| rq1 | hedl | oscr | 4 | 0.730124 [0.204847, 1.255400] |
| rq1 | hedl | scorer_density_reference_size | 4 | 3197.000000 [335.980772, 6058.019228] |
| rq1 | hedl | scorer_density_selection_margin | 4 | 0.175000 [0.095439, 0.254561] |
| rq1 | hedl | scorer_proxy_density_auroc | 4 | 0.841198 [0.726806, 0.955591] |
| rq1 | hedl | scorer_proxy_evidential_auroc | 4 | 0.864106 [0.477353, 1.250859] |
| rq1 | hedl | tpr_at_0_1_fpr | 4 | 0.000000 [0.000000, 0.000000] |
| rq1 | hedl | tpr_at_1_fpr | 4 | 0.316561 [-0.018951, 0.652073] |
| rq1 | hedl | tpr_at_5_fpr | 4 | 0.691920 [0.425742, 0.958098] |
| rq1 | hedl | unknown_auroc | 4 | 0.913021 [0.841119, 0.984923] |
| rq1 | hedl | unknown_f1 | 4 | 0.591857 [0.408296, 0.775418] |
| rq1 | hedl | unknown_precision | 4 | 0.903450 [0.662425, 1.144475] |
| rq1 | hedl | unknown_recall | 4 | 0.455238 [0.261609, 0.648867] |

## Paired H-EDL comparisons

| rq | metric | proposed | baseline | n_pairs | mean_oriented_improvement | wins | ties | losses | wilcoxon_one_sided_p | cohens_dz | holm_adjusted_p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rq1 | aupr_out | hedl | closr | 1 | 0.27860153042034175 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | aupr_out | hedl | efc | 1 | 0.2317273315921709 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | aupr_out | hedl | renoir_dml | 1 | 0.011714957520400193 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | aupr_out | hedl | ori | 1 | 0.022929949297551544 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | aupr_out | hedl | docpp | 1 | 0.47175477855693715 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | closed_reference_macro_f1 | hedl | closr | 1 | 0.0 | 0 | 1 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | closed_reference_macro_f1 | hedl | efc | 1 | 0.0 | 0 | 1 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | closed_reference_macro_f1 | hedl | renoir_dml | 1 | 0.0 | 0 | 1 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | closed_reference_macro_f1 | hedl | ori | 1 | 0.0 | 0 | 1 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | closed_reference_macro_f1 | hedl | docpp | 1 | 0.0 | 0 | 1 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | delta_f1 | hedl | closr | 1 | -0.4233922593994489 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | delta_f1 | hedl | efc | 1 | -0.5227765910790767 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | delta_f1 | hedl | renoir_dml | 1 | -0.4239194095173783 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | delta_f1 | hedl | ori | 1 | -0.6935133848429915 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | delta_f1 | hedl | docpp | 1 | 0.179531279834799 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | far | hedl | closr | 1 | -0.008791208791208791 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | far | hedl | efc | 1 | -0.01978021978021978 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | far | hedl | renoir_dml | 1 | -0.004395604395604397 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | far | hedl | ori | 1 | -0.013186813186813187 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | far | hedl | docpp | 1 | -0.002197802197802197 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | fpr95 | hedl | closr | 1 | 0.15384615384615385 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | fpr95 | hedl | efc | 1 | 0.39780219780219783 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | fpr95 | hedl | renoir_dml | 1 | 0.12747252747252746 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | fpr95 | hedl | ori | 1 | -0.29670329670329665 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | fpr95 | hedl | docpp | 1 | 0.4593406593406594 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | frr | hedl | closr | 1 | 0.31111111111111117 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | frr | hedl | efc | 1 | 0.4444444444444445 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | frr | hedl | renoir_dml | 1 | 0.17777777777777776 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | frr | hedl | ori | 1 | 0.4222222222222222 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | frr | hedl | docpp | 1 | 0.4222222222222222 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | known_accuracy | hedl | closr | 1 | -0.41538461538461535 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | known_accuracy | hedl | efc | 1 | -0.5054945054945055 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | known_accuracy | hedl | renoir_dml | 1 | -0.41538461538461535 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | known_accuracy | hedl | ori | 1 | -0.6527472527472528 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | known_accuracy | hedl | docpp | 1 | 0.15604395604395604 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | known_macro_f1 | hedl | closr | 1 | -0.4233922593994489 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | known_macro_f1 | hedl | efc | 1 | -0.5227765910790767 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | known_macro_f1 | hedl | renoir_dml | 1 | -0.4239194095173783 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | known_macro_f1 | hedl | ori | 1 | -0.6935133848429915 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | known_macro_f1 | hedl | docpp | 1 | 0.179531279834799 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | known_weighted_f1 | hedl | closr | 1 | -0.42210628542447837 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | known_weighted_f1 | hedl | efc | 1 | -0.5222351447388963 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | known_weighted_f1 | hedl | renoir_dml | 1 | -0.4228969447206409 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | known_weighted_f1 | hedl | ori | 1 | -0.6934556072175101 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | known_weighted_f1 | hedl | docpp | 1 | 0.1801428059163797 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | open_world_macro_f1 | hedl | closr | 1 | -0.3472776655962322 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | open_world_macro_f1 | hedl | efc | 1 | -0.4259257810899092 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | open_world_macro_f1 | hedl | renoir_dml | 1 | -0.3646147547077828 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | open_world_macro_f1 | hedl | ori | 1 | -0.5760639415078439 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | open_world_macro_f1 | hedl | docpp | 1 | 0.19771777435038168 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | oscr | hedl | closr | 1 | -0.3083516483516483 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | oscr | hedl | efc | 1 | -0.2543345543345543 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | oscr | hedl | renoir_dml | 1 | -0.3657387057387057 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | oscr | hedl | ori | 1 | -0.637069597069597 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | oscr | hedl | docpp | 1 | 0.17472527472527474 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_0_1_fpr | hedl | closr | 1 | 0.0 | 0 | 1 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_0_1_fpr | hedl | efc | 1 | 0.0 | 0 | 1 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_0_1_fpr | hedl | renoir_dml | 1 | -0.044444444444444446 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_0_1_fpr | hedl | ori | 1 | 0.0 | 0 | 1 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_0_1_fpr | hedl | docpp | 1 | -0.022222222222222223 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_1_fpr | hedl | closr | 1 | 0.022222222222222223 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_1_fpr | hedl | efc | 1 | -0.044444444444444446 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_1_fpr | hedl | renoir_dml | 1 | -0.28888888888888886 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_1_fpr | hedl | ori | 1 | 0.0 | 0 | 1 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_1_fpr | hedl | docpp | 1 | -0.02222222222222222 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_5_fpr | hedl | closr | 1 | 0.4444444444444445 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_5_fpr | hedl | efc | 1 | 0.22222222222222232 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_5_fpr | hedl | renoir_dml | 1 | 0.022222222222222254 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_5_fpr | hedl | ori | 1 | 0.06666666666666676 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | tpr_at_5_fpr | hedl | docpp | 1 | 0.6888888888888889 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_auroc | hedl | closr | 1 | 0.13792429792429783 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_auroc | hedl | efc | 1 | 0.2565323565323565 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_auroc | hedl | renoir_dml | 1 | 0.034139194139194085 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_auroc | hedl | ori | 1 | -0.04312576312576322 | 0 | 0 | 1 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_auroc | hedl | docpp | 1 | 0.615189255189255 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_f1 | hedl | closr | 1 | 0.2871965137995435 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_f1 | hedl | efc | 1 | 0.4622784810126582 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_f1 | hedl | renoir_dml | 1 | 0.14749587231700606 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_f1 | hedl | ori | 1 | 0.4341303328645101 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_f1 | hedl | docpp | 1 | 0.4466852606736752 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_precision | hedl | closr | 1 | 0.11397058823529416 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_precision | hedl | efc | 1 | 0.07647058823529418 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_precision | hedl | renoir_dml | 1 | 0.05147058823529416 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_precision | hedl | ori | 1 | 0.23202614379084974 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_precision | hedl | docpp | 1 | 0.39075630252100846 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_recall | hedl | closr | 1 | 0.31111111111111106 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_recall | hedl | efc | 1 | 0.4444444444444444 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_recall | hedl | renoir_dml | 1 | 0.17777777777777776 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_recall | hedl | ori | 1 | 0.42222222222222217 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |
| rq1 | unknown_recall | hedl | docpp | 1 | 0.42222222222222217 | 1 | 0 | 0 | 1.0 | 0.0 | 1.0 |

## Average ranks

| rq | metric | method | n_complete_cases | average_rank |
| --- | --- | --- | --- | --- |
| rq1 | aupr_out | hedl | 1 | 1.0 |
| rq1 | aupr_out | closr | 1 | 5.0 |
| rq1 | aupr_out | efc | 1 | 4.0 |
| rq1 | aupr_out | renoir_dml | 1 | 2.0 |
| rq1 | aupr_out | ori | 1 | 3.0 |
| rq1 | aupr_out | docpp | 1 | 6.0 |
| rq1 | closed_reference_macro_f1 | hedl | 1 | 3.5 |
| rq1 | closed_reference_macro_f1 | closr | 1 | 3.5 |
| rq1 | closed_reference_macro_f1 | efc | 1 | 3.5 |
| rq1 | closed_reference_macro_f1 | renoir_dml | 1 | 3.5 |
| rq1 | closed_reference_macro_f1 | ori | 1 | 3.5 |
| rq1 | closed_reference_macro_f1 | docpp | 1 | 3.5 |
| rq1 | delta_f1 | hedl | 1 | 5.0 |
| rq1 | delta_f1 | closr | 1 | 4.0 |
| rq1 | delta_f1 | efc | 1 | 2.0 |
| rq1 | delta_f1 | renoir_dml | 1 | 3.0 |
| rq1 | delta_f1 | ori | 1 | 1.0 |
| rq1 | delta_f1 | docpp | 1 | 6.0 |
| rq1 | far | hedl | 1 | 6.0 |
| rq1 | far | closr | 1 | 3.0 |
| rq1 | far | efc | 1 | 1.0 |
| rq1 | far | renoir_dml | 1 | 4.0 |
| rq1 | far | ori | 1 | 2.0 |
| rq1 | far | docpp | 1 | 5.0 |
| rq1 | fpr95 | hedl | 1 | 2.0 |
| rq1 | fpr95 | closr | 1 | 4.0 |
| rq1 | fpr95 | efc | 1 | 5.0 |
| rq1 | fpr95 | renoir_dml | 1 | 3.0 |
| rq1 | fpr95 | ori | 1 | 1.0 |
| rq1 | fpr95 | docpp | 1 | 6.0 |
| rq1 | frr | hedl | 1 | 1.0 |
| rq1 | frr | closr | 1 | 3.0 |
| rq1 | frr | efc | 1 | 6.0 |
| rq1 | frr | renoir_dml | 1 | 2.0 |
| rq1 | frr | ori | 1 | 4.5 |
| rq1 | frr | docpp | 1 | 4.5 |
| rq1 | known_accuracy | hedl | 1 | 5.0 |
| rq1 | known_accuracy | closr | 1 | 3.5 |
| rq1 | known_accuracy | efc | 1 | 2.0 |
| rq1 | known_accuracy | renoir_dml | 1 | 3.5 |
| rq1 | known_accuracy | ori | 1 | 1.0 |
| rq1 | known_accuracy | docpp | 1 | 6.0 |
| rq1 | known_macro_f1 | hedl | 1 | 5.0 |
| rq1 | known_macro_f1 | closr | 1 | 4.0 |
| rq1 | known_macro_f1 | efc | 1 | 2.0 |
| rq1 | known_macro_f1 | renoir_dml | 1 | 3.0 |
| rq1 | known_macro_f1 | ori | 1 | 1.0 |
| rq1 | known_macro_f1 | docpp | 1 | 6.0 |
| rq1 | known_weighted_f1 | hedl | 1 | 5.0 |
| rq1 | known_weighted_f1 | closr | 1 | 4.0 |
| rq1 | known_weighted_f1 | efc | 1 | 2.0 |
| rq1 | known_weighted_f1 | renoir_dml | 1 | 3.0 |
| rq1 | known_weighted_f1 | ori | 1 | 1.0 |
| rq1 | known_weighted_f1 | docpp | 1 | 6.0 |
| rq1 | open_world_macro_f1 | hedl | 1 | 5.0 |
| rq1 | open_world_macro_f1 | closr | 1 | 4.0 |
| rq1 | open_world_macro_f1 | efc | 1 | 2.0 |
| rq1 | open_world_macro_f1 | renoir_dml | 1 | 3.0 |
| rq1 | open_world_macro_f1 | ori | 1 | 1.0 |
| rq1 | open_world_macro_f1 | docpp | 1 | 6.0 |
| rq1 | oscr | hedl | 1 | 5.0 |
| rq1 | oscr | closr | 1 | 3.0 |
| rq1 | oscr | efc | 1 | 4.0 |
| rq1 | oscr | renoir_dml | 1 | 2.0 |
| rq1 | oscr | ori | 1 | 1.0 |
| rq1 | oscr | docpp | 1 | 6.0 |
| rq1 | tpr_at_0_1_fpr | hedl | 1 | 4.5 |
| rq1 | tpr_at_0_1_fpr | closr | 1 | 4.5 |
| rq1 | tpr_at_0_1_fpr | efc | 1 | 4.5 |
| rq1 | tpr_at_0_1_fpr | renoir_dml | 1 | 1.0 |
| rq1 | tpr_at_0_1_fpr | ori | 1 | 4.5 |
| rq1 | tpr_at_0_1_fpr | docpp | 1 | 2.0 |
| rq1 | tpr_at_1_fpr | hedl | 1 | 4.5 |
| rq1 | tpr_at_1_fpr | closr | 1 | 6.0 |
| rq1 | tpr_at_1_fpr | efc | 1 | 2.0 |
| rq1 | tpr_at_1_fpr | renoir_dml | 1 | 1.0 |
| rq1 | tpr_at_1_fpr | ori | 1 | 4.5 |
| rq1 | tpr_at_1_fpr | docpp | 1 | 3.0 |
| rq1 | tpr_at_5_fpr | hedl | 1 | 1.0 |
| rq1 | tpr_at_5_fpr | closr | 1 | 5.0 |
| rq1 | tpr_at_5_fpr | efc | 1 | 4.0 |
| rq1 | tpr_at_5_fpr | renoir_dml | 1 | 2.0 |
| rq1 | tpr_at_5_fpr | ori | 1 | 3.0 |
| rq1 | tpr_at_5_fpr | docpp | 1 | 6.0 |
| rq1 | unknown_auroc | hedl | 1 | 2.0 |
| rq1 | unknown_auroc | closr | 1 | 4.0 |
| rq1 | unknown_auroc | efc | 1 | 5.0 |
| rq1 | unknown_auroc | renoir_dml | 1 | 3.0 |
| rq1 | unknown_auroc | ori | 1 | 1.0 |
| rq1 | unknown_auroc | docpp | 1 | 6.0 |
| rq1 | unknown_f1 | hedl | 1 | 1.0 |
| rq1 | unknown_f1 | closr | 1 | 3.0 |
| rq1 | unknown_f1 | efc | 1 | 6.0 |
| rq1 | unknown_f1 | renoir_dml | 1 | 2.0 |
| rq1 | unknown_f1 | ori | 1 | 4.0 |
| rq1 | unknown_f1 | docpp | 1 | 5.0 |
| rq1 | unknown_precision | hedl | 1 | 1.0 |
| rq1 | unknown_precision | closr | 1 | 4.0 |
| rq1 | unknown_precision | efc | 1 | 3.0 |
| rq1 | unknown_precision | renoir_dml | 1 | 2.0 |
| rq1 | unknown_precision | ori | 1 | 5.0 |
| rq1 | unknown_precision | docpp | 1 | 6.0 |
| rq1 | unknown_recall | hedl | 1 | 1.0 |
| rq1 | unknown_recall | closr | 1 | 3.0 |
| rq1 | unknown_recall | efc | 1 | 6.0 |
| rq1 | unknown_recall | renoir_dml | 1 | 2.0 |
| rq1 | unknown_recall | ori | 1 | 4.5 |
| rq1 | unknown_recall | docpp | 1 | 4.5 |
