# Open-set / zero-day experiment framework

Implements the design locked in `reports/RQ_DESIGN_2026-09-12.md`. Proposed-method
runs and external-baseline runs stay in separate commands and separate output
trees.

## Two levels, deliberately not one-to-one

The paper's **research questions** and the runners' **protocols** are different
things. One protocol feeds several questions, and numbering the protocols after
the questions is what previously made "RQ3" ambiguous between a paper section
and a command-line flag. Both levels are declared in `rq_matrix.yaml`.

| Research question | Priority | Fed by |
| --- | ---: | --- |
| RQ1 attainability — when does an alert-quality guarantee exist, and what is emitted when it does not (headline prevalence **1%**; reporting unit the **stream**) | 1 | `prevalence` |
| RQ2 keepability — does the guarantee hold for the one calibration sample a deployment has | 2 | `prevalence` |
| RQ3 reachability — what caps attainable power, and can the cap be raised without spending validity | 3 | `loao`, `prevalence` |
| RQ4 shift behaviour — does the system detect that its guarantee no longer applies, and what does a label budget buy (**reduced**: gate + label budget only) | 4 | `shift` |

| Protocol | What it executes |
| --- | --- |
| `loao` | leave-one-attack-family-out detector panel across the partitioned datasets |
| `shift` | openness sweep, near/far rotations, cross-domain and leave-one-environment-out — used as **shift generators**, not as a transfer benchmark |
| `prevalence` | operational prevalence, fixed-FPR operating points, and the alert-quality audit |

`rq1` also appears as a directory name inside the frozen `data/v7` partitions.
That is a data artefact and is unrelated to these protocol names.

## Deployment layer (RQ1–RQ3)

| Module | Provides |
| --- | --- |
| `resolution.py` | distribution-free floor, resolution barrier `n >= 1/(q pi)`, contamination floor below it, training-conditional correction, escape routes |
| `tail.py` | peaks-over-threshold extension of a conformal score, bootstrap upper bound, held-out audit |
| `pact.py` | certificate (`certified` / `degraded` / `refuse`), conditional alerting, fixed-alarm-budget fallback, calibration shortfall |
| `run_window.py` | stream-level alert-window sweep — the unit RQ1 reports, with Binomial rather than forced attack counts |
| `anchor_transport.py` | deployment-time reference adaptation on one retention axis, two-currency target label budget |

`capture_scores` trains once and writes scores; every sweep then reads the same
cached scores, so two rows of a table can never differ by a training run.
Training seeds are varied explicitly, outside the sweeps.

```powershell
$env:PYTHONPATH = (Get-Location).Path

# One training run per (dataset, seed); --tail-extension is the RQ3 arm.
python -m experiments.open_set.capture_scores --dataset cicids2017 --scenario Z1 `
  --tail-extension --tag cicids2017_Z1_s13_tail

# RQ1 + RQ2: barrier, contamination floor, per-draw keepability (per-window diagnostics).
python -m experiments.open_set.run_resolution --tag cicids2017_Z1_s13_tail --calibration-draws 12

# RQ1 reported quantity: stream-level aggregate across alert-window sizes.
python -m experiments.open_set.run_window --tag cicids2017_Z1_s13_tail

# RQ3: usability frontier and prevalence floor, floored vs tail-lifted.
python -m experiments.open_set.run_frontier --tags cicids2017_Z1_s13,cicids2017_Z1_s13_tail

# RQ4: target label-budget allocation under shift.
python -m experiments.open_set.run_budget --case unsw_to_ton --seed 13
```

Everything above, across datasets, seeds and transfer cases:

```powershell
& experiments/open_set/full_scripts/run_pact_full.ps1
```

## Detector-panel protocols

### Audit

```powershell
python -m experiments.open_set.audit
```

### Smoke tests

Smoke mode uses one seed, one epoch and at most 500 stratified rows per split.
It verifies execution only and is never publication evidence.

```powershell
python -m experiments.open_set.run_loao_ours --smoke
python -m experiments.open_set.run_loao_baselines --smoke

python -m experiments.open_set.run_shift_ours --smoke
python -m experiments.open_set.run_shift_baselines --smoke

python -m experiments.open_set.run_prevalence_ours --smoke
python -m experiments.open_set.run_prevalence_baselines --smoke
```

### Full runs

```powershell
python -m experiments.open_set.run_loao_ours --epochs 10
python -m experiments.open_set.run_loao_baselines --epochs 30

python -m experiments.open_set.run_shift_ours --epochs 10
python -m experiments.open_set.run_shift_baselines --epochs 30

python -m experiments.open_set.run_prevalence_ours --epochs 10
python -m experiments.open_set.run_prevalence_baselines --epochs 30
```

Each entrypoint writes one JSON per dataset/scenario/seed plus a resumable
manifest under `results/protocols/_runs/`. Use `--resume` to continue an
interrupted sweep and `--dry-run` to count jobs first.

```powershell
& experiments/open_set/full_scripts/run_all_full.ps1
```

Output trees:

```
results/protocols/loao/ours/
results/protocols/loao/baselines/
results/protocols/shift/ours/
results/protocols/shift/baselines/
results/protocols/prevalence/ours/
results/protocols/prevalence/baselines/
```

## Baseline panel

Five primary Q1 baselines per protocol:

- `loao`: CLOSR, EFC, RENOIR-DML, ORI, DOC++.
- `shift`: CLOSR, EFC, RENOIR-DML, FOSS, Cross-dataset Siamese-RL.
- `prevalence`: CLOSR, EFC, RENOIR-DML, AIS-NIDS, usfAD.

CLOSR, EFC and RENOIR-DML are direct adapters from verified source. DOC++ and
FOSS are V7 adapters derived from cloned paper repositories. ORI, Cross-dataset
Siamese-RL, AIS-NIDS and usfAD are labelled `paper_reimplementation` and must
not be described as official author code. MSP, Energy, ODIN, Mahalanobis and
OpenMax are available through `--include-auxiliary` as sanity checks and do not
count among the five competitors.

RQ1 and RQ2 additionally need **procedure** baselines, which are detector-
independent: Bates split-conformal BH, BY, Storey-BH and a full-conformal
e-value comparator. No FDR claim table may be published without them.

## Alert-quality audit

Nested known-only calibration: one half may tune the detector score, the other
half creates the final conformal p-values. The same wrapper is applied to H-EDL
and to every baseline, so a comparison is power at a fixed false-discovery
budget, never whether a detector happened to emit calibrated scores.

```powershell
python -m experiments.open_set.run_fdr `
  --dataset ciciomt2024 --scenario Z1 `
  --methods hedl,closr,efc,renoir_dml,ais_nids,usfad `
  --epochs 3 --max-rows 20000 `
  --alert-batch-size 2000 --repeats 200 `
  --output results/fdr/ciciomt2024_Z1_pilot.json
```

Marginal split-conformal calibration is the primary analysis. Predicted-class
Mondrian is retained as a sensitivity analysis and is **expected** to fail:
grouping divides the calibration budget by `G` while predicted class does not
concentrate attacks, so by the break-even condition `n >= G/(q pi c_g)` it
cannot afford itself. The RQ3 remedy is grouping by a covariate that does
concentrate attacks or does remove known-class heterogeneity.

Held-out-known super-uniformity is audited with a **two-sample** DKW critical
value. A rejected audit, zero power or near-complete abstention is reported as
`not_deployable`; a low empirical FDR caused by emitting no alerts is never
converted into a positive deployment claim.

See `reports/FDR_PILOT_2026-09-12.md` for the pilot findings and
`reports/PACT_ALGORITHM_2026-09-12.md` for the theory that explains them.

## Aggregation

```powershell
python -m experiments.open_set.aggregate_results --strict
```

Writes long-form metrics, mean and 95% confidence intervals, paired one-sided
Wilcoxon tests with Holm correction, Cohen's dz, win/tie/loss counts and
complete-case average ranks under `results/protocols/aggregate/`.
