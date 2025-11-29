# Ollama Model Configuration Guide

## Quick Answer: Use Your Existing Model!

**Yes, you can use `gpt-oss:20b`!** In fact, it's probably better than the default recommendation.

---

## Model Comparison

### Your Model: `gpt-oss:20b`

**Pros:**
- ✅ **20 billion parameters** - Much larger than llama3.1:8b
- ✅ **Higher accuracy** - Better at understanding complex events
- ✅ **Better structured output** - More reliable JSON formatting
- ✅ **Already installed** - No download needed

**Cons:**
- ⚠️ **Slower** - Takes 2-3x longer per article than 8B models
- ⚠️ **More memory** - Requires ~12-16GB RAM
- ⚠️ **Better with GPU** - CPU inference will be slower

**Recommendation:** ⭐⭐⭐⭐⭐ **Best choice for accuracy**

---

### Alternative: `llama3.1:8b`

**Pros:**
- ✅ **Faster** - 2-3x quicker than 20B models
- ✅ **Lower resources** - Works with 4-6GB RAM
- ✅ **Good accuracy** - Sufficient for most use cases

**Cons:**
- ⚠️ **Less nuanced** - May miss subtle details
- ⚠️ **Needs download** - ~4.7GB download

**Recommendation:** ⭐⭐⭐ Good balance for production

---

### Lightweight: `phi3:mini`

**Pros:**
- ✅ **Very fast** - Best for high-volume processing
- ✅ **Minimal resources** - Only ~2-3GB RAM

**Cons:**
- ⚠️ **Lower accuracy** - May struggle with complex events
- ⚠️ **Less reliable** - More errors in structured output

**Recommendation:** ⭐⭐ Only for simple, high-volume use

---

## Performance Estimates

Based on typical news article (500-1000 words):

| Model | Processing Time | Accuracy | Memory |
|-------|----------------|----------|--------|
| `gpt-oss:20b` | ~15-20 seconds | 95% | 12-16GB |
| `llama3.1:8b` | ~5-8 seconds | 85% | 4-6GB |
| `phi3:mini` | ~2-3 seconds | 70% | 2-3GB |

*Times are estimates for CPU inference. GPU will be faster.*

---

## Configuration Steps

### 1. Check Your Installed Models

```bash
ollama list
```

You should see something like:
```
NAME             ID              SIZE      MODIFIED
gpt-oss:20b      abc123def       12 GB     2 weeks ago
```

### 2. Configure Your Application

Create/edit `.env` file in your project root:

```bash
# Use your existing model
OLLAMA_MODEL=gpt-oss:20b

# Or use a different one
# OLLAMA_MODEL=llama3.1:8b
# OLLAMA_MODEL=phi3:mini
```

### 3. Verify Configuration

```bash
# Start your backend
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload

# In another terminal, check the status
curl http://localhost:8000/api/v1/ollama/status
```

Should return:
```json
{
  "status": "connected",
  "model": "gpt-oss:20b",
  "base_url": "http://localhost:11434"
}
```

---

## When to Use Each Model

### Use `gpt-oss:20b` (Your Current Model) When:
- ✅ Accuracy is more important than speed
- ✅ Processing 10-100 articles at a time
- ✅ You have 16GB+ RAM
- ✅ Working with complex/ambiguous events
- ✅ Need reliable structured data extraction

**Perfect for:** Research, analysis, quality over speed

### Use `llama3.1:8b` When:
- ✅ Need faster processing
- ✅ Processing 100-500 articles
- ✅ Limited to 8GB RAM
- ✅ Events are relatively straightforward

**Perfect for:** Regular monitoring, production use

### Use `phi3:mini` When:
- ✅ Need maximum speed
- ✅ Processing 500+ articles
- ✅ Very limited resources (4GB RAM)
- ✅ Simple event types only

**Perfect for:** High-volume, simple categorization

---

## Switching Models

You can switch models anytime without code changes:

```bash
# Pull a new model
ollama pull llama3.1:8b

# Update .env file
OLLAMA_MODEL=llama3.1:8b

# Restart backend
# Changes take effect immediately
```

---

## GPU Acceleration (Optional)

If you have an NVIDIA GPU, Ollama will automatically use it:

**Check GPU usage:**
```bash
# Windows
nvidia-smi

# Should show ollama process using GPU
```

**GPU Benefits:**
- 3-5x faster inference
- Especially beneficial for large models (20B+)
- Makes `gpt-oss:20b` much more practical

---

## Recommended Configuration

**For this project (event scraping tool), use:**

```bash
# .env
OLLAMA_MODEL=gpt-oss:20b  # You already have it!
```

**Why?**
- Better event extraction accuracy
- More reliable perpetrator/location identification  
- Better handling of ambiguous text
- Quality matters more than speed for research use

---

## Troubleshooting

### Model too slow?
- Consider using GPU if available
- Try `llama3.1:8b` for faster processing
- Process fewer articles per batch

### Out of memory?
- Close other applications
- Use `llama3.1:8b` instead
- Add more RAM or use GPU

### Poor extraction quality?
- Use larger model (`gpt-oss:20b` or `llama3.1:70b`)
- Improve prompts (see PromptEngineering.md)
- Add more examples to prompts

---

## Summary

**Your Setup:**
- Model: `gpt-oss:20b` ✅ (already installed)
- Expected speed: ~15-20 sec/article
- Expected accuracy: ~95%
- Memory needed: 12-16GB

**Action:** Just set `OLLAMA_MODEL=gpt-oss:20b` in your `.env` file and you're good to go!

---

**Last Updated:** November 2025
