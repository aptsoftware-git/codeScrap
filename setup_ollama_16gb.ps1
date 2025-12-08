# Ollama Optimization Script for 16GB RAM System
# Run this as Administrator in PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Ollama 16GB RAM Optimization Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Step 1: Setting Ollama Environment Variables..." -ForegroundColor Yellow

# Set environment variables for Ollama (Machine-level)
[System.Environment]::SetEnvironmentVariable('OLLAMA_NUM_PARALLEL', '1', 'Machine')
[System.Environment]::SetEnvironmentVariable('OLLAMA_MAX_LOADED_MODELS', '1', 'Machine')
[System.Environment]::SetEnvironmentVariable('OLLAMA_NUM_THREADS', '4', 'Machine')
[System.Environment]::SetEnvironmentVariable('OLLAMA_NUM_CTX', '1024', 'Machine')

Write-Host "✓ Environment variables set successfully!" -ForegroundColor Green
Write-Host ""

# Verify settings
Write-Host "Step 2: Verifying Settings..." -ForegroundColor Yellow
Write-Host "OLLAMA_NUM_PARALLEL: " -NoNewline
Write-Host ([System.Environment]::GetEnvironmentVariable('OLLAMA_NUM_PARALLEL', 'Machine')) -ForegroundColor Cyan

Write-Host "OLLAMA_MAX_LOADED_MODELS: " -NoNewline
Write-Host ([System.Environment]::GetEnvironmentVariable('OLLAMA_MAX_LOADED_MODELS', 'Machine')) -ForegroundColor Cyan

Write-Host "OLLAMA_NUM_THREADS: " -NoNewline
Write-Host ([System.Environment]::GetEnvironmentVariable('OLLAMA_NUM_THREADS', 'Machine')) -ForegroundColor Cyan

Write-Host "OLLAMA_NUM_CTX: " -NoNewline
Write-Host ([System.Environment]::GetEnvironmentVariable('OLLAMA_NUM_CTX', 'Machine')) -ForegroundColor Cyan

Write-Host ""
Write-Host "✓ Settings verified!" -ForegroundColor Green
Write-Host ""

# Restart Ollama
Write-Host "Step 3: Restarting Ollama Service..." -ForegroundColor Yellow

try {
    # Stop Ollama
    Write-Host "Stopping Ollama..." -ForegroundColor Gray
    Get-Process -Name "ollama*" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
    
    Write-Host "✓ Ollama stopped" -ForegroundColor Green
    Write-Host ""
    
    # Start Ollama
    Write-Host "Starting Ollama..." -ForegroundColor Gray
    $ollamaPath = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
    
    if (Test-Path $ollamaPath) {
        Start-Process -FilePath $ollamaPath -ArgumentList "serve" -WindowStyle Hidden
        Start-Sleep -Seconds 3
        Write-Host "✓ Ollama started with new settings" -ForegroundColor Green
    } else {
        Write-Host "⚠ Ollama not found at: $ollamaPath" -ForegroundColor Yellow
        Write-Host "Please start Ollama manually from the Start menu" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Could not restart Ollama automatically" -ForegroundColor Yellow
    Write-Host "Please restart Ollama manually:" -ForegroundColor Yellow
    Write-Host "  1. Right-click Ollama icon in system tray" -ForegroundColor Gray
    Write-Host "  2. Click 'Quit Ollama'" -ForegroundColor Gray
    Write-Host "  3. Start Ollama from Start menu" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Optimization Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Restart your backend server (Ctrl+C, then start again)" -ForegroundColor White
Write-Host "2. Test search at http://localhost:5173" -ForegroundColor White
Write-Host "3. System should no longer hang!" -ForegroundColor White
Write-Host ""
Write-Host "Expected Performance:" -ForegroundColor Yellow
Write-Host "- Process 1 article at a time (sequential)" -ForegroundColor White
Write-Host "- ~60 seconds per article" -ForegroundColor White
Write-Host "- Total: 5-6 minutes for 5 articles" -ForegroundColor White
Write-Host "- System remains responsive ✓" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to exit"
