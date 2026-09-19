# FreightMind AI — Full Stack Startup Script (SIH 2026 PS 26006)
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  FreightMind AI — Intelligent Freight & Vessel Optimization" -ForegroundColor Green
Write-Host "  Smart India Hackathon 2026 | PS ID: 26006" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green

$Root = Split-Path -Parent $PSScriptRoot

Write-Host "`n[*] Launching FastAPI Backend on http://localhost:8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Root'; .\.venv\Scripts\uvicorn.exe backend.main:app --reload --port 8000"

Start-Sleep -Seconds 2

Write-Host "[*] Launching React Vite Dashboard on http://localhost:5173..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Root\frontend'; npm run dev"

Write-Host "`n[OK] FreightMind AI is running!" -ForegroundColor Green
Write-Host "     Dashboard: http://localhost:5173" -ForegroundColor Yellow
Write-Host "     Backend:   http://localhost:8000" -ForegroundColor Yellow
Write-Host "     API Docs:  http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "============================================================`n" -ForegroundColor Green
