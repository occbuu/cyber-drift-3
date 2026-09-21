param(
    [int[]]$Seeds = @(37, 73),
    [string[]]$Datasets = @('nf_cse_cic_ids2018_v3', 'cicids2017'),
    [string]$Scenario = 'Z1'
)

# Replication of the panel study across training seeds.
#
# Every headline number in PANEL_BARRIER and ADAPTER_EXCLUSION currently rests
# on seed 13.  The finding most exposed by that is the category-flip result --
# five of eight methods changing deployability class between two datasets --
# because seed noise is an alternative explanation for a category change.  This
# script exists to remove that alternative, so it captures the same eight
# methods under the same protocol and varies only the training seed.
#
# Batches of four keep a single failure from discarding an hour of training.

$ErrorActionPreference = 'Continue'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
Set-Location -LiteralPath $Root
$env:PYTHONPATH = $Root
New-Item -ItemType Directory -Force -Path 'results/scores', 'results/frontier', 'results/resolution' | Out-Null

$batches = @(
    @{ suffix = 'A'; methods = 'hedl,closr,efc,renoir_dml' },
    @{ suffix = 'B'; methods = 'ori,docpp,ais_nids,usfad' }
)
$shortName = @{ 'nf_cse_cic_ids2018_v3' = 'cse2018'; 'cicids2017' = 'cicids2017' }

foreach ($seed in $Seeds) {
    foreach ($dataset in $Datasets) {
        foreach ($batch in $batches) {
            $tag = "$($shortName[$dataset])_panel$($batch.suffix)_s$seed"
            if (Test-Path "results/scores/$tag.npz") { Write-Output "skip $tag"; continue }
            Write-Output "=== capture $tag ==="
            python -m experiments.open_set.capture_scores `
                --dataset $dataset --scenario $Scenario --methods $batch.methods `
                --epochs 30 --seed $seed --tuning-fraction 0.2 --no-tail-extension `
                --tag $tag *> "results/scores/$tag.log"
            if ($LASTEXITCODE -ne 0) { Write-Output "  FAILED $tag" }
        }
    }
}

# Frontier and failure-shape classification for every captured panel, seed 13
# included so the comparison is made on one consistent analysis pass.
$allTags = @()
foreach ($seed in @(13) + $Seeds) {
    foreach ($dataset in $Datasets) {
        foreach ($batch in $batches) {
            $tag = if ($seed -eq 13) { "$($shortName[$dataset])_panel$($batch.suffix)" }
                   else { "$($shortName[$dataset])_panel$($batch.suffix)_s$seed" }
            if (Test-Path "results/scores/$tag.npz") { $allTags += $tag }
        }
    }
}
if ($allTags.Count -gt 0) {
    Write-Output "=== frontier over $($allTags.Count) panel captures ==="
    python -m experiments.open_set.run_frontier `
        --tags ($allTags -join ',') `
        --methods hedl,closr,efc,renoir_dml,ori,docpp,ais_nids,usfad `
        --prevalences 0.25,0.1,0.05,0.02,0.01,0.005,0.001 `
        --target-prevalence 0.01 --repeats 300 `
        --output results/frontier/panel_replication.json *> results/frontier/panel_replication.log
}

# The positive demonstration (RQ1 claim gate b) on the replication seeds.
foreach ($seed in $Seeds) {
    $tag = "cse2018_panelA_s$seed"
    if (-not (Test-Path "results/scores/$tag.npz")) { continue }
    Write-Output "=== sizing sweep $tag (hedl) ==="
    python -m experiments.open_set.run_resolution `
        --tag $tag --method hedl --repeats 400 --calibration-draws 6 `
        --calibration-sizes 4000,12000,23932 `
        --prevalences 0.01,0.001 --q-levels 0.1 `
        --pvalue-modes distribution_free,training_conditional,e_bh,clairvoyant `
        --output "results/resolution/positive_demo_s$seed.json" *> "results/resolution/positive_demo_s$seed.log"
}

Write-Output 'replication complete'
