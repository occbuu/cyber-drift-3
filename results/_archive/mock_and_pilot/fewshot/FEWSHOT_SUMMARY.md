### loeo_unsw

| k/họ | Chỉ số | H-EDL | Baseline tốt nhất | Kết quả |
| ---: | --- | --- | --- | --- |
| 0 | unknown_auroc | 0.5277 ± 0.0471 | closr 0.5399 ± 0.0079 | thua |
| 0 | fpr95 | 0.9037 ± 0.0428 | cd_zd_srl 0.9169 ± 0.0398 | **THẮNG** |
| 0 | aupr_out | 0.2168 ± 0.0236 | closr 0.2243 ± 0.0056 | thua |
| 0 | oscr | 0.0526 ± 0.0334 | renoir_dml 0.0879 ± 0.0060 | thua |
| 0 | open_world_macro_f1 | 0.0368 ± 0.0211 | cd_zd_srl 0.0490 ± 0.0210 | thua |
| 50 | unknown_auroc | 0.5747 ± 0.0077 | closr 0.5575 ± 0.0183 | **THẮNG** |
| 50 | fpr95 | 0.8758 ± 0.0582 | efc 0.9128 ± 0.0138 | **THẮNG** |
| 50 | aupr_out | 0.2394 ± 0.0019 | foss 0.2341 ± 0.0066 | **THẮNG** |
| 50 | oscr | 0.3928 ± 0.0051 | foss 0.3779 ± 0.0109 | **THẮNG** |
| 50 | open_world_macro_f1 | 0.1705 ± 0.0392 | foss 0.1419 ± 0.0060 | **THẮNG** |

Thắng theo k: k=0: 1/5, k=50: 5/5

### unsw_to_ton

| k/họ | Chỉ số | H-EDL | Baseline tốt nhất | Kết quả |
| ---: | --- | --- | --- | --- |
| 0 | unknown_auroc | 0.4998 ± 0.0621 | efc 0.6697 ± 0.0000 | thua |
| 0 | fpr95 | 0.8968 ± 0.0272 | cd_zd_srl 0.8428 ± 0.0678 | thua |
| 0 | aupr_out | 0.2632 ± 0.0507 | efc 0.5740 ± 0.0000 | thua |
| 0 | oscr | 0.1058 ± 0.0221 | foss 0.1648 ± 0.0444 | thua |
| 0 | open_world_macro_f1 | 0.0773 ± 0.0227 | foss 0.2066 ± 0.0083 | thua |
| 10 | unknown_auroc | 0.7809 ± 0.0291 | efc 0.6697 ± 0.0000 | **THẮNG** |
| 10 | fpr95 | 0.7618 ± 0.0243 | foss 0.8394 ± 0.0868 | **THẮNG** |
| 10 | aupr_out | 0.5267 ± 0.0492 | efc 0.5746 ± 0.0002 | thua |
| 10 | oscr | 0.7102 ± 0.0201 | foss 0.3741 ± 0.0537 | **THẮNG** |
| 10 | open_world_macro_f1 | 0.3811 ± 0.0987 | foss 0.3824 ± 0.0442 | thua |
| 50 | unknown_auroc | 0.8467 ± 0.0150 | closr 0.7014 ± 0.0418 | **THẮNG** |
| 50 | fpr95 | 0.6763 ± 0.0818 | foss 0.8015 ± 0.0368 | **THẮNG** |
| 50 | aupr_out | 0.6496 ± 0.0330 | efc 0.5788 ± 0.0007 | **THẮNG** |
| 50 | oscr | 0.8027 ± 0.0195 | closr 0.4954 ± 0.0165 | **THẮNG** |
| 50 | open_world_macro_f1 | 0.3429 ± 0.0044 | foss 0.4110 ± 0.0061 | thua |
| 200 | unknown_auroc | 0.8923 ± 0.0055 | closr 0.8385 ± 0.0115 | **THẮNG** |
| 200 | fpr95 | 0.5226 ± 0.1041 | foss 0.7790 ± 0.0496 | **THẮNG** |
| 200 | aupr_out | 0.7470 ± 0.0208 | closr 0.7221 ± 0.0234 | **THẮNG** |
| 200 | oscr | 0.8718 ± 0.0029 | closr 0.7745 ± 0.0521 | **THẮNG** |
| 200 | open_world_macro_f1 | 0.3420 ± 0.0503 | foss 0.4348 ± 0.0718 | thua |

Thắng theo k: k=0: 0/5, k=10: 3/5, k=50: 4/5, k=200: 4/5
