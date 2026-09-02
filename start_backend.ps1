# start_backend.ps1
# Starts the IssueRouter FastAPI backend.
# Run this from the project root: .\start_backend.ps1

Set-Location backend

# Check if venv exists, create if not
if (-not (Test-Path ".venv")) {
    Write-Host "[setup] Creating Python virtual environment..." -ForegroundColor Cyan
    # Using 'py' because the main 'python' command sometimes isn't in PATH
    py -m venv .venv
}

# Activate venv
Write-Host "[setup] Activating virtual environment..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "[setup] Installing backend dependencies..." -ForegroundColor Cyan
python -m pip install fastapi uvicorn sqlalchemy pydantic

# Seed the database
Write-Host "[seed] Seeding database with 150 clusters..." -ForegroundColor Cyan
python seed.py

# Start the server
Write-Host "[server] Starting FastAPI on http://localhost:8000" -ForegroundColor Green
Write-Host "[server] API docs: http://localhost:8000/docs" -ForegroundColor Green
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
