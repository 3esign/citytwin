# Run a CityTwin step with the project environment:  tools\run.ps1 core\fetch\overture.py trebinje
$envroot = if ($env:CITYTWIN_ENV) { $env:CITYTWIN_ENV } else { Join-Path $env:LOCALAPPDATA 'citytwin' }
$py = Join-Path $envroot 'venv\Scripts\python.exe'
$root = Split-Path -Parent $PSScriptRoot
& $py (Join-Path $root $args[0]) @($args | Select-Object -Skip 1)
exit $LASTEXITCODE
