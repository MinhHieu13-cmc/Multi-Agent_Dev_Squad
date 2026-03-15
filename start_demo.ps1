# Neos Autonomous Dev Squad - Demo Launcher (Windows PowerShell)
# Usage: .\start_demo.ps1

$ErrorActionPreference = "Stop"

$Root      = $PSScriptRoot
$Uvicorn   = Join-Path $Root "venv\Scripts\uvicorn.exe"
$Streamlit = Join-Path $Root "venv\Scripts\streamlit.exe"
$LogDir    = Join-Path $Root "logs"

Write-Host ""
Write-Host "  NEOS AUTONOMOUS DEV SQUAD" -ForegroundColor Cyan
Write-Host "  Mission Launcher - Windows Edition" -ForegroundColor Cyan
Write-Host "  -----------------------------------" -ForegroundColor DarkGray
Write-Host ""

# Pre-flight checks
if (-not (Test-Path $Uvicorn)) {
    Write-Host "[ERROR] venv not found. Run:" -ForegroundColor Red
    Write-Host "        python -m venv venv" -ForegroundColor Yellow
    Write-Host "        .\venv\Scripts\activate" -ForegroundColor Yellow
    Write-Host "        pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $Streamlit)) {
    Write-Host "[ERROR] streamlit not found. Run: pip install streamlit" -ForegroundColor Red
    exit 1
}

if (-not (Get-Command ngrok -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] ngrok not found. Download from https://ngrok.com/download" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path (Join-Path $Root ".env"))) {
    Write-Host "[WARN]  No .env file found. Create one with GOOGLE_API_KEY=<your-key>" -ForegroundColor Yellow
}

Write-Host "[OK]    All pre-flight checks passed." -ForegroundColor Green

# Create log directory
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

# Start FastAPI backend
Write-Host ""
Write-Host "[1/3]  Starting FastAPI backend on port 8000..." -ForegroundColor Cyan

$BackendLog = Join-Path $LogDir "backend.log"
$BackendProc = Start-Process `
    -FilePath $Uvicorn `
    -ArgumentList @("worker:app", "--host", "0.0.0.0", "--port", "8000") `
    -WorkingDirectory $Root `
    -RedirectStandardOutput $BackendLog `
    -RedirectStandardError  "$LogDir\backend_err.log" `
    -NoNewWindow -PassThru

Write-Host "[OK]    FastAPI PID $($BackendProc.Id) -> http://localhost:8000" -ForegroundColor Green
Write-Host "        Log: logs\backend.log" -ForegroundColor DarkGray

Start-Sleep -Seconds 2

# Start Streamlit frontend
Write-Host ""
Write-Host "[2/3]  Starting Streamlit frontend on port 8501..." -ForegroundColor Cyan

$FrontendLog = Join-Path $LogDir "frontend.log"
$FrontendProc = Start-Process `
    -FilePath $Streamlit `
    -ArgumentList @("run", "app_ui.py", "--server.port", "8501", "--server.headless", "true", "--browser.gatherUsageStats", "false") `
    -WorkingDirectory $Root `
    -RedirectStandardOutput $FrontendLog `
    -RedirectStandardError  "$LogDir\frontend_err.log" `
    -NoNewWindow -PassThru

Write-Host "[OK]    Streamlit PID $($FrontendProc.Id) -> http://localhost:8501" -ForegroundColor Green
Write-Host "        Log: logs\frontend.log" -ForegroundColor DarkGray

Start-Sleep -Seconds 3

# Launch ngrok in the foreground
Write-Host ""
Write-Host "[3/3]  Opening ngrok tunnel to port 8501..." -ForegroundColor Cyan
Write-Host ""
Write-Host "  ============================================" -ForegroundColor White
Write-Host "    Your public demo URL will appear below:  " -ForegroundColor White
Write-Host "  ============================================" -ForegroundColor White
Write-Host ""

try {
    & ngrok http 8501
}
finally {
    Write-Host ""
    Write-Host "[SHUTDOWN] Stopping demo stack..." -ForegroundColor Yellow

    if ($null -ne $BackendProc -and -not $BackendProc.HasExited) {
        Stop-Process -Id $BackendProc.Id -Force -ErrorAction SilentlyContinue
        Write-Host "[SHUTDOWN] FastAPI stopped." -ForegroundColor Yellow
    }

    if ($null -ne $FrontendProc -and -not $FrontendProc.HasExited) {
        Stop-Process -Id $FrontendProc.Id -Force -ErrorAction SilentlyContinue
        Write-Host "[SHUTDOWN] Streamlit stopped." -ForegroundColor Yellow
    }

    Write-Host "[DONE]   All processes stopped. Mission debrief complete." -ForegroundColor Green
}
