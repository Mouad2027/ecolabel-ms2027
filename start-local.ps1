# EcoLabel-MS Local Development Startup Script
# Run this script to start all services locally without Docker

$ErrorActionPreference = "Continue"
$BaseDir = "C:\projects\ecolabel-ms"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  EcoLabel-MS Local Development Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Install all dependencies first
Write-Host "`n[1/2] Installing Python dependencies..." -ForegroundColor Yellow

$packages = @(
    "fastapi",
    "uvicorn[standard]",
    "sqlalchemy",
    "psycopg2-binary",
    "pydantic",
    "python-dotenv",
    "python-multipart",
    "pdfplumber",
    "beautifulsoup4",
    "pytesseract",
    "pyzbar",
    "Pillow",
    "spacy",
    "scikit-learn",
    "numpy",
    "pandas",
    "requests",
    "aiohttp"
)

pip install $packages --user --quiet 2>$null

Write-Host "[2/2] Starting services..." -ForegroundColor Yellow

# Start Parser Service (Port 8001)
Write-Host "`nStarting Parser Service on port 8001..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$BaseDir\parser-produit'; `$env:DATABASE_URL='sqlite:///./parser.db'; python -m uvicorn main:app --port 8001 --host 127.0.0.1"

Start-Sleep -Seconds 2

# Start Scoring Service (Port 8004)
Write-Host "Starting Scoring Service on port 8004..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$BaseDir\scoring'; `$env:DATABASE_URL='sqlite:///./scoring.db'; python -m uvicorn main:app --port 8004 --host 127.0.0.1"

Start-Sleep -Seconds 2

# Start Widget API (Port 8005)
Write-Host "Starting Widget API on port 8005..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$BaseDir\widget-api\backend'; `$env:DATABASE_URL='sqlite:///./widget.db'; python -m uvicorn main:app --port 8005 --host 127.0.0.1"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Services Starting!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nAccess points:" -ForegroundColor White
Write-Host "  Parser API:  http://localhost:8001/docs" -ForegroundColor Gray
Write-Host "  Scoring API: http://localhost:8004/docs" -ForegroundColor Gray
Write-Host "  Widget API:  http://localhost:8005/docs" -ForegroundColor Gray
Write-Host "`nNote: NLP and LCA services require additional setup (spaCy models, torch)" -ForegroundColor Yellow
