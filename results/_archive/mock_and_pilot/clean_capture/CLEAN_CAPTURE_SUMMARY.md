### loeo_unsw

| Dữ liệu mạng mới | Chỉ số | H-EDL | Baseline tốt nhất | Kết quả |
| ---: | --- | --- | --- | --- |
| 0 (khoa) | unknown_auroc | 0.5277 ± 0.0471 | closr 0.5399 ± 0.0079 | thua |
| 0 (khoa) | fpr95 | 0.9037 ± 0.0428 | cd_zd_srl 0.9169 ± 0.0398 | **THẮNG** |
| 0 (khoa) | aupr_out | 0.2168 ± 0.0236 | closr 0.2243 ± 0.0056 | thua |
| 0 (khoa) | oscr | 0.0526 ± 0.0334 | renoir_dml 0.0879 ± 0.0060 | thua |
| 0 (khoa) | open_world_macro_f1 | 0.0368 ± 0.0211 | cd_zd_srl 0.0490 ± 0.0210 | thua |
| 2000 luong, lan 0% | unknown_auroc | 0.5543 ± 0.0146 | foss 0.5644 ± 0.0200 | thua |
| 2000 luong, lan 0% | fpr95 | 0.8123 ± 0.0201 | closr 0.9241 ± 0.0125 | **THẮNG** |
| 2000 luong, lan 0% | aupr_out | 0.2416 ± 0.0057 | foss 0.2680 ± 0.0089 | thua |
| 2000 luong, lan 0% | oscr | 0.1423 ± 0.0009 | closr 0.1158 ± 0.0170 | **THẮNG** |
| 2000 luong, lan 0% | open_world_macro_f1 | 0.1194 ± 0.0145 | cd_zd_srl 0.0522 ± 0.0068 | **THẮNG** |
| 400 luong, lan 0% | unknown_auroc | 0.5866 ± 0.0105 | closr 0.5664 ± 0.0308 | **THẮNG** |
| 400 luong, lan 0% | fpr95 | 0.7973 ± 0.0122 | foss 0.9067 ± 0.0065 | **THẮNG** |
| 400 luong, lan 0% | aupr_out | 0.2438 ± 0.0119 | closr 0.2423 ± 0.0154 | **THẮNG** |
| 400 luong, lan 0% | oscr | 0.2170 ± 0.0095 | foss 0.1397 ± 0.0031 | **THẮNG** |
| 400 luong, lan 0% | open_world_macro_f1 | 0.0562 ± 0.0159 | cd_zd_srl 0.0703 ± 0.0034 | thua |

Thắng theo k: k=0 (khoa): 1/5, k=2000 luong, lan 0%: 3/5, k=400 luong, lan 0%: 4/5

### unsw_to_ton

| Dữ liệu mạng mới | Chỉ số | H-EDL | Baseline tốt nhất | Kết quả |
| ---: | --- | --- | --- | --- |
| 0 (khoa) | unknown_auroc | 0.4998 ± 0.0621 | efc 0.6697 ± 0.0000 | thua |
| 0 (khoa) | fpr95 | 0.8968 ± 0.0272 | cd_zd_srl 0.8428 ± 0.0678 | thua |
| 0 (khoa) | aupr_out | 0.2632 ± 0.0507 | efc 0.5740 ± 0.0000 | thua |
| 0 (khoa) | oscr | 0.1058 ± 0.0221 | foss 0.1648 ± 0.0444 | thua |
| 0 (khoa) | open_world_macro_f1 | 0.0773 ± 0.0227 | foss 0.2066 ± 0.0083 | thua |
| 2000 luong, lan 0% | unknown_auroc | 0.4364 ± 0.0927 | cd_zd_srl 0.6886 ± 0.0502 | thua |
| 2000 luong, lan 0% | fpr95 | 0.8924 ± 0.0048 | cd_zd_srl 0.8834 ± 0.0096 | thua |
| 2000 luong, lan 0% | aupr_out | 0.2367 ± 0.0379 | cd_zd_srl 0.4970 ± 0.0644 | thua |
| 2000 luong, lan 0% | oscr | 0.2036 ± 0.0030 | foss 0.2456 ± 0.0227 | thua |
| 2000 luong, lan 0% | open_world_macro_f1 | 0.1180 ± 0.0160 | foss 0.1819 ± 0.0459 | thua |
| 400 luong, lan 0% | unknown_auroc | 0.5286 ± 0.0542 | efc 0.6681 ± 0.0009 | thua |
| 400 luong, lan 0% | fpr95 | 0.9016 ± 0.0123 | cd_zd_srl 0.8427 ± 0.0658 | thua |
| 400 luong, lan 0% | aupr_out | 0.2771 ± 0.0734 | efc 0.5859 ± 0.0011 | thua |
| 400 luong, lan 0% | oscr | 0.2687 ± 0.0032 | closr 0.2859 ± 0.0055 | thua |
| 400 luong, lan 0% | open_world_macro_f1 | 0.0865 ± 0.0196 | foss 0.2364 ± 0.0262 | thua |

Thắng theo k: k=0 (khoa): 0/5, k=2000 luong, lan 0%: 0/5, k=400 luong, lan 0%: 0/5
