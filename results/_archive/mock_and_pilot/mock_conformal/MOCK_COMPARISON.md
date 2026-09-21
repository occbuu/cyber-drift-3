# Mock test — conformal fusion scorer (2026-09-10)

## Scorecard

```json
{
  "by_rq": {
    "rq1": {
      "loss": 10
    },
    "rq2": {
      "loss": 20,
      "win": 5
    },
    "rq3": {
      "loss": 4,
      "tie": 6
    }
  },
  "overall": {
    "loss": 34,
    "tie": 6,
    "win": 5
  },
  "prevalence": {
    "loss": 6
  }
}
```

## RQ1

- win 0 / tie 0 / loss 10

| case | metric | proposed | best_baseline | baseline_value | outcome |
| --- | --- | --- | --- | --- | --- |
| loao/cicids2017/Z1/seed_13 | known_accuracy | 0.356044 | ori | 0.903297 | loss |
| loao/cicids2017/Z1/seed_13 | known_macro_f1 | 0.321008 | ori | 0.898040 | loss |
| loao/cicids2017/Z1/seed_13 | known_weighted_f1 | 0.322110 | ori | 0.898779 | loss |
| loao/cicids2017/Z1/seed_13 | delta_f1 | 0.082383 | ori | 0.659416 | loss |
| loao/cicids2017/Z1/seed_13 | unknown_auroc | 0.890110 | ori | 0.958681 | loss |
| loao/cicids2017/Z1/seed_13 | fpr95 | 0.470330 | ori | 0.116484 | loss |
| loao/cicids2017/Z1/seed_13 | aupr_out | 0.452805 | renoir_dml | 0.584469 | loss |
| loao/cicids2017/Z1/seed_13 | oscr | 0.336459 | ori | 0.876264 | loss |
| loao/cicids2017/Z1/seed_13 | open_world_macro_f1 | 0.307504 | ori | 0.806850 | loss |
| loao/cicids2017/Z1/seed_13 | unknown_f1 | 0.368421 | renoir_dml | 0.434783 | loss |

## RQ2

- win 5 / tie 0 / loss 20

| case | metric | proposed | best_baseline | baseline_value | outcome |
| --- | --- | --- | --- | --- | --- |
| cross_domain/leave_one_environment_out/nf_unsw_nb15_v3/seed_13 | unknown_auroc | 0.561200 | cd_zd_srl | 0.541775 | win |
| cross_domain/leave_one_environment_out/nf_unsw_nb15_v3/seed_13 | fpr95 | 0.985000 | closr | 0.920000 | loss |
| cross_domain/leave_one_environment_out/nf_unsw_nb15_v3/seed_13 | aupr_out | 0.228395 | closr | 0.232199 | loss |
| cross_domain/leave_one_environment_out/nf_unsw_nb15_v3/seed_13 | oscr | 0.000000 | renoir_dml | 0.097275 | loss |
| cross_domain/leave_one_environment_out/nf_unsw_nb15_v3/seed_13 | open_world_macro_f1 | 0.015909 | cd_zd_srl | 0.069922 | loss |
| cross_domain/source_target/nf_unsw_nb15_v3_to_nf_ton_iot_v3/seed_13 | unknown_auroc | 0.451221 | closr | 0.730688 | loss |
| cross_domain/source_target/nf_unsw_nb15_v3_to_nf_ton_iot_v3/seed_13 | fpr95 | 0.962667 | closr | 0.832000 | loss |
| cross_domain/source_target/nf_unsw_nb15_v3_to_nf_ton_iot_v3/seed_13 | aupr_out | 0.232465 | closr | 0.481204 | loss |
| cross_domain/source_target/nf_unsw_nb15_v3_to_nf_ton_iot_v3/seed_13 | oscr | 0.004992 | cd_zd_srl | 0.230677 | loss |
| cross_domain/source_target/nf_unsw_nb15_v3_to_nf_ton_iot_v3/seed_13 | open_world_macro_f1 | 0.013751 | foss | 0.148392 | loss |
| difficulty/near_far/far/cicids2017/Z2/seed_13 | unknown_auroc | 0.848990 | efc | 0.911760 | loss |
| difficulty/near_far/far/cicids2017/Z2/seed_13 | fpr95 | 0.297593 | efc | 0.168490 | loss |
| difficulty/near_far/far/cicids2017/Z2/seed_13 | aupr_out | 0.296834 | efc | 0.444357 | loss |
| difficulty/near_far/far/cicids2017/Z2/seed_13 | oscr | 0.368684 | efc | 0.737062 | loss |
| difficulty/near_far/far/cicids2017/Z2/seed_13 | open_world_macro_f1 | 0.295758 | foss | 0.764143 | loss |
| difficulty/near_far/near/cicids2017/Z1/seed_13 | unknown_auroc | 0.925397 | cd_zd_srl | 0.882955 | win |
| difficulty/near_far/near/cicids2017/Z1/seed_13 | fpr95 | 0.323077 | closr | 0.279121 | loss |
| difficulty/near_far/near/cicids2017/Z1/seed_13 | aupr_out | 0.642468 | cd_zd_srl | 0.592592 | win |
| difficulty/near_far/near/cicids2017/Z1/seed_13 | oscr | 0.441807 | foss | 0.752186 | loss |
| difficulty/near_far/near/cicids2017/Z1/seed_13 | open_world_macro_f1 | 0.423047 | foss | 0.758313 | loss |
| difficulty/openness/cicids2017/O1/seed_13 | unknown_auroc | 0.925397 | cd_zd_srl | 0.882955 | win |
| difficulty/openness/cicids2017/O1/seed_13 | fpr95 | 0.323077 | closr | 0.279121 | loss |
| difficulty/openness/cicids2017/O1/seed_13 | aupr_out | 0.642468 | cd_zd_srl | 0.592592 | win |
| difficulty/openness/cicids2017/O1/seed_13 | oscr | 0.441807 | foss | 0.752186 | loss |
| difficulty/openness/cicids2017/O1/seed_13 | open_world_macro_f1 | 0.423047 | foss | 0.758313 | loss |

## RQ3

- win 0 / tie 6 / loss 4

| case | metric | proposed | best_baseline | baseline_value | outcome |
| --- | --- | --- | --- | --- | --- |
| prevalence/ciciomt2024/Z1/seed_13 | aupr_out | 0.030757 | efc | 0.130571 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | unknown_precision | 0.000000 | ais_nids | 0.000000 | tie |
| prevalence/ciciomt2024/Z1/seed_13 | unknown_recall | 0.000000 | ais_nids | 0.000000 | tie |
| prevalence/ciciomt2024/Z1/seed_13 | unknown_f1 | 0.000000 | ais_nids | 0.000000 | tie |
| prevalence/ciciomt2024/Z1/seed_13 | tpr_at_5_fpr | 0.000000 | ais_nids | 0.000000 | tie |
| prevalence/ciciomt2024/Z1/seed_13 | tpr_at_1_fpr | 0.000000 | ais_nids | 0.000000 | tie |
| prevalence/ciciomt2024/Z1/seed_13 | tpr_at_0_1_fpr | 0.000000 | ais_nids | 0.000000 | tie |
| prevalence/ciciomt2024/Z1/seed_13 | latency_ms_per_flow | 0.074536 | closr | 0.015369 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | throughput_fps | 13416.407729 | closr | 65064.348625 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | parameters | 4404.000000 | efc | 0.000000 | loss |

## RQ3 prevalence sweep

| case | prevalence | proposed_aupr_out | best_baseline | baseline_aupr_out | outcome |
| --- | --- | --- | --- | --- | --- |
| prevalence/ciciomt2024/Z1/seed_13 | 0.500000 | 0.352267 | ais_nids | 0.755038 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | 0.250000 | 0.154238 | efc | 0.440269 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | 0.100000 | 0.060209 | efc | 0.230083 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | 0.050000 | 0.029697 | efc | 0.126032 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | 0.010000 | 0.006934 | efc | 0.029240 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | 0.001000 | 0.002336 | ais_nids | 0.006803 | loss |
