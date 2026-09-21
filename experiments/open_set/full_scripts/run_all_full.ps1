param(
    [double]$TimeoutMinutes = 720
)

# Detector-panel protocols, in the order the paper needs them.  The deployment
# layer (RQ1/RQ2 of reports/RQ_DESIGN_2026-09-12.md) runs from cached scores and
# has its own driver: run_pact_full.ps1.
$ErrorActionPreference = 'Stop'

foreach ($protocol in @('loao', 'shift', 'prevalence')) {
    $script = Join-Path $PSScriptRoot ("run_{0}_full.ps1" -f $protocol)
    & $script -TimeoutMinutes $TimeoutMinutes
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
