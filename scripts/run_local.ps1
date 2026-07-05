param(
    [string]$venvPath = ".venv",
    [switch]$NoInstall
)

Write-Host "Preparing local run (Windows PowerShell)"

if (-not (Test-Path $venvPath)) {
    python -m venv $venvPath
}

$activate = Join-Path $venvPath 'Scripts\Activate.ps1'
if (Test-Path $activate) {
    Write-Host "Activating venv..."
    & $activate
} else {
    Write-Host "Could not find activation script at $activate" -ForegroundColor Yellow
}

if (-not $NoInstall) {
    Write-Host "Installing Python requirements..."
    pip install -r requirements.txt
}

Write-Host "Starting Flask app (debug mode). Access http://localhost:5000"
python app.py
