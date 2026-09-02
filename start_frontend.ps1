# start_frontend.ps1
# Installs npm deps and starts the Vite dev server.

Set-Location frontend

Write-Host "[setup] Installing frontend dependencies..." -ForegroundColor Cyan
npm install

Write-Host "[dev] Starting Vite on http://localhost:5173" -ForegroundColor Green
npm run dev
