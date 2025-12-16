# LocalMate HF Deployment Guide

## ✅ Files Created
- `Dockerfile` - Multi-stage build with SigLIP pre-cached
- `.dockerignore` - Excludes .venv, tests, docs
- `README.md` - Updated with HF Spaces header

## 🚀 Deployment Checklist

### Step 1: Create HF Space
1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. **Name:** `LocalMate-API`
3. **SDK:** Select **Docker**
4. **Visibility:** Public or Private

### Step 2: Configure Secrets
Go to **Space Settings > Repository secrets** and add:

| Secret | Description |
|--------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host:5432/db` |
| `NEO4J_URI` | `neo4j+s://xxx.databases.neo4j.io` |
| `NEO4J_USER` | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password |
| `MEGALLM_API_KEY` | MegaLLM API key |
| `GOOGLE_API_KEY` | Gemini API key |

### Step 3: Push Code
```bash
# Add HF Space as remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/LocalMate-API

# Push to HF
git push hf main
```

### Step 4: Verify
- Wait for build (5-10 min for first build with torch)
- Check: `https://YOUR_USERNAME-localmate-api.hf.space/docs`
- Test `/api/v1/chat` endpoint

## ⚠️ Notes
- First build takes ~10 min (downloading torch + SigLIP)
- Cold start ~30s after space sleeps
- SigLIP model is pre-cached in Docker image
