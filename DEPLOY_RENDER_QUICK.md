# 🚀 Quick Deploy Guide - Render

**5-minute deployment checklist**

## ✅ Pre-Deploy Checklist

```bash
# 1. Vérifier Phase 4 est complète
git log --oneline | head -5
# Doit montrer "Phase 4" commits

# 2. Vérifier code compiles
python -m py_compile src/api/main.py
# Pas d'erreur = bon

# 3. Vérifier tests passent
pytest tests/test_api.py -v
# 15/15 PASSING = bon

# 4. Push sur GitHub
git status
# Doit être clean
git push origin main
```

## 🎬 Step-by-Step Deployment

### 1. Create Render Account (2 min)
```
1. Go to https://render.com
2. Sign up with GitHub
3. Authorize GitHub access
```

### 2. Create PostgreSQL (2 min)
```
Dashboard → New+ → PostgreSQL

Name:     accidents-db-prod
Region:   Frankfurt
Tier:     Free

Save credentials:
  - Hostname: accidents-db-prod.c99xyz.postgres.render.com
  - Password: ••••••••••••
```

### 3. Create Web Service (2 min)
```
Dashboard → New+ → Web Service

1. Select GitHub repo: projetetudeaccidentfrance
2. Configure:
   Name:        accidents-api-prod
   Region:      Frankfurt
   Environment: Python
   Build Cmd:   pip install -r requirements.txt
   Start Cmd:   uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
3. Deploy

Wait 3-5 min for build...
```

### 4. Add Environment Variables (1 min)
```
Web Service → Environment → Add Variable

DB_HOST=accidents-db-prod.c99xyz.postgres.render.com
DB_PORT=5432
DB_NAME=accidents_db
DB_USER=postgres
DB_PASSWORD=[from PostgreSQL]
API_HOST=0.0.0.0
ENVIRONMENT=production
```

### 5. Load Database (2 min)
```bash
# Option A: Using Python loader
python scripts/migrate_to_render.py \
  --action load \
  --render-db accidents-db-prod.c99xyz.postgres.render.com \
  --db-password [PASSWORD]

# Option B: Using psql
psql -h accidents-db-prod.c99xyz.postgres.render.com \
     -U postgres \
     -d accidents_db \
     -f data/schema.sql
```

## ✅ Verify Deployment

```bash
# Health check
curl https://accidents-api-prod.onrender.com/api/v1/health

# Test endpoint
curl "https://accidents-api-prod.onrender.com/api/v1/accidents?limit=5"

# Access Swagger
https://accidents-api-prod.onrender.com/docs
```

## 🎯 URLs

```
API:      https://accidents-api-prod.onrender.com
Swagger:  https://accidents-api-prod.onrender.com/docs
ReDoc:    https://accidents-api-prod.onrender.com/redoc
Health:   https://accidents-api-prod.onrender.com/api/v1/health
```

## 🔍 Monitoring

```
Render Dashboard:
  ├── Logs (live tail)
  ├── Metrics (CPU, memory)
  └── Deployments (history)

Monitor for:
  ✅ No errors in logs
  ✅ All endpoints responding
  ✅ Database connected
  ✅ Response times < 1s
```

## 📝 Troubleshooting

### Build Fails
```bash
# Check locally first
pip install -r requirements.txt
python -m py_compile src/api/main.py
```

### Can't Connect to DB
```bash
# Verify credentials in Render environment
# Check database is accessible:
psql -h [HOST] -U postgres -d accidents_db -c "SELECT 1"
```

### Slow Requests
```bash
# Check database indices
# Optimize queries
# Upgrade Render tier if needed
```

---

**Done!** Your API is live on Render 🎉

See `PHASE5_RENDER_DEPLOYMENT.md` for detailed guide
