# start_backend.ps1
# Starts the IssueRouter FastAPI backend.
# Run this from the project root: .\start_backend.ps1

$ErrorActionPreference = "Stop"

Set-Location "$PSScriptRoot\backend"

# Check if venv exists; create if not
if (-not (Test-Path ".venv")) {
    Write-Host "[setup] Creating Python virtual environment..." -ForegroundColor Cyan
    py -m venv .venv
}

# Activate virtual environment
Write-Host "[setup] Activating virtual environment..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "[setup] Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Install all dependencies from requirements.txt
Write-Host "[setup] Installing backend dependencies from requirements.txt..." -ForegroundColor Cyan

if (Test-Path "requirements.txt") {
    python -m pip install -r requirements.txt
}
else {
    Write-Host "[ERROR] backend\requirements.txt was not found." -ForegroundColor Red
    exit 1
}

# Verify Groq installation
Write-Host "[setup] Checking Groq package..." -ForegroundColor Cyan
python -c "from groq import Groq; print('Groq package installed successfully')"

# Seed the database
Write-Host "[seed] Seeding database with Jharkhand Societal Innovation Clusters..." -ForegroundColor Cyan
python seed_all.py

# Start the server
Write-Host "[server] Starting FastAPI on http://localhost:8000" -ForegroundColor Green
Write-Host "[server] API docs: http://localhost:8000/docs" -ForegroundColor Green

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000