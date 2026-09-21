param(
    [string[]]$Datasets = @('cicids2017', 'ciciomt2024', 'nf_cse_cic_ids2018_v3', 'nf_ton_iot_v3'),
    [int[]]$Seeds = @(13, 37, 73),
    [string[]]$TransferCases = @('unsw_to_ton', 'ton_to_unsw', 'loeo_unsw')
)

# Deployment layer: RQ1 attainability, RQ2 keepability, RQ3 reachability and the
# RQ4 label-budget study of reports/RQ_DESIGN_2026-09-12.md.
#
# Training happens once per (dataset, seed) in capture_scores; every sweep then
# reads the same cached scores, so two rows of a table can never differ by a
# training run.  That is why this driver is cheap to re-run and why the seed
# loop sits outside the sweeps rather than inside them.

$ErrorActionPreference = 'Continue'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
Set-Location -LiteralPath $Root
$env:PYTHONPATH = $Root
New-Item -ItemType Directory -Force -Path 'results/scores', 'results/resolution', 'results/frontier', 'results/budget' | Out-Null

# --- Score capture: floored and tail-lifted, so RQ3 can compare them ---------
foreach ($dataset in $Datasets) {
    foreach ($seed in $Seeds) {
        foreach ($variant in @(@{suffix = ''; flag = '--no-tail-extension' },
                               @{suffix = '_tail'; flag = '--tail-extension' })) {
            $tag = "${dataset}_Z1_s${seed}$($variant.suffix)"
            if (Test-Path "results/scores/$tag.npz") { Write-Output "skip capture $tag"; continue }
            Write-Output "=== capture $tag ==="
            python -m experiments.open_set.capture_scores `
                --dataset $dataset --scenario Z1 --methods hedl --epochs 30 --seed $seed `
                $variant.flag --tail-confidence 0.9 --tag $tag *> "results/scores/$tag.log"
        }
    }
}

# --- RQ1 + RQ2: barrier, contamination floor, per-draw keepability -----------
foreach ($dataset in $Datasets) {
    foreach ($seed in $Seeds) {
        $tag = "${dataset}_Z1_s${seed}_tail"
        if (-not (Test-Path "results/scores/$tag.npz")) { continue }
        Write-Output "=== resolution sweep $tag ==="
        python -m experiments.open_set.run_resolution `
            --tag $tag --repeats 400 --calibration-draws 12 `
            --calibration-sizes 1000,4000,12000,23025,41873 `
            --prevalences 0.25,0.1,0.05,0.01,0.001 --q-levels 0.05,0.1,0.2 `
            --pvalue-modes distribution_free,training_conditional,tail_extended,clairvoyant `
            --output "results/resolution/${tag}_sweep.json" *> "results/resolution/${tag}_sweep.log"
    }
}

# --- RQ3: usability frontier, floored vs tail-lifted -------------------------
$tags = @()
foreach ($dataset in $Datasets) {
    foreach ($seed in $Seeds) {
        foreach ($suffix in @('', '_tail')) {
            $tag = "${dataset}_Z1_s${seed}${suffix}"
            if (Test-Path "results/scores/$tag.npz") { $tags += $tag }
        }
    }
}
if ($tags.Count -gt 0) {
    Write-Output "=== usability frontier ($($tags.Count) score sets) ==="
    python -m experiments.open_set.run_frontier --tags ($tags -join ',') `
        --output results/frontier/usability_frontier.json *> results/frontier/frontier.log
}

# --- RQ4: target label-budget allocation under shift -------------------------
foreach ($case in $TransferCases) {
    foreach ($seed in $Seeds) {
        $out = "results/budget/${case}_seed${seed}.json"
        if (Test-Path $out) { Write-Output "skip budget $case seed=$seed"; continue }
        Write-Output "=== budget $case seed=$seed ==="
        python -m experiments.open_set.run_budget `
            --case $case --seed $seed `
            --budgets 60,120,300,1000,3000 --family-shots 2,5,10,20 `
            --policies anchors_only,aligned_tenth,aligned_full,selected `
            --output $out *> "results/budget/${case}_seed${seed}.log"
    }
}

Write-Output 'deployment layer complete'
