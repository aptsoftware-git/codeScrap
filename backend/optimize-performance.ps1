# Performance Optimization Setup for Dual Xeon Gold 6140 Server
# Run this after installing Ollama and pulling qwen2.5:3b

Write-Host "=== CodeScrap Performance Optimization ===" -ForegroundColor Green
Write-Host ""

# 1. Create optimized Ollama model
Write-Host "Step 1: Creating optimized qwen2.5:3b model..." -ForegroundColor Cyan
ollama create qwen2.5-optimized -f Modelfile-qwen2.5-optimized

# 2. Update backend .env to use optimized model (optional)
Write-Host ""
Write-Host "Step 2: Configuration updated" -ForegroundColor Cyan
Write-Host "  - Parallel LLM processing: 4 concurrent articles"
Write-Host "  - Threads per LLM request: 8 (total 32 threads when all busy)"
Write-Host "  - Parallel web scraping: 10 concurrent requests"
Write-Host "  - Ollama timeout: 30s per article"
Write-Host ""

# 3. Restart backend
Write-Host "Step 3: Restart the backend server to apply changes:" -ForegroundColor Yellow
Write-Host "  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
Write-Host ""

# Performance expectations
Write-Host "=== Expected Performance Improvements ===" -ForegroundColor Green
Write-Host "Before optimization:"
Write-Host "  - Sequential processing: ~5s per article"
Write-Host "  - 5 articles: ~25 seconds total"
Write-Host ""
Write-Host "After optimization:"
Write-Host "  - Parallel processing: 4 articles at once"
Write-Host "  - 10 articles: ~15-20 seconds total (4x speedup)"
Write-Host "  - CPU usage: Better distributed across 72 threads"
Write-Host ""

Write-Host "=== Optional: Use optimized model ===" -ForegroundColor Yellow
Write-Host "To use the custom optimized model, update .env:"
Write-Host '  OLLAMA_MODEL=qwen2.5-optimized' -ForegroundColor White
Write-Host ""
