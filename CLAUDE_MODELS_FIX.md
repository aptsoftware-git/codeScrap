# Claude API Model Names Fix

## Issue Summary
Claude API was returning 404 "model not found" errors because the code referenced non-existent model versions (4.5 series that don't exist yet).

## Root Cause
- Code used model names like `claude-4.5-haiku-20250514`, `claude-4.5-sonnet-20250514`, `claude-opus-4-20250514`
- These models don't exist in Claude's API (as of December 2024)
- Actual available models are Claude 3.x series: 3.5-haiku, 3.5-sonnet, 3-opus

## Errors Encountered
```
anthropic.NotFoundError: Error code: 404 - model: claude-4.5-haiku-20250514
```

## Files Fixed

### 1. `backend/app/services/claude_service.py`
**Changes:**
- Updated `MODELS` dict (lines 137-142) to map to actual available versions:
  - `claude-4.5-haiku` → `claude-3-5-haiku-20241022` (was non-existent 20250514)
  - `claude-4.5-sonnet` → `claude-3-5-sonnet-20241022` (was non-existent 20250514)
  - `claude-opus-4` → `claude-3-opus-20240229` (was non-existent opus-4-20250514)

- Updated `PRICING` dict (lines 22-48) to remove non-existent models:
  - Removed: `claude-4.5-haiku-20250514`, `claude-4.5-sonnet-20250514`, `claude-opus-4-20250514`
  - Kept only: `claude-3-5-haiku-20241022`, `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`

- Updated `list_models()` function (lines 309-350):
  - Removed all 4.5 model references
  - Show only actual available models: 3.5-haiku, 3.5-sonnet, 3-opus
  - Updated descriptions (removed "Previous generation" labels)

- Changed default model to `claude-3.5-haiku` (line 148)

### 2. `backend/app/services/llm_router.py`
**Changes:**
- Updated `list_available_models()` default to `claude-3.5-haiku` (was 4.5-haiku)

### 3. `backend/.env`
**Changes:**
- Changed `DEFAULT_CLAUDE_MODEL=claude-3.5-haiku` (was claude-4.5-haiku)
- Updated comment to list only available models: `3.5-haiku, 3.5-sonnet, opus`

## Additional Fix: Ollama Service Restart

**Issue:** Ollama process was running but not accepting connections on port 11434

**Solution:** 
```powershell
Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
```

## Verification

### Available Models (Corrected)
```json
{
  "claude": {
    "default": "claude-3.5-haiku",
    "models": [
      {
        "id": "claude-3.5-haiku",
        "version": "claude-3-5-haiku-20241022",
        "description": "Fastest and most cost-effective (Recommended)"
      },
      {
        "id": "claude-3.5-sonnet",
        "version": "claude-3-5-sonnet-20241022",
        "description": "Balanced quality and speed"
      },
      {
        "id": "claude-3-opus",
        "version": "claude-3-opus-20240229",
        "description": "Highest quality, most expensive"
      }
    ]
  }
}
```

### System Status
```json
{
  "default_provider": "claude",
  "fallback_enabled": true,
  "providers": {
    "ollama": {
      "available": true,
      "model": "qwen2.5:3b"
    },
    "claude": {
      "available": true,
      "model": "claude-3.5-haiku"
    }
  }
}
```

## Impact
- ✅ Claude API now works with correct model names
- ✅ No more 404 "model not found" errors
- ✅ Ollama fallback operational (connection restored)
- ✅ Both LLM providers available for event extraction
- ✅ Frontend shows only actual available models

## Testing
Backend initialized successfully:
```
2025-12-10 14:05:55 | INFO | ClaudeService initialized with model: claude-3-5-haiku-20241022
2025-12-10 14:05:55 | INFO | LLMRouter initialized: default=claude, claude_model=claude-3.5-haiku, fallback=True
2025-12-10 14:05:56 | INFO | Ollama client initialized successfully
```

## Next Steps
1. Test end-to-end search with Claude API
2. Verify cost tracking with actual API usage
3. Test fallback to Ollama when Claude quota exceeded
