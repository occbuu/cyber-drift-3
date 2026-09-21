# Mock test v2 (20k dong/split, 15 epoch) — conformal fusion scorer

## Scorecard

```json
{
  "by_rq": {
    "rq1": {
      "loss": 9,
      "win": 1
    },
    "rq2": {
      "loss": 17,
      "win": 8
    },
    "rq3": {
      "loss": 9,
      "tie": 1
    }
  },
  "overall": {
    "loss": 35,
    "tie": 1,
    "win": 9
  },
  "prevalence": {
    "loss": 6
  }
}
```

## RQ1

- win 1 / tie 0 / loss 9

| case | metric | proposed | best_baseline | baseline_value | outcome |
| --- | --- | --- | --- | --- | --- |
| loao/cicids2017/Z1/seed_13 | known_accuracy | 0.954193 | ori | 0.976652 | loss |
| loao/cicids2017/Z1/seed_13 | known_macro_f1 | 0.844947 | ori | 0.893029 | loss |
| loao/cicids2017/Z1/seed_13 | known_weighted_f1 | 0.952205 | ori | 0.976643 | loss |
| loao/cicids2017/Z1/seed_13 | delta_f1 | -0.016476 | ori | 0.031605 | loss |
| loao/cicids2017/Z1/seed_13 | unknown_auroc | 0.959096 | ori | 0.972836 | loss |
| loao/cicids2017/Z1/seed_13 | fpr95 | 0.129746 | ori | 0.198659 | win |
| loao/cicids2017/Z1/seed_13 | aupr_out | 0.904405 | ori | 0.954965 | loss |
| loao/cicids2017/Z1/seed_13 | oscr | 0.920960 | ori | 0.951445 | loss |
| loao/cicids2017/Z1/seed_13 | open_world_macro_f1 | 0.739355 | ori | 0.795847 | loss |
| loao/cicids2017/Z1/seed_13 | unknown_f1 | 0.409903 | ori | 0.612072 | loss |

## RQ2

- win 8 / tie 0 / loss 17

| case | metric | proposed | best_baseline | baseline_value | outcome |
| --- | --- | --- | --- | --- | --- |
| cross_domain/leave_one_environment_out/nf_unsw_nb15_v3/seed_13 | unknown_auroc | 0.528658 | closr | 0.541415 | loss |
| cross_domain/leave_one_environment_out/nf_unsw_nb15_v3/seed_13 | fpr95 | 0.895312 | cd_zd_srl | 0.882313 | loss |
| cross_domain/leave_one_environment_out/nf_unsw_nb15_v3/seed_13 | aupr_out | 0.203999 | closr | 0.228805 | loss |
| cross_domain/leave_one_environment_out/nf_unsw_nb15_v3/seed_13 | oscr | 0.076222 | renoir_dml | 0.079506 | loss |
| cross_domain/leave_one_environment_out/nf_unsw_nb15_v3/seed_13 | open_world_macro_f1 | 0.026164 | cd_zd_srl | 0.033001 | loss |
| cross_domain/source_target/nf_unsw_nb15_v3_to_nf_ton_iot_v3/seed_13 | unknown_auroc | 0.417255 | efc | 0.669680 | loss |
| cross_domain/source_target/nf_unsw_nb15_v3_to_nf_ton_iot_v3/seed_13 | fpr95 | 0.970800 | cd_zd_srl | 0.843133 | loss |
| cross_domain/source_target/nf_unsw_nb15_v3_to_nf_ton_iot_v3/seed_13 | aupr_out | 0.209683 | efc | 0.573973 | loss |
| cross_domain/source_target/nf_unsw_nb15_v3_to_nf_ton_iot_v3/seed_13 | oscr | 0.110074 | foss | 0.215343 | loss |
| cross_domain/source_target/nf_unsw_nb15_v3_to_nf_ton_iot_v3/seed_13 | open_world_macro_f1 | 0.104401 | foss | 0.216205 | loss |
| difficulty/near_far/far/cicids2017/Z2/seed_13 | unknown_auroc | 0.914368 | closr | 0.966387 | loss |
| difficulty/near_far/far/cicids2017/Z2/seed_13 | fpr95 | 0.182764 | renoir_dml | 0.058477 | loss |
| difficulty/near_far/far/cicids2017/Z2/seed_13 | aupr_out | 0.590858 | closr | 0.808347 | loss |
| difficulty/near_far/far/cicids2017/Z2/seed_13 | oscr | 0.882827 | closr | 0.915734 | loss |
| difficulty/near_far/far/cicids2017/Z2/seed_13 | open_world_macro_f1 | 0.699193 | closr | 0.785664 | loss |
| difficulty/near_far/near/cicids2017/Z1/seed_13 | unknown_auroc | 0.961795 | renoir_dml | 0.933979 | win |
| difficulty/near_far/near/cicids2017/Z1/seed_13 | fpr95 | 0.095330 | cd_zd_srl | 0.189934 | win |
| difficulty/near_far/near/cicids2017/Z1/seed_13 | aupr_out | 0.917632 | foss | 0.892276 | win |
| difficulty/near_far/near/cicids2017/Z1/seed_13 | oscr | 0.923167 | cd_zd_srl | 0.906979 | win |
| difficulty/near_far/near/cicids2017/Z1/seed_13 | open_world_macro_f1 | 0.748774 | foss | 0.835719 | loss |
| difficulty/openness/cicids2017/O1/seed_13 | unknown_auroc | 0.961795 | renoir_dml | 0.933979 | win |
| difficulty/openness/cicids2017/O1/seed_13 | fpr95 | 0.095330 | cd_zd_srl | 0.189934 | win |
| difficulty/openness/cicids2017/O1/seed_13 | aupr_out | 0.917632 | foss | 0.892275 | win |
| difficulty/openness/cicids2017/O1/seed_13 | oscr | 0.923167 | cd_zd_srl | 0.906979 | win |
| difficulty/openness/cicids2017/O1/seed_13 | open_world_macro_f1 | 0.748774 | foss | 0.835719 | loss |

## RQ3

- win 0 / tie 1 / loss 9

| case | metric | proposed | best_baseline | baseline_value | outcome |
| --- | --- | --- | --- | --- | --- |
| prevalence/ciciomt2024/Z1/seed_13 | aupr_out | 0.030875 | efc | 0.172749 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | unknown_precision | 0.002793 | efc | 0.019868 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | unknown_recall | 0.000900 | efc | 0.002700 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | unknown_f1 | 0.001361 | efc | 0.004754 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | tpr_at_5_fpr | 0.002700 | usfad | 0.012601 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | tpr_at_1_fpr | 0.000900 | efc | 0.002700 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | tpr_at_0_1_fpr | 0.000000 | ais_nids | 0.000000 | tie |
| prevalence/ciciomt2024/Z1/seed_13 | latency_ms_per_flow | 0.164545 | closr | 0.006509 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | throughput_fps | 6077.382583 | closr | 153624.461931 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | parameters | 4404.000000 | efc | 0.000000 | loss |

## RQ3 prevalence sweep

| case | prevalence | proposed_aupr_out | best_baseline | baseline_aupr_out | outcome |
| --- | --- | --- | --- | --- | --- |
| prevalence/ciciomt2024/Z1/seed_13 | 0.500000 | 0.329912 | efc | 0.770921 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | 0.250000 | 0.148599 | efc | 0.539628 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | 0.100000 | 0.056346 | efc | 0.281866 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | 0.050000 | 0.027734 | efc | 0.157952 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | 0.010000 | 0.005535 | efc | 0.034938 | loss |
| prevalence/ciciomt2024/Z1/seed_13 | 0.001000 | 0.000589 | efc | 0.004460 | loss |
