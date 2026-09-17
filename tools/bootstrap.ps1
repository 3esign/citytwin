# CityTwin bootstrap (Windows): uv + venv OUTSIDE the project folder.
# Why outside: on the PC, executables launched from D:\Svemir\!Projekti hang (uv --version never
# returns) while the same file copied to C: runs instantly (KNOWLEDGE.md, 2026-09-17).
# Environment root: $env:CITYTWIN_ENV, default %LOCALAPPDATA%\citytwin
$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue'
$root = Split-Path -Parent $PSScriptRoot
$envroot = if ($env:CITYTWIN_ENV) { $env:CITYTWIN_ENV } else { Join-Path $env:LOCALAPPDATA 'citytwin' }
$tools = Join-Path $envroot 'tools'; New-Item -ItemType Directory -Force $tools | Out-Null
$uv = Join-Path $tools 'uv.exe'
if (-not (Test-Path $uv)) {
  $zip = Join-Path $tools 'uv.zip'
  Invoke-WebRequest -UseBasicParsing -OutFile $zip 'https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip'
  Expand-Archive -Force $zip $tools; Remove-Item $zip
}
& $uv --version
$venv = Join-Path $envroot 'venv'
$py = Join-Path $venv 'Scripts\python.exe'
if (-not (Test-Path $py)) { & $uv venv $venv --python 3.12 }
& $uv pip install --python $py -r (Join-Path $root 'requirements.txt')
& $py -c "import duckdb, rasterio, numpy, shapely, pyproj, geopandas, networkx; print('env ok', duckdb.__version__, rasterio.__version__)"
Write-Output "PYTHON=$py"
