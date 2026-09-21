# PACT: Prevalence-Aware Conformal Triage for Open-Set Zero-Day Intrusion Detection


This repository contains the PyTorch implementation and experimental pipeline for **PACT**, a deployment procedure for open-set NIDS, together with the open-set detector it is built on and the SOTA panel both are measured against.

The detector reaches 0.9985 unknown AUROC on CICIDS2017 Z1. The central result of this repository is that **that number does not determine whether the detector can be deployed**, and that the gap between ranking and deciding is governed by a resolution barrier no detector improvement can cross. See `reports/THEORY_2026-09-13.md` for the formal results and `reports/PACT_ALGORITHM_2026-09-12.md` for the algorithm.

**The defensible operating point of this system is an attack prevalence of 1%, not 0.1%.** At 10⁻³ no configuration tested produces a queue that is both non-empty and mostly real; that regime is reported as the failure the theory predicts. Every false-discovery figure is an aggregate over a *stream* of traffic partitioned into alert windows — per-window figures and the false fraction of a day's queue diverge sharply, and only the second is what an operator experiences (`reports/WINDOW_SIZE_2026-09-13.md`).

## 🚀 Key Contributions

**Deployment theory and procedure (PACT).**
- **Resolution barrier.** Any distribution-free p-value from `n` calibration flows is floored at `1/(n+1)`, so Benjamini-Hochberg at budget `q` and attack prevalence `π` needs `n ≥ 1/(qπ)` verified-known flows — a sizing rule, independent of alert-window size, not removable by pre-screening, and **not removable by switching to e-values**: every rank-based conformal e-value is capped at `n+1` and e-BH meets the identical threshold.
- **Windowing does not compose.** Per-window FDR control does not bound the false fraction of a day's queue, and the aggregate degrades monotonically as the window shrinks — at a 100-flow window every measured stream exceeded budget. Reach the barrier by buying calibration, not by batching less.
- **Contamination floor.** Below the barrier BH does not go quiet: conditional on emitting any alerts, the queue satisfies `FDP ≥ 1 − mπ/r_min`. Verified on 42 of 42 measured operating points, mean realised false fraction 0.698 while the procedure reported `q = 0.1`.
- **Training-conditional guarantee.** Split-conformal validity is an average over calibration draws; low-prevalence alerting operates exactly at the floor, where the realised false-alarm rate has a standard deviation of the same order as its mean. At `n = 10,000`, marginal BH reports mean FDR 0.098 against a 0.100 budget while one draw in six exceeds 0.3. The Beta-corrected version never does, for a 7% relative power cost where the budget suffices.
- **Certificate, not a number.** PACT emits `certified` / `degraded` / `refuse`, and when it refuses it falls back to a fixed alarm budget that promises a workload rather than a false-discovery rate it cannot keep. It also returns the actionable shortfall ("acquire 10,433 more verified-known flows").
- **Usability frontier.** The power a clairvoyant rule could reach at a given prevalence while holding FDP ≤ q. CICIoMT2024 has 0.888 AUROC and a frontier of 0.000 at every prevalence tested — its extreme tail is inverted — which no aggregate ranking metric reveals.

**Detector.**
- **Pure Zero-Day Detection:** Operates strictly without synthetic unknown data, boundary exposure, or target-domain labels during training/validation.
- **Tail-lifted conformal fusion:** the fused score `-Σ wᵢ log pᵢ` is bounded *above* by the component p-value floor, tying 2,600 CICIDS2017 test flows at one value. Lifting each component's tail removes the ceiling and raises TPR at a 1e-4 false-alarm rate from 0.136 to 0.235, while AUROC moves by 0.00002. This costs nothing in validity: the score is a function, and the alert-stage p-value is still an exact conformal rank on a disjoint split.
- **Evidential Uncertainty:** Corrected Subjective Logic loss (`dirichlet_kl` applies penalty strictly to false evidence) yielding calibrated Dirichlet evidence over the known families.
- **Hyperbolic geometry (code, not a claim):** Poincaré Ball embeddings are implemented and available via `--curvature`, but `curvature = 0` is the default in every runner here and the ablation puts the manifold within noise on all ten metrics across three seeds (p = 0.23-0.78). It is **not** listed as a contribution.
- **Conformal Fusion Scoring:** Zero-day scores come from `experiments/open_set/conformal.py`, which fuses three complementary tangent-space statistics -- class-conditional Mahalanobis, Relative Mahalanobis (Ren et al. 2021) and 1-NN distance on L2-normalised features (Sun et al., ICML 2022) -- as conformal p-values (Bates et al., Ann. Statist. 2023) combined by Fisher's method. Thresholding a p-value at `alpha` controls the false-alarm rate at `alpha` in finite samples, and the fusion weights are picked by a leave-one-class-out proxy that never sees unknown traffic.
- **Distribution-aware input encoding:** `experiments/open_set/features.py` fits a rank-gauss transform and an optional piecewise-linear quantile expansion (Gorishniy et al., NeurIPS 2022) on the training split. Flow counters are heavy-tailed with large point masses at zero, and normalising that geometry is what lets a micro-MLP match a tree ensemble on closed-set accuracy -- which in turn drives open-set performance (Vaze et al., ICLR 2022). Neither encoder adds a trainable parameter.
- **Ultra-lightweight:** Three backbone profiles selected with `--profile`: `lite` (6,340 parameters), `balanced` (40,836, default) and `max` (162,564). Even `max` is smaller than the CLOSR baseline (226,112), and the reference-free edge scorer runs at 0.0074 ms/flow.

See `reports/PACT_ALGORITHM_2026-09-12.md` for the deployment theory, the algorithm and the evidence, and `reports/HEDL_FINAL_ALGORITHM_2026-09-11.md` for the detector's own design and closed/open-set results.

### Reproducing the deployment results

```bash
python -m experiments.open_set.capture_scores --dataset cicids2017 --scenario Z1 --tail-extension --tag cicids2017_Z1_s13_tail
python -m experiments.open_set.run_resolution --tag cicids2017_Z1_s13_tail --calibration-draws 12
python -m experiments.open_set.run_frontier --tags cicids2017_Z1_s13,cicids2017_Z1_s13_tail
python -m experiments.open_set.run_budget --case unsw_to_ton --seed 13
```

Training happens once per dataset and seed; every sweep reads the same cached scores, so two rows of a table cannot differ by a training run.

## 📊 Research questions, in priority order

Locked in `reports/RQ_DESIGN_2026-09-12.md`. Five seeds, held-out unknown sets, and
a deliberate separation between the questions the paper asks and the protocols
the runners execute — one protocol feeds several questions.

### RQ1 — Attainability *(carries the central claim)*
**Under what conditions on calibration budget, false-discovery budget and attack prevalence does a distribution-free alert-quality guarantee exist, and what is emitted when those conditions fail?**
- Theory: floor `p >= 1/(n+1)`; barrier `n >= 1/(q pi)` with window size cancelling; screening invariance; contamination floor `FDP >= 1 - m pi / r_min`; currency invariance; windowing does not compose.
- **Headline prevalence 1%.** 10⁻³ is measured but carries no positive claim.
- **Reporting unit is the stream**, not the window. Runners: `capture_scores` → `run_resolution` (diagnostics) and `run_window` (the reported aggregate).
- Comparators: every panel detector conformalised identically, plus Bates split-conformal BH, BY, Storey-BH and a full-conformal e-value.
- Claim gate: the contamination bound holds on every below-barrier firing cell across ≥4 datasets × 3 seeds, and ≥1 dataset demonstrates at `pi = 1e-2` a certified guarantee whose stream-level aggregate FDR stays within `q` on every calibration draw.

### RQ2 — Keepability *(carries the deployment claim)*
**When the guarantee holds on average over calibration draws, does it hold for the single calibration sample a deployment actually has, and what does the stronger guarantee cost?**
- Theory: training-conditional floor `Beta(1, n)`; corrected sizing `n >= ln(1/delta)/(q pi)`.
- Protocol: `prevalence` with ≥12 independent calibration draws per `n`.
- Key metric: the distribution of FDR **across calibration draws**, not its mean — the mean is exactly what hides the failure.
- Claim gate: marginal BH over budget on ≥10% of draws in ≥2 datasets, conditional on 0%, power price ≤15% relative.

### RQ3 — Reachability *(carries the detector-side claim)*
**Once a guarantee is available, what caps attainable power, and can the cap be raised without spending validity?**
- Usability frontier and prevalence floor; the conformal-fusion score ceiling and its tail lift; known-class heterogeneity as a top-of-ranking precision cap; the Mondrian break-even condition `n >= G/(q pi c_g)`.
- Protocols: `loao`, `prevalence`. Runners: `capture_scores --tail-extension`, `run_frontier`.
- The classical panel (AUROC, FPR95, OSCR, macro-F1) is reported to establish competitiveness — it is not the answer.

### RQ4 — Behaviour under shift *(reduced; carries the honesty claim)*
**When the environment changes so the guarantee no longer applies, does the system detect that and abstain, and what does a target labelling budget buy?**
- Two components only: the exchangeability gate, and the two-currency label budget (family labels buy ranking and saturate; verified-known flows buy the right to make a claim).
- Protocol: `shift` — openness `O1…O50` and near/far rotations as controlled shift generators.
- **Cross-dataset transfer was removed as a research question** and is reported as a measured impossibility with a causal localisation. This takes the temporal-data question off the critical path.
- Claim gate: the gate fires on ≥90% of shift conditions where AUROC collapses with ≤10% false refusal on exchangeable traffic.

### Supporting protocol (not a research question)
Leave-one-attack-family-out against CLOSR, EFC, RENOIR-DML, ORI and DOC++, with the closed backbone as internal control. Its only job is to show that the deployment results are not an artefact of a weak detector.

### Explicitly out of scope
Cross-dataset open-set **transfer** as a solved problem (every panel method at chance; oracle post-hoc repair 0.533 against a 0.93 supervised probe; shared family labels are semantically different phenomena across testbeds); hyperbolic geometry as a contribution; a new multiple-testing procedure; "first conformal NIDS"; host-level alert aggregation as an evaluated escape (degenerate on public benchmarks).

## 🛠️ Reproducibility

### Setup
```bash
pip install -r requirements.txt
```

### Deployment layer (RQ1–RQ3)
```bash
python -m experiments.open_set.capture_scores --dataset cicids2017 --scenario Z1 --tail-extension --tag cicids2017_Z1_s13_tail
python -m experiments.open_set.run_resolution --tag cicids2017_Z1_s13_tail --calibration-draws 12
python -m experiments.open_set.run_frontier --tags cicids2017_Z1_s13,cicids2017_Z1_s13_tail
python -m experiments.open_set.run_budget --case unsw_to_ton --seed 13
```

Training happens once per dataset and seed; every sweep reads the same cached scores, so two rows of a table cannot differ by a training run.

### Detector-panel protocols
```bash
python -m experiments.open_set.run_loao_ours --smoke
python -m experiments.open_set.run_shift_ours --smoke
python -m experiments.open_set.run_prevalence_ours --smoke
```

A single condition, directly:
```bash
python -m experiments.open_set.run --protocol-group loao --protocol loao --dataset cicids2017 --scenario Z1 --methods hedl,ori --epochs 30 --batch-size 256
```

Everything, across datasets and seeds:
```bash
pwsh experiments/open_set/full_scripts/run_pact_full.ps1   # deployment layer
pwsh experiments/open_set/full_scripts/run_all_full.ps1    # detector panel
```

## 📝 Performance note (PCF vs the Q1 baseline panel)

**Superseded by the full run; the pilot numbers that used to sit here were three
seeds on one rotation and are no longer the evidence.** The current panel result,
regenerated by `python -m experiments.open_set.paper_tables`, is eight detectors
over four datasets, eleven leave-one-attack-out rotations and five seeds:

| method | mean unknown AUROC | mean rank |
| --- | ---: | ---: |
| **PCF (this work, `hedl`)** | **0.926** | **1.45** |
| usfAD | 0.876 | 4.00 |
| AIS-NIDS | 0.828 | 5.00 |
| RENOIR-DML | 0.814 | 4.27 |
| ORI | 0.794 | 4.36 |
| CLOSR | 0.793 | 5.36 |
| DOC++ | 0.737 | 6.00 |
| EFC | 0.725 | 5.55 |

PCF ranks first on 10 of the 11 rotations (Friedman p = 6.1e-4). Taking the
rotation as the unit of replication, the Holm-corrected signed-rank test
separates it from ORI, EFC and DOC++ (p ≤ 0.015) but **not** from usfAD,
RENOIR-DML, AIS-NIDS or CLOSR (p = 0.129): eleven rotations is not enough power
to split the top half of the panel, and the paper says so. The detector table is
a supporting result; the claims the paper makes are about alert-quality
guarantees, not about detector ranking.

## Method name

The detector is written up as **Prototype Conformal Fusion (PCF)**: a
prototype-trained encoder whose open-set score is a Fisher fusion of conformal
p-values over class-conditional Mahalanobis, relative Mahalanobis and 1-NN
distances. Code, CLI flags and every result file keep the historical identifier
`hedl`, so anything published before this rename still resolves. Two components
of the earlier name were dropped after measuring them against their own removal:
hyperbolic geometry (-0.0003 unknown AUROC, and every capture ran at curvature 0)
and the Dirichlet evidential term (+0.0000 pooled over ten paired runs,
p = 1.00). Both appear in the paper as negative ablations; see
`results/paper/paper_tables.md`, section "What the method's name may claim".

## Reproducing the paper

```
python scripts/reproduce.py --dry-run      # print the plan
python scripts/reproduce.py --stage analysis   # every table from cached scores, minutes
python scripts/reproduce.py                # everything, ~107 machine-hours
```

Each stage writes one file per job and skips jobs whose output exists, so the run
is interruptible and resumable. `results/paper/environment.json` records the
machine, the package versions, the git commit, the per-stage wall clock and a
content hash for each partition split; it is written by
`python -m experiments.open_set.environment` and never by hand. The reference run
used an RTX 3050 6GB laptop GPU with 12 CPU cores and took 106.9 machine-hours,
of which 35.6 were the rotation captures.
