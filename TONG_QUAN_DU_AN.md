# PACT — hồ sơ nghiên cứu self-contained cho Prism

**Ngày rà soát:** 2026-09-18
**Định vị bài:** methodology / evaluation về cảnh báo có bảo đảm thống kê cho open-set NIDS.
**Venue mục tiêu:** *Computer Networks* (Elsevier).
**Tên phương pháp trong bài:** PACT (*Prevalence-Aware Conformal Triage*).
**Tên detector trong bài:** PCF (*Prototype Conformal Fusion*); mã lịch sử trong code và result là `hedl`.

## 1. Tóm tắt một đoạn

Bài nghiên cứu không đề xuất detector mới để thắng AUROC. Bài hỏi một vấn đề triển khai khác: khi NIDS bật cảnh báo cho các flow có thể là zero-day, có thể bảo đảm rằng tỷ lệ cảnh báo sai trong toàn bộ hàng đợi không vượt ngân sách (q) hay không, và hệ thống phải làm gì khi điều kiện bảo đảm không còn đúng. PACT kết hợp detector open-set PCF, conformal p-values, Benjamini–Hochberg (BH), hiệu chỉnh training-conditional theo Beta, kiểm định exchangeability và cơ chế `certified / degraded / refuse`. Kết quả cho thấy khả năng bảo đảm bị giới hạn bởi cỡ calibration và prevalence; ở dưới barrier, false-discovery fraction có sàn không thể tránh. Trên dữ liệu random split, một số operating point ở prevalence 1% đạt FDR trong ngân sách; trên temporal split, audit từ chối 6/6 captures và FDR của thủ tục marginal tăng từ 0.095 lên 0.684. Đây là bài về **khi nào alerting đáng tin và khi nào phải từ chối bảo đảm**, không phải bài về detector SOTA.

## 2. Research problem, gap và câu hỏi trung tâm

### Bài toán

NIDS thường báo cáo AUROC, FPR95 hoặc macro-F1. Những metric này không trả lời câu hỏi của SOC ở prevalence thấp: trong các cảnh báo được đẩy vào queue, bao nhiêu phần trăm là báo nhầm và con số đó có được bảo đảm cho calibration sample đang dùng không? Với zero-day/open-set, unknown family không xuất hiện trong train, calibration hoặc tuning.

Ký hiệu chính:

- (n): số verified-known flows trong calibration;
- (q): FDR budget, chủ yếu 0.05/0.10/0.20;
- π: attack prevalence, từ 0.25 đến (10^{-3}), headline là 0.01;
- (m): số flow trong một alert window;
- FDP: false fraction của một queue/window; FDR: kỳ vọng FDP qua stream;
- power: tỷ lệ unknown attacks được alert.

**Reporting unit chính là stream**, tức nhiều window nối tiếp nhau. Per-window FDP chỉ là chẩn đoán; FDR của union/stream mới là đại lượng operator trải nghiệm.

### Research gap

Khoảng trống không phải “thiếu một detector có AUROC cao hơn”, mà là thiếu một đánh giá deployment-level trả lời đồng thời: (i) resolution của conformal tail có đủ để BH tạo alert ở prevalence thực tế không; (ii) FDR guarantee có giữ được cho đúng calibration sample đang triển khai không; (iii) hệ thống có biết khi exchangeability bị phá vỡ và fail closed không; (iv) random split có đang làm FDR trông đẹp hơn temporal deployment không.

Conformal p-values + BH/BY/e-BH là công cụ đã biết. Novelty nằm ở việc đặc tả barrier/contamination floor cho open-set NIDS, biến chúng thành certificate triển khai, và đánh giá alert stream dưới prevalence thấp, calibration draw và temporal shift.

## 3. Scientific story được chốt

### Core idea

Một detector chỉ tạo ra **ranking**. Để biến ranking thành hàng đợi cảnh báo có lời hứa FDR, cần đủ resolution ở conformal tail, đủ attack prevalence để có số rejections cần thiết, và exchangeability giữa calibration với traffic được chấm. PACT kiểm tra ba điều kiện trước khi phát cảnh báo. Nếu không đủ, nó không nói “FDR được kiểm soát”; nó chuyển sang `degraded` hoặc `refuse` và dùng fallback alert budget.

### Ba đóng góp chính

1. **Attainability boundary.** Từ p-value floor (p_{min}=1/(n+1)), suy ra BH cần xấp xỉ (n\ge 1/(q\pi)). Dưới barrier, nếu procedure vẫn phát (r_{min}) alerts thì FDP có lower bound (1-m\pi/r_{min}). Rank-based conformal e-values có ceiling (n+1), nên đổi currency không thoát barrier.
2. **Fail-closed alerting.** PACT kiểm tra calibration budget, detector headroom và held-out-known exchangeability; output gắn với claim (`certified`, `degraded`, `refuse`) và shortfall cần bổ sung.
3. **Deployment-safe evaluation.** Đánh giá theo stream, prevalence thấp, nhiều calibration draws, temporal split và procedure baselines. Random split trên CSE2018 cho FDR 0.095; temporal split trên cùng dataset/detector cho 0.684.

### Claim đủ evidence

- Contamination floor đúng **340/340** below-barrier firing cells.
- Positive side của RQ1 có **3 cells** ở π = 0.01 với stream FDR trong q ở mọi calibration draw được báo cáo (CSE2018 q=.1/.2; CICIDS2017 q=.2).
- e-BH không vượt Bates BH ở **0/64** panel cells.
- Pre-stream classification khớp outcome **15/16** operating points.
- Temporal audit từ chối **6/6** captures; CSE2018 marginal BH FDR tăng **0.095 → 0.684**.
- Detector panel chỉ là supporting evidence: PCF đứng đầu mean AUROC nhưng margin so với đối thủ mạnh nhất là **−0.001 AUROC [−0.097, +0.070]**; không claim SOTA superiority.

### Claim phải giảm hoặc bỏ

- Không claim “new FDR-control algorithm”; BH, BY, Beta correction là công cụ hiện có.
- Không claim “first conformal NIDS”.
- Không claim universal FDR control under arbitrary shift.
- Không claim positive operating point ở π = (10^{-3}).
- Không claim tail lift cải thiện power nói chung: TPR@(10^{-3}) chỉ tăng 2/4 datasets và mọi chênh lệch nằm trong seed interval.
- Không claim Mondrian/grouping phục hồi power: gate không đạt; grouping nhìn chung làm giảm power.
- Không claim detector PCF vượt toàn bộ SOTA.

## 4. Proposed method

### 4.1 PCF score generator

PCF là detector được dùng để tạo score, không phải đóng góp trung tâm của bài:

1. Rank-Gauss và optional piecewise-linear quantile encoding được fit trên train-only.
2. Micro-MLP prototype encoder học embedding của known attack families; mặc định profile `balanced`.
3. Với flow mới, tính ba statistic: class-conditional Mahalanobis (MD), relative Mahalanobis (RMD), và 1-NN distance trên L2-normalised feature.
4. Mỗi statistic được đổi thành known-only conformal p-value; weights học bằng leave-one-known-class-out proxy, không nhìn unknown.
5. Fused score là Fisher combination (-\sum_i w_i\log p_i). Final alert-stage p-value vẫn là conformal rank trên split tách biệt.

Tail extension (`tail.py`) fit an audited peaks-over-threshold model phía trên empirical anchor để tháo score ties. Đây là sensitivity/mechanism analysis; tail model chỉ được dùng trong claim khi held-out-known audit không bác bỏ.

### 4.2 PACT alerting và certificate

`pact.py` thực hiện: (1) resolution check theo (n,q,\pi,m); (2) two-sample one-sided DKW trên held-out-known scores; (3) training-conditional Beta upper quantile, với δ chia cho số levels/alert budget mà procedure thực sự đọc; (4) cap alerts/window và fallback fixed alert budget; (5) state `certified`, `degraded` hoặc `refuse`; (6) actionable calibration shortfall.

## 5. Datasets, splits và experimental setting

### Deployment datasets

| Dataset | Vai trò/evidence | Timestamp |
|---|---|---|
| CICIDS2017 | detector tốt, calibration hạn chế; temporal/random comparison | Không dùng temporal chính |
| CICIoMT2024 | family-mix/partition shift; certificate từ chối cả 5 seed | Không |
| NF-CSE-CIC-IDS2018-v3 (CSE2018) | positive certified operating point; temporal audit; calibration đủ | Có |
| NF-ToN-IoT-v3 | AUROC khá nhưng usability frontier thấp; temporal/random audit | Có |

Supporting protocol có thêm partitioned datasets để sanity/shift; paper panel chính giới hạn ở bốn deployment datasets trên.

### Open-set protocol và metrics

- Leave-one-attack-family-out; unknown family không xuất hiện trong train, calibration, tuning hoặc checkpoint selection.
- Separability audit gom twin families ở balanced-accuracy threshold 0.80; sensitivity 0.70/0.90 được ghi nhận.
- 5 training seeds: **13, 37, 73, 101, 137**; 30 epochs; batch size 256; PCF `balanced`.
- Cached scores: mọi prevalence/window sweep đọc cùng score capture.
- Random streams dùng Binomial attack counts; stream size 40,000; 20 streams/cell.
- Headline: π = 0.01, window (m=2000), q = 0.10/0.20, calibration (n=12000) cho per-draw study.

Primary alert-quality metrics: stream FDP/FDR, fraction of streams/draws over q, power, alerts/1000 flows, certificate state và audit violation. Supporting detector metrics: unknown AUROC, FPR95, AUPR-Out, OSCR, open-world macro-F1, known accuracy/macro-F1. Báo cáo mean, SD và 95% CI; FAR (10^{-4}) được đánh dấu unresolvable nếu chỉ có 1.6–5.6 known test flows.

## 6. Baselines và provenance

### Detector panel

| Method | Provenance/role |
|---|---|
| PCF (`hedl`) | proposed score generator |
| CLOSR | official clone adapter |
| EFC | official pure-Python reference/adapter; deterministic across seeds |
| RENOIR-DML | source-derived PyTorch adapter |
| ORI | paper reimplementation |
| DOC++ | source-derived adapter |
| AIS-NIDS | paper reimplementation; cloned artifacts chỉ hỗ trợ |
| usfAD | paper reimplementation |

Auxiliary sanity scorers: MSP, Energy, ODIN, Mahalanobis, OpenMax. Procedure baselines: Bates split-conformal BH, BH marginal, BY, Storey-BH, e-BH/full-conformal e-value comparator. Cùng FDR wrapper được áp dụng cho mọi detector.

## 7. RQ1–RQ4: câu hỏi, experiment, evidence và kết luận

### RQ1 — Attainability

**Câu hỏi:** Với (n,q,\pi) nào thì distribution-free alert-quality guarantee tồn tại, và khi fail thì queue có đặc tính gì?

**Experiment:** `capture_scores` → `run_resolution` → `run_window`; prevalences 0.25/0.10/0.05/0.01/0.001; q 0.05/0.10/0.20; windows 100–4000.

**Kết quả:** contamination floor **340/340**; e-BH không vượt Bates BH **0/64**; tại π=.01 có CSE2018 q=.10 (FDR .0357, power .430), CSE2018 q=.20 (FDR .0941, power .934), CICIDS2017 q=.20 (FDR .0721, power .228). Ở π=.001 không có operating point dương để claim deployment; ba cell lớn nhất vẫn còn power .148–.215 nên không được viết “mọi method đều zero power”.

**Support:** mạnh cho barrier, floor, currency invariance và vùng positive tại 1%; không support claim mạnh hơn ở 0.1%.

**Evidence:** `results/paper/paper_tables.json` (`rq1_contamination`, `rq1_panel_barrier`, `rq1_rq2_draws`); `results/resolution/`; `results/window/`; `reports/THEORY_2026-09-13.md`; `reports/WINDOW_SIZE_2026-09-13.md`.

**Limitations:** π là operating assumption; cached-score stream chưa phải live packet stream; temporal dependence trong traffic không được mô phỏng đầy đủ; per-window FDR không phải day-level guarantee.

### RQ2 — Keepability for one calibration sample

**Câu hỏi:** Marginal conformal validity là trung bình qua calibration draws; một calibration sample triển khai thật có giữ được lời hứa không, và giá power là bao nhiêu?

**Experiment:** `run_resolution --calibration-draws`, `results/window_draws/`, n=12,000, 5 seeds × 5 subsamples, PACT shipped `L=100`, sensitivity L=1/5/20/100/2000.

| Cell | Marginal draws > q | PACT L=100 draws > q | Power | Power price |
|---|---:|---:|---:|---:|
| CSE2018, q=.20 | 20% | 0% | .934 | 6.2% |
| CSE2018, q=.10 | 36% | 0% | .430 | 55.6% |
| CICIDS2017, q=.20 | 4% | 0% | .228 | 68.5% |

**Support:** conditional procedure giữ budget trên certified cells; composite gate đăng ký trước (marginal >10% ở ≥2 dataset, conditional 0%, giá power ≤15%) chỉ đạt **1 cell**, CSE2018 q=.20. Không diễn giải convenience `met` flag trong generated table là gate đầy đủ.

**Evidence:** `results/paper/paper_tables.json:rq1_rq2_draws`; `results/window_draws/`; `results/paper/figures/fig_rq1_rq2_keepability.*`; `reports/RESULTS_AUDIT_2026-09-17.md` §2.1–2.2.

**Limitations:** 0/25 exceedance có one-sided 95% upper bound khoảng 11.3%; 25 draw không phải 25 calibration clusters độc lập. Giá power phụ thuộc detector/headroom, không phải “7%” cố định.

### RQ3 — Reachability và detector-side limits

**Câu hỏi:** Sau khi có guarantee, điều gì giới hạn power hữu ích; tail extension hoặc grouping có nâng ceiling mà không tiêu validity không?

**Experiment:** LOAO panel, `run_frontier`, `capture_scores --tail-extension`, `run_mondrian`, separability audit.

**Kết quả:** panel PCF mean unknown AUROC **.926**, rotation-level mean rank **1.45** trên 11 rotations (seed-level secondary mean rank **1.42**); margin so strongest competitor **−.001 [−.097,+.070]**, nên không claim detector superiority. Tail extension giảm ties ở CSE2018 4199.6→1, CICIDS2017 886.2→1, ToN-IoT 12→1, CICIoMT 2.6→1; TPR@1e-3 chỉ tăng 2/4 datasets và mọi delta nằm trong seed interval. Mondrian trên predicted-class, port-class và protocol không tạo lift hữu ích; một group vượt zero chỉ .00025 (rounding artefact), verdict đúng 59/80 groups.

**Support:** negative/mechanism result được support; registered positive tail/Mondrian gates **không đạt**. Scientific conclusion: score ceiling là thật và Proposition 11 giải thích tại sao grouping không tập trung attack sẽ làm mất resolution.

**Evidence:** `results/paper/paper_tables.json` (`rq3_panel`, `rq3_tail`, `rq3_mondrian`, `rq3_frontier`, `rq3_separability_sensitivity`); `results/frontier/`; `results/mondrian/`; `results/paper/figures/fig_rq3_*.{pdf,png}`; `reports/RESULTS_AUDIT_2026-09-17.md` §3.

**Limitations:** rotation là unit độc lập, seed là replicate; một số rotation nhỏ; covariate grouping còn exploratory; PCF không được claim thắng toàn bộ baseline.

### RQ4 — Shift và abstention

**Câu hỏi:** Khi deployment environment thay đổi, hệ thống có nhận ra guarantee không còn áp dụng và abstain không; label budget mua được gì?

**Experiment:** `run_shift_gate`, `run_budget`, `build_temporal`, temporal operator/audit.

**Kết quả gate:** aggregate detection **90.6%**, false refusal **8.0%** theo exchangeable definition đã ghi rõ. Per dataset: CICIDS2017 **59.8% / 10.3%** (fail cả hai), CSE2018 **93.5% / 6.7%**, ToN-IoT **93.3% / 7.0%**; CICIoMT baseline partition đã refuse. Cross-domain budget phát hiện mismatch 100%; false refusal trên adapted/matched arm 4.3%; verified-known flows chuyển refuse→degraded, không đạt certified.

**Temporal:** CSE2018 random audit violation .0049 vs DKW .0107, temporal .1418 vs .0111; random refuse 0/3, temporal refuse 3/3. Tổng hai dataset temporal refuse **6/6**. CSE2018 marginal FDR .0951 random→.6843 temporal; PACT L=100 .0334→.5855. Procedures nào còn emit alerts đều vượt q=.10 trên temporal split.

**Operator baseline:** trên CSE2018, policy báo top 0.1% vượt q ở **40%** stream; ở π=​(10^{-3}), FDP trung bình là **0.497**. Đây là đối chứng trực tiếp cho việc fixed alert quota không tự tạo ra FDR guarantee.

**Support:** aggregate gate đạt nhưng per-dataset failure phải được trình bày; gate chỉ phát hiện observed guarantee-breaking shifts, không chứng minh exchangeability khi audit pass.

**Evidence:** `results/paper/paper_tables.json` (`rq4_shift_gate`, `rq4_budget`, `temporal`); `results/shift_gate/`; `results/budget/`; `results/operator/`; `results/paper/figures/fig_rq4_temporal_shift.*`.

**Limitations:** aggregate rows nested; 4.3% là conditional on adapted/matched labelling; mild violations khó phát hiện hơn severe violations.

## 8. Ablation và integrity

| Component | Kết quả | Kết luận |
|---|---|---|
| Encoder removed | AUROC cost tới **.656** | encoder có tác dụng vật chất |
| KNN removed | giữ KNN thêm +.0021 trên CSE2018 | component phụ có tín hiệu nhỏ |
| Curvature .5 vs flat | Δ −.0003, 3 seeds | hyperbolic không phải contribution |
| Evidential term on/off | pooled Δ +.0000, p=.997 | negative ablation, không claim |

`check_claims.py --strict`: **23/23** số khớp `paper_tables.json`. `pytest`: **88 passed**. Không có source-id overlap giữa splits. CSE2018 có 10,505/223,507 flows label collision (4.7%); ToN-IoT có 75. `environment.json` ghi package, machine, git commit, timing và split hashes.

## 9. Figures/tables để Prism dùng

Presentation audit: `reports/Q1_LITERATURE_MATRIX_OPEN_SET_NIDS_2026-09-19.md` records ten recent Q1-style papers and the writing/figure patterns extracted from them. The manuscript follows the common pattern of an operational opening, explicit open-set assumptions, a stage-based method figure, scenario-specific RQs, and captions that state the scientific message.

Plot source: `scripts/plot_paper_figures.py`; input duy nhất: `results/paper/paper_tables.json`; output PNG 300 dpi và vector PDF tại `results/paper/figures/`.

| Figure | Data source | Cấu trúc/metric | RQ | Thông điệp |
|---|---|---|---|---|
| `fig_pact_overview.pdf` | `scripts/plot_pact_overview.py` | two-row deployment flow: evidence construction above, feasibility/validity gates and certification policy below | method | detector ranking and statistical certification are separate decisions; the certificate is fail-closed |
| `fig_rq1_prevalence_barrier.*` | `rq1_panel_barrier` | x prevalence, y training-conditional power | RQ1 | power collapse ở .1%; resolution/prevalence là giới hạn |
| `fig_rq1_rq2_keepability.*` | `rq1_rq2_draws` | FDR và power của Bates/Storey/BY/e-BH/PACT L | RQ1/RQ2 | guarantee mạnh hơn bỏ exceedance nhưng giá power tăng |
| `fig_rq3_tail_lift.*` | `rq3_tail` | ties-at-max và TPR@1e-3, floor vs tail | RQ3 | tháo ties nhưng chưa chứng minh power gain |
| `fig_rq3_detector_panel.*` | `rq3_panel` | mean AUROC ± CI, 8 methods | supporting | PCF là score generator hợp lý, không phải claim SOTA |
| `fig_rq4_temporal_shift.*` | `temporal` | audit violation/bound và random-vs-temporal FDR | RQ4 | random validity không chuyển sang temporal deployment |
| `fig_ablation_components.*` | `method_components` | AUROC change qua ablations | method | encoder là component chính; tên cũ bị rút gọn đúng evidence |

Generated table source: `results/paper/paper_tables.md`; machine-readable source: `results/paper/paper_tables.json`.

## 10. Discussion, limitations và threats to validity

Vùng positive hẹp và chủ yếu ở prevalence 1%; không có positive claim tại .1%. Guarantee phụ thuộc exchangeability và known-only calibration; audit không bác bỏ chỉ là evidence. Temporal traffic cho thấy vì sao fail-closed cần thiết. Public testbeds có staged attack order, label collisions và partition-specific family mix. Cached-score resampling cô lập alert-quality mechanics nhưng chưa thay live packet stream. Chỉ hai datasets có timestamp. RQ4 aggregate cần đi kèm per-dataset và cluster uncertainty. Baseline provenance không đồng nhất (direct clone, source-derived adapter, paper reimplementation) và phải ghi trong paper.

## 11. Key claims và suggested manuscript structure

**Giữ:** attainability region; contamination floor; certificate/abstention; random-vs-temporal optimism; detector-portable evaluation.
**Viết có điều kiện:** mọi “guarantee” phải nêu exchangeability, q, π, n, stream/window estimand và δ; 0/25 phải kèm upper bound; PCF đứng đầu panel không đồng nghĩa universal superiority.
**Bỏ:** new FDR algorithm, first conformal NIDS, universal shift guarantee, positive .1%, tail/Mondrian success, detector SOTA.

Cấu trúc cho *Computer Networks*: (1) Introduction/SOC motivation; (2) background and estimands; (3) resolution theory; (4) PACT certificate; (5) experimental design; (6) RQ1–RQ4 results; (7) discussion/deployment implications; (8) limitations/threats; (9) conclusion. Abstract phải dẫn bằng alert trustworthiness và random/temporal contrast, không dẫn bằng kiến trúc PCF.

## 12. FILES TO UPLOAD TO PRISM

### Required narrative and summaries

- `TONG_QUAN_DU_AN.md`
- `results/paper/paper_tables.md`
- `results/paper/paper_tables.json`
- `results/paper/environment.json`
- `results/paper/prism_summaries/rq1_rq2_keepability.csv`
- `results/paper/prism_summaries/rq3_panel_overall.csv`
- `results/paper/prism_summaries/rq4_temporal.csv`

### Figures

- `results/paper/figures/fig_rq1_prevalence_barrier.pdf` và `.png`
- `results/paper/figures/fig_rq1_rq2_keepability.pdf` và `.png`
- `results/paper/figures/fig_rq3_tail_lift.pdf` và `.png`
- `results/paper/figures/fig_rq3_detector_panel.pdf` và `.png`
- `results/paper/figures/fig_rq4_temporal_shift.pdf` và `.png`
- `results/paper/figures/fig_ablation_components.pdf` và `.png`

### Raw/summary evidence cần thiết

- `results/resolution/` — JSON barrier, conditional stability, procedure comparison và panel resolution; bỏ `.log`.
- `results/window/` — `full_*_panelA_s*_q*.json` và các `rq1_*`/`rq2_*` summary JSON.
- `results/window_draws/` — `algorithm_levels.json`, `rq2_matched_calibration.json`, `full_*_L{1,5,100}.json`.
- `results/shift_gate/` — JSON gate results, bỏ `.log`.
- `results/budget/` — JSON của `loeo_unsw`, `unsw_to_ton`, `ton_to_unsw`.
- `results/mondrian/` — JSON grouping results dùng cho negative RQ3.
- `results/frontier/` — `full_panel_frontier.json`, `panel_seed_aggregated.json`, `usability_frontier.json`, `gate1_frontier.json`.
- `results/latency/` — latency JSON.
- `results/ablation_geometry/`, `results/ablation_knn/`, `results/ablation_backbone.json`.

### Context reports

- `reports/RESULTS_AUDIT_2026-09-17.md`
- `reports/PAPER_CLAIMS_2026-09-17.md`
- `reports/THEORY_2026-09-13.md`
- `reports/PACT_ALGORITHM_2026-09-12.md`
- `reports/RQ_DESIGN_2026-09-12.md`
- `reports/WINDOW_SIZE_2026-09-13.md`
- `reports/Q1_NOVELTY_AUDIT_2026-09-12.md`
- `experiments/open_set/rq_matrix.yaml`

### Không upload mặc định

Không cần upload `results/scores/*.npz`, `results/_archive/`, `.log`, cloned baseline repositories, smoke/pilot outputs hoặc toàn bộ `baselines/`, trừ khi Prism được yêu cầu audit implementation.

## 13. Verification commands

```powershell
$env:PYTHONPATH = (Get-Location).Path
python scripts/plot_paper_figures.py
python -m experiments.open_set.paper_tables
python scripts/check_claims.py --strict
python -m pytest tests -q
python scripts/reproduce.py --stage analysis
```

`reproduce.py --stage analysis` dùng cached scores và đủ cho Prism dựng manuscript; full recapture là bước tốn máy riêng.
