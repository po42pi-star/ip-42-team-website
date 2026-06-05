# start-faq.ps1 - Запуск FAQ сервера

Write-Host "================================" -ForegroundColor Cyan
Write-Host "FAQ Widget Server" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Проверка .env файла
if (-not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found in widget directory!" -ForegroundColor Red
    Write-Host "Please create .env file with your API key." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Example .env content:" -ForegroundColor Yellow
    Write-Host "  OPENAI_API_KEY=sk-your-key-here" -ForegroundColor White
    Write-Host "  OPENAI_BASE_URL=https://api.proxyapi.ru/openai/v1" -ForegroundColor White
    exit 1
}

# Проверка наличия индекса
if (-not (Test-Path "data\faiss_index.bin")) {
    Write-Host "WARNING: faiss_index.bin not found!" -ForegroundColor Yellow
    Write-Host "Building index first..." -ForegroundColor Yellow
    Write-Host ""
    python build_index.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to build index!" -ForegroundColor Red
        exit 1
    }
    Write-Host ""
}

Write-Host "Starting FAQ server on http://localhost:8000..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Health Check: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""

# Запуск сервера
uvicorn app:app --host 0.0.0.0 --port 8000
