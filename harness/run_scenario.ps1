param(
    [Parameter(Mandatory = $true)]
    [string]$ScenarioId
)

$scriptPath = Join-Path $PSScriptRoot "run_scenario.py"
$python = "python"
$env:PYTHONUNBUFFERED = "1"

& $python "$scriptPath" $ScenarioId @args
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

