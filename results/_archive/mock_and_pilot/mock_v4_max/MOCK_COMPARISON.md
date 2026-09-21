# Mock v4 - profile max

## Scorecard

```json
{
  "by_rq": {
    "rq1": {
      "win": 10
    },
    "rq2": {
      "loss": 9,
      "win": 16
    },
    "rq3": {
      "loss": 3,
      "win": 7
    }
  },
  "overall": {
    "loss": 12,
    "win": 33
  },
  "prevalence": {
    "win": 6
  }
}
```

## RQ1

- win 10 / tie 0 / loss 0

| case | metric | proposed | best_baseline | baseline_value | outcome |
| --- | --- | --- | --- | --- | --- |
| loao/cicids2017/Z1/seed_13 | known_accuracy | 0.985135 | ori | 0.976652 | win |
| loao/cicids2017/Z1/seed_13 | known_macro_f1 | 0.896502 | ori | 0.893029 | win |
| loao/cicids2017/Z1/seed_13 | known_weighted_f1 | 0.983777 | ori | 0.976643 | win |
| loao/cicids2017/Z1/seed_13 | delta_f1 | 0.035078 | ori | 0.031605 | win |
| loao/cicids2017/Z1/seed_13 | unknown_auroc | 0.994842 | ori | 0.972835 | win |
| loao/cicids2017/Z1/seed_13 | fpr95 | 0.016562 | ori | 0.198659 | win |
| loao/cicids2017/Z1/seed_13 | aupr_out | 0.985148 | ori | 0.954965 | win |
| loao/cicids2017/Z1/seed_13 | oscr | 0.981483 | ori | 0.951444 | win |
| loao/cicids2017/Z1/seed_13 | open_world_macro_f1 | 0.830527 | ori | 0.795847 | win |
| loao/cicids2017/Z1/seed_13 | unknown_f1 | 0.848562 | ori | 0.612072 | win |

## RQ2

- win 16 / tie 0 / loss 9

| case | metric | proposed | best_baseline | baseline_value | outcome |
| --- | --- | --- | --- | --- | --- |
| cross_domain/leave_one_environment_out/nf_unsw_nb15_v3/seed_13 | unknown_auroc | 0.535283 | closr | 0.541415 | loss |
| cross_domain/leave_one_environment_out/nf_unsw_nb15_v3/seed_13 | fpr95 | 0.925687 | cd_zd_srl | 0.882313 | loss |
| cross_domain/leave_one_environment_out/nf_unsw_nb15_v3/seed_13 | aupr_out | 0.220542 | closr | 0.228805 | loss |
| cross_domain/leave_one_environment_out/nf_unsw_nb15_v3/seed_13 | oscr | 0.059586 | renoir_dml | 0.079506 | loss |
| cross_domain/leave_one_environment_out/nf_unsw_nb15_v3/seed_13 | open_world_macro_f1 | 0.107202 | cd_zd_srl | 0.033001 | win |
| cross_domain/source_target/nf_unsw_nb15_v3_to_nf_ton_iot_v3/seed_13 | unknown_auroc | 0.499121 | efc | 0.669680 | loss |
| cross_domain/source_target/nf_unsw_nb15_v3_to_nf_ton_iot_v3/seed_13 | fpr95 | 0.844667 | cd_zd_srl | 0.843133 | loss |
| cross_domain/source_target/nf_unsw_nb15_v3_to_nf_ton_iot_v3/seed_13 | aupr_out | 0.249025 | efc | 0.573973 | loss |
| cross_domain/source_target/nf_unsw_nb15_v3_to_nf_ton_iot_v3/seed_13 | oscr | 0.097220 | foss | 0.215343 | loss |
| cross_domain/source_target/nf_unsw_nb15_v3_to_nf_ton_iot_v3/seed_13 | open_world_macro_f1 | 0.100771 | foss | 0.216205 | loss |
| difficulty/near_far/far/cicids2017/Z2/seed_13 | unknown_auroc | 0.995950 | closr | 0.966387 | win |
| difficulty/near_far/far/cicids2017/Z2/seed_13 | fpr95 | 0.004951 | renoir_dml | 0.058477 | win |
| difficulty/near_far/far/cicids2017/Z2/seed_13 | aupr_out | 0.942911 | closr | 0.808347 | win |
| difficulty/near_far/far/cicids2017/Z2/seed_13 | oscr | 0.985973 | closr | 0.915734 | win |
| difficulty/near_far/far/cicids2017/Z2/seed_13 | open_world_macro_f1 | 0.900205 | closr | 0.785664 | win |
| difficulty/near_far/near/cicids2017/Z1/seed_13 | unknown_auroc | 0.996709 | renoir_dml | 0.933979 | win |
| difficulty/near_far/near/cicids2017/Z1/seed_13 | fpr95 | 0.009856 | cd_zd_srl | 0.189934 | win |
| difficulty/near_far/near/cicids2017/Z1/seed_13 | aupr_out | 0.991454 | foss | 0.892274 | win |
| difficulty/near_far/near/cicids2017/Z1/seed_13 | oscr | 0.984385 | cd_zd_srl | 0.906979 | win |
| difficulty/near_far/near/cicids2017/Z1/seed_13 | open_world_macro_f1 | 0.887048 | foss | 0.835719 | win |
| difficulty/openness/cicids2017/O2/seed_13 | unknown_auroc | 0.987636 | cd_zd_srl | 0.943296 | win |
| difficulty/openness/cicids2017/O2/seed_13 | fpr95 | 0.104487 | cd_zd_srl | 0.126237 | win |
| difficulty/openness/cicids2017/O2/seed_13 | aupr_out | 0.979629 | cd_zd_srl | 0.883406 | win |
| difficulty/openness/cicids2017/O2/seed_13 | oscr | 0.976324 | cd_zd_srl | 0.917160 | win |
| difficulty/openness/cicids2017/O2/seed_13 | open_world_macro_f1 | 0.853538 | foss | 0.810051 | win |

## RQ3

- win 7 / tie 0 / loss 3

| case | metric | proposed | best_baseline | baseline_value | outcome |
| --- | --- | --- | --- | --- | --- |
| prevalence/ciciomt2024/Z1/seed_13 | aupr_out | 0.836730 | efc | 0.172749 | win |
| prevalence/ciciomt2024/Z1/seed_13 | unknown_precision | 0.800432 | efc | 0.019868 | win |
| prevalence/ciciomt2024/Z1/seed_13 | unknown_recall | 1.000000 | efc | 0.002700 | win |
| prevalence/ciciomt2024/Z1/seed_13 | unknown_f1 | 0.889156 | efc | 0.004754 | win |
| prevalence/ciciomt2024/Z1/seed_13 | tpr_at_5_fpr | 1.000000 | usfad | 0.012601 | win |
| prevalence/ciciomt2024/Z1/seed_13 | tpr_at_1_fpr | 0.997300 | efc | 0.002700 | win |
| prevalence/ciciomt2024/Z1/seed_13 | tpr_at_0_1_fpr | 0.000900 | ais_nids | 0.000000 | win |
| prevalence/ciciomt2024/Z1/seed_13 | latency_ms_per_flow | 0.044233 | closr | 0.006030 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | throughput_fps | 22607.509446 | closr | 165842.567310 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | parameters | 97252.000000 | efc | 0.000000 | loss |

## RQ3 prevalence sweep

| case | prevalence | proposed_aupr_out | best_baseline | baseline_aupr_out | outcome |
| --- | --- | --- | --- | --- | --- |
| prevalence/ciciomt2024/Z1/seed_13 | 0.500000 | 0.994944 | efc | 0.770921 | win |
| prevalence/ciciomt2024/Z1/seed_13 | 0.250000 | 0.959594 | efc | 0.539628 | win |
| prevalence/ciciomt2024/Z1/seed_13 | 0.100000 | 0.903945 | efc | 0.281866 | win |
| prevalence/ciciomt2024/Z1/seed_13 | 0.050000 | 0.823945 | efc | 0.157952 | win |
| prevalence/ciciomt2024/Z1/seed_13 | 0.010000 | 0.540460 | efc | 0.034938 | win |
| prevalence/ciciomt2024/Z1/seed_13 | 0.001000 | 0.129111 | efc | 0.004460 | win |
