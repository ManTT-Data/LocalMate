# Running LocalMate Server

Quick commands để start/stop LocalMate server.

---

## 🚀 Start Server

```bash
# Bước 1: Kill process cũ (nếu đang chạy)
lsof -ti:8001 | xargs kill -9

# Bước 2: Activate venv & start server
cd localmate-danang-backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

**One-liner:**
```bash
lsof -ti:8001 | xargs kill -9 && cd localmate-danang-backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8001
```

---

## 🛑 Stop Server

```bash
# Kill process trên port 8001
lsof -ti:8001 | xargs kill -9
```

Hoặc `Ctrl+C` trong terminal đang chạy server.

---

## 📊 Check Server Status

```bash
# Check process đang chạy trên port 8001
lsof -i:8001

# Test health endpoint
curl http://localhost:8001/health

# Open Swagger UI
open http://localhost:8001/docs
```

---

## 🔧 Troubleshooting

### Issue: "Address already in use"
```bash
lsof -ti:8001 | xargs kill -9
```

### Issue: "No such file .venv"
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Issue: "ModuleNotFoundError"
```bash
source .venv/bin/activate
pip install -e ".[dev]"
```
