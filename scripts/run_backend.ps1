# FreightMind AI — Backend Startup Script
Write-Host "[FreightMind AI] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Cyan
Set-Location -Path (Split-Path -Parent $PSScriptRoot)
& .\.venv\Scripts\uvicorn.exe backend.main:app --reload --port 8000
