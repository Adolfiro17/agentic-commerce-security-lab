# One command to run the Adolfiro Market AI commerce lab on Windows. No API key, no cloud account.
#   .\start.ps1             open the lab in your browser (http://localhost:8501)
#   .\start.ps1 matrix      run every attack in both modes
#   .\start.ps1 run 3       run one module in the terminal
#   .\start.ps1 test        run the test suite
#   .\start.ps1 site        serve the course site at http://localhost:8000
param([string]$Command = "app", [Parameter(ValueFromRemainingArguments = $true)][string[]]$Rest)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path .venv)) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Could not create a virtual environment. Install Python 3.11+ from python.org." }
}
$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
& $py -m pip install -q -r requirements.txt

switch ($Command) {
    "app"    { Write-Host "Opening the lab at http://localhost:8501 (Ctrl+C to stop)"; & $py -m streamlit run app.py }
    "matrix" { & $py -m shop.cli matrix }
    "run"    { & $py -m shop.cli run @Rest }
    "test"   { & $py -m pytest -q }
    "site"   { Write-Host "Serving http://localhost:8000 (Ctrl+C to stop)"; & $py -m http.server 8000 --directory docs }
    default  { & $py -m shop.cli $Command @Rest }
}
