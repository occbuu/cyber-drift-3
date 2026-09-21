param(
    [string]$TagA = 'cse2018_panelA',
    [string]$TagB = 'cse2018_panelB',
    [string[]]$MethodsA = @('hedl', 'closr', 'efc', 'renoir_dml'),
    [string[]]$MethodsB = @('ori', 'docpp', 'ais_nids', 'usfad')
)

# Does the resolution barrier bind every detector, or only ours?
#
# The barrier is a statement about the calibration sample, so it should not care
# which detector produced the scores.  That is a prediction, and this script
# tests it by running the identical sweep over every method in the panel from
# its own cached scores.  A method-specific result here would falsify the
# framing; a uniform one turns a claim about our detector into a claim about the
# field.

$ErrorActionPreference = 'Continue'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
Set-Location -LiteralPath $Root
$env:PYTHONPATH = $Root
New-Item -ItemType Directory -Force -Path 'results/resolution/panel' | Out-Null

foreach ($pair in @(@{tag = $TagA; methods = $MethodsA }, @{tag = $TagB; methods = $MethodsB })) {
    if (-not (Test-Path "results/scores/$($pair.tag).npz")) {
        Write-Output "missing scores: $($pair.tag) - skipping"
        continue
    }
    foreach ($method in $pair.methods) {
        $out = "results/resolution/panel/$($method)_barrier.json"
        if (Test-Path $out) { Write-Output "skip $method"; continue }
        Write-Output "=== barrier sweep: $method ==="
        python -m experiments.open_set.run_resolution `
            --tag $pair.tag --method $method `
            --repeats 400 --calibration-draws 6 `
            --calibration-sizes 4000,12000,23932 `
            --prevalences 0.01,0.001 --q-levels 0.1 `
            --pvalue-modes distribution_free,training_conditional,e_bh,clairvoyant `
            --output $out *> "results/resolution/panel/$($method)_barrier.log"
    }
}

Write-Output 'panel barrier sweep complete'
