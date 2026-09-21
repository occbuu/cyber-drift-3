param(
    [double]$TimeoutMinutes = 720
)

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
Set-Location -LiteralPath $Root
$env:PYTHONPATH = $Root

python -m experiments.open_set.run_prevalence_ours --resume --timeout-minutes $TimeoutMinutes
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python -m experiments.open_set.run_prevalence_baselines --resume --timeout-minutes $TimeoutMinutes
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python -m experiments.open_set.aggregate_results --protocol-group prevalence --strict --output-dir results/protocols/aggregate/prevalence
exit $LASTEXITCODE
