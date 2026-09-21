# Mock rerun comparison — 2026-08-31

Smoke configuration: seed 13, one epoch, maximum 500 rows per split. H-EDL is compared against the best value among all five RQ-specific baselines.

## RQ1

- Wins: 2/10
- Ties: 0/10
- Losses: 8/10

| Case | Metric | H-EDL | Best baseline | Best value | Verdict |
|---|---|---:|---|---:|---|
| CICIDS2017 Z1 LOAO | known_accuracy | 0.250549 | ori | 0.903297 | loss |
| CICIDS2017 Z1 LOAO | known_macro_f1 | 0.204527 | ori | 0.898040 | loss |
| CICIDS2017 Z1 LOAO | known_weighted_f1 | 0.205323 | ori | 0.898779 | loss |
| CICIDS2017 Z1 LOAO | delta_f1 | -0.034098 | ori | 0.659416 | loss |
| CICIDS2017 Z1 LOAO | unknown_auroc | 0.915556 | ori | 0.958681 | loss |
| CICIDS2017 Z1 LOAO | fpr95 | 0.413187 | ori | 0.116484 | loss |
| CICIDS2017 Z1 LOAO | aupr_out | 0.596184 | renoir_dml | 0.584469 | win |
| CICIDS2017 Z1 LOAO | oscr | 0.239194 | ori | 0.876264 | loss |
| CICIDS2017 Z1 LOAO | open_world_macro_f1 | 0.230786 | ori | 0.806850 | loss |
| CICIDS2017 Z1 LOAO | unknown_f1 | 0.582278 | renoir_dml | 0.434783 | win |

## RQ2

- Wins: 3/25
- Ties: 0/25
- Losses: 22/25

| Case | Metric | H-EDL | Best baseline | Best value | Verdict |
|---|---|---:|---|---:|---|
| CICIDS2017 openness O1 | unknown_auroc | 0.903004 | cd_zd_srl | 0.882955 | win |
| CICIDS2017 openness O1 | fpr95 | 0.424176 | closr | 0.279121 | loss |
| CICIDS2017 openness O1 | aupr_out | 0.517339 | cd_zd_srl | 0.592592 | loss |
| CICIDS2017 openness O1 | oscr | 0.366569 | foss | 0.752186 | loss |
| CICIDS2017 openness O1 | open_world_macro_f1 | 0.341174 | foss | 0.758313 | loss |
| CICIDS2017 near Z1 | unknown_auroc | 0.903004 | cd_zd_srl | 0.882955 | win |
| CICIDS2017 near Z1 | fpr95 | 0.424176 | closr | 0.279121 | loss |
| CICIDS2017 near Z1 | aupr_out | 0.517339 | cd_zd_srl | 0.592592 | loss |
| CICIDS2017 near Z1 | oscr | 0.366569 | foss | 0.752186 | loss |
| CICIDS2017 near Z1 | open_world_macro_f1 | 0.341174 | foss | 0.758313 | loss |
| CICIDS2017 far Z2 | unknown_auroc | 0.639713 | efc | 0.911760 | loss |
| CICIDS2017 far Z2 | fpr95 | 0.566740 | efc | 0.168490 | loss |
| CICIDS2017 far Z2 | aupr_out | 0.126129 | efc | 0.444357 | loss |
| CICIDS2017 far Z2 | oscr | 0.259045 | efc | 0.737062 | loss |
| CICIDS2017 far Z2 | open_world_macro_f1 | 0.299792 | foss | 0.764143 | loss |
| UNSW→ToN-IoT | unknown_auroc | 0.452587 | closr | 0.730688 | loss |
| UNSW→ToN-IoT | fpr95 | 0.968000 | closr | 0.832000 | loss |
| UNSW→ToN-IoT | aupr_out | 0.221485 | closr | 0.481204 | loss |
| UNSW→ToN-IoT | oscr | 0.013781 | cd_zd_srl | 0.230677 | loss |
| UNSW→ToN-IoT | open_world_macro_f1 | 0.016378 | foss | 0.148392 | loss |
| LOEO target UNSW | unknown_auroc | 0.557875 | cd_zd_srl | 0.541775 | win |
| LOEO target UNSW | fpr95 | 0.990000 | closr | 0.920000 | loss |
| LOEO target UNSW | aupr_out | 0.228893 | closr | 0.232199 | loss |
| LOEO target UNSW | oscr | 0.000000 | renoir_dml | 0.097275 | loss |
| LOEO target UNSW | open_world_macro_f1 | 0.013245 | cd_zd_srl | 0.069922 | loss |

## RQ3

- Wins: 0/10
- Ties: 6/10
- Losses: 4/10

| Case | Metric | H-EDL | Best baseline | Best value | Verdict |
|---|---|---:|---|---:|---|
| CICIoMT2024 Z1 deployment | aupr_out | 0.037184 | efc | 0.130571 | loss |
| CICIoMT2024 Z1 deployment | unknown_precision | 0.000000 | ais_nids | 0.000000 | tie |
| CICIoMT2024 Z1 deployment | unknown_recall | 0.000000 | ais_nids | 0.000000 | tie |
| CICIoMT2024 Z1 deployment | unknown_f1 | 0.000000 | ais_nids | 0.000000 | tie |
| CICIoMT2024 Z1 deployment | tpr_at_5_fpr | 0.000000 | ais_nids | 0.000000 | tie |
| CICIoMT2024 Z1 deployment | tpr_at_1_fpr | 0.000000 | ais_nids | 0.000000 | tie |
| CICIoMT2024 Z1 deployment | tpr_at_0_1_fpr | 0.000000 | ais_nids | 0.000000 | tie |
| CICIoMT2024 Z1 deployment | latency_ms_per_flow | 0.479140 | ais_nids | 0.043894 | loss |
| CICIoMT2024 Z1 deployment | throughput_fps | 2087.073543 | ais_nids | 22782.157013 | loss |
| CICIoMT2024 Z1 deployment | parameters | 4404.000000 | efc | 0.000000 | loss |

## RQ3 prevalence sub-analysis

- Wins: 0/24
- Ties: 18/24
- Losses: 6/24

