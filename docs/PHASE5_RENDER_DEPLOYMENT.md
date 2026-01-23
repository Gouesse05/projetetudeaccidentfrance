# 🚀 Phase 5: Déploiement sur Render - Guide Complet

**Date**: Janvier 2026  
**Objectif**: Déployer l'API FastAPI sur Render via GitHub  
**Plateforme**: Render.com (hosting gratuit + PostgreSQL)

---

## 📋 Vue d'ensemble

**Phase 5** déploiera l'API Phase 4 sur **Render**, une plateforme PaaS moderne qui:
- ✅ Déploie directement depuis GitHub
- ✅ Fournit PostgreSQL géré
- ✅ Supporte Python/FastAPI nativement
- ✅ Auto-scaling inclus
- ✅ HTTPS gratuit
- ✅ Custom domains
- ✅ Monitoring inclus

---

## 🎯 Objectifs Phase 5

### Objectifs Principaux
- [ ] Créer compte Render
- [ ] Configurer PostgreSQL sur Render
- [ ] Configurer variables d'environnement
- [ ] Déployer l'API depuis GitHub
- [ ] Vérifier fonctionnement production
- [ ] Configurer monitoring
- [ ] Documenter processus

### Livrables Attendus
- ✅ API en ligne sur `https://accidents-api-prod.onrender.com`
- ✅ PostgreSQL hébergée sur Render
- ✅ CI/CD depuis GitHub automatisé
- ✅ Monitoring et logs actifs
- ✅ Documentation déploiement
- ✅ Guide maintenance

---

## 🔧 Architecture Déploiement

```
┌─────────────────┐
│   GitHub Repo   │ (projetetudeaccidentfrance)
└────────┬────────┘
         │
         │ (Git Push)
         ▼
┌─────────────────┐
│   Render.com    │ (CI/CD + Hosting)
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────────┐
│ Web    │ │ PostgreSQL   │
│Service │ │ (Managed DB) │
└────┬───┘ └──────────────┘
     │
     ▼
https://accidents-api-prod.onrender.com

Client Requests
     ↓
Render Edge Network (auto-scaling)
     ↓
FastAPI Container (Python)
     ↓
PostgreSQL Database
```

---

## 📦 Prérequis

### Compte & Access
- [ ] Compte GitHub (déjà créé: Gouesse05)
- [ ] Repository GitHub (déjà créé: projetetudeaccidentfrance)
- [ ] Compte Render (à créer)
- [ ] Carte de crédit Render (optionnel - tier gratuit disponible)

### Code Local
- [ ] Phase 4 complètement commitée sur main
- [ ] `requirements.txt` à jour
- [ ] `.env.example` en place (sans secrets)
- [ ] `src/config.py` avec variables d'environnement
- [ ] Tests passants localement

### Vérification Pré-déploiement

```bash
cd /home/sdd/projetetudeapi

# 1. Vérifier tous les commits sont pushés
git status  # Doit dire "à jour avec 'origin/main'"

# 2. Vérifier requirements.txt
cat requirements.txt | grep -E "fastapi|uvicorn|pydantic|psycopg2"

# 3. Lancer tests localement
pytest tests/test_api.py -v  # 15/15 PASSING

# 4. Vérifier API démarre
uvicorn src.api.main:app --reload  # Accessible sur :8000
```

---

## 🎬 Étape 1: Créer Compte Render

### 1.1 Inscription
```
1. Aller sur https://render.com
2. Cliquer "Sign Up"
3. Sélectionner "Sign up with GitHub"
4. Autoriser l'accès aux repos GitHub
5. Compléter profil
```

### 1.2 Configuration de Base
```
Dashboard Render
  ├── Account Settings
  │   ├── GitHub Connection (vérifier)
  │   ├── Email & Notifications
  │   └── Billing (optionnel pour tier gratuit)
  └── Create New
      ├── Web Service
      └── PostgreSQL Database
```

---

## 📊 Étape 2: Créer PostgreSQL sur Render

### 2.1 Créer Database

**Naviguer à**: Dashboard → New+ → PostgreSQL

**Configuration**:
```
Name:               accidents-db-prod
Database:           accidents_db
User:              postgres
Password:          (auto-généré - noter)
Region:            Frankfurt (EU - gratuit)
Tier:              Free (0.07 credits/heure)
```

### 2.2 Récupérer Credentials

Après création, Render affichera:
```
Hostname:          accidents-db-prod.c99xyz.postgres.render.com
Database:          accidents_db
User:              postgres
Password:          ••••••••••••••
Internal Database URL: postgres://postgres:••••••••@localhost/accidents_db
External Database URL: postgres://postgres:••••••••@accidents-db-prod.c99xyz.postgres.render.com/accidents_db
```

**Action**: Copier l'URL externe - on l'utilisera dans la Web Service

### 2.3 Initialiser Base de Données

Deux options:

#### Option A: Restore depuis backup Phase 3
```bash
# Depuis machine locale avec accès à la backup Phase 3
pg_restore -h accidents-db-prod.c99xyz.postgres.render.com \
           -U postgres \
           -d accidents_db \
           /chemin/vers/backup_accidents_db.sql

# Ou si dump simple:
psql -h accidents-db-prod.c99xyz.postgres.render.com \
     -U postgres \
     -d accidents_db \
     < /chemin/vers/schema.sql
```

#### Option B: Charger depuis Python (Phase 3)
```python
# Créer script de migration
from src.database.load_postgresql import PostgreSQLLoader

loader = PostgreSQLLoader(
    host='accidents-db-prod.c99xyz.postgres.render.com',
    user='postgres',
    password='••••••••••••••',
    dbname='accidents_db'
)
loader.load_all_data()  # Charge les 480k+ rows
```

### 2.4 Vérifier Connexion

```bash
# Test connexion
psql -h accidents-db-prod.c99xyz.postgres.render.com \
     -U postgres \
     -d accidents_db \
     -c "SELECT COUNT(*) FROM accidents;"

# Doit retourner ~68k accidents
```

---

## 🌐 Étape 3: Créer Web Service sur Render

### 3.1 Connecter Repository

**Naviguer à**: Dashboard → New+ → Web Service

**Connecter GitHub**:
```
1. Sélectionner "GitHub"
2. Choisir "projetetudeaccidentfrance"
3. Cliquer "Connect"
```

### 3.2 Configurer Web Service

```
Name:                    accidents-api-prod
Environment:            Python 3
Build Command:          pip install -r requirements.txt
Start Command:          uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
Region:                 Frankfurt (EU)
Tier:                   Free
Auto-Deploy:            Yes (git push automatique)
```

### 3.3 Ajouter Variables d'Environnement

**Naviguer à**: Web Service → Environment

**Ajouter les variables**:

| Variable | Valeur | Source |
|----------|--------|--------|
| `DB_HOST` | `accidents-db-prod.c99xyz.postgres.render.com` | PostgreSQL settings |
| `DB_PORT` | `5432` | Standard PostgreSQL |
| `DB_NAME` | `accidents_db` | PostgreSQL config |
| `DB_USER` | `postgres` | PostgreSQL config |
| `DB_PASSWORD` | `••••••••••••••` | PostgreSQL password |
| `API_HOST` | `0.0.0.0` | Pour Render |
| `API_PORT` | (auto par Render) | Render injecte $PORT |
| `ENVIRONMENT` | `production` | Nouveau |

**Format Render**:
```
# Copier directement:
DB_HOST=accidents-db-prod.c99xyz.postgres.render.com
DB_PORT=5432
DB_NAME=accidents_db
DB_USER=postgres
DB_PASSWORD=your_secure_password_here
API_HOST=0.0.0.0
ENVIRONMENT=production
```

### 3.4 Déployer

```
1. Cliquer "Deploy"
2. Attendre ~3-5 minutes build
3. Vérifier logs en temps réel
```

**Logs attendus**:
```
Building...
Installing dependencies from requirements.txt
...
[INFO] Starting Accidents API v1.0.0
[INFO] Host: 0.0.0.0, Port: 10000
[INFO] Documentation: https://accidents-api-prod.onrender.com/docs
```

---

## ✅ Étape 4: Vérifier Déploiement

### 4.1 Tester Endpoints

```bash
# Remplacer par URL Render réelle
BASE_URL="https://accidents-api-prod.onrender.com"

# 1. Health check
curl "$BASE_URL/api/v1/health"

# 2. List accidents
curl "$BASE_URL/api/v1/accidents?limit=5"

# 3. Danger scores
curl "$BASE_URL/api/v1/danger-scores?limit=10"

# 4. Swagger docs
curl "$BASE_URL/docs"
```

### 4.2 Vérifier Swagger

```
Naviguer à: https://accidents-api-prod.onrender.com/docs

Vérifier:
  ✅ Tous les endpoints visibles
  ✅ Données chargées correctement
  ✅ Réponses JSON valides
  ✅ Pas d'erreurs 500
```

### 4.3 Logs Production

**Naviguer à**: Web Service → Logs

Vérifier:
- Pas d'erreurs de connexion DB
- Requêtes HTTP loggées
- Response times raisonnables
- Pas de memory leaks

---

## 🔄 Étape 5: Configurer Auto-Deploy

### 5.1 GitHub Actions (Optionnel)

Créer `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Render

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: pytest tests/test_api.py -v
    
    - name: Deploy to Render
      if: success()
      run: |
        curl https://api.render.com/deploy/srv-${{ secrets.RENDER_SERVICE_ID }}?key=${{ secrets.RENDER_DEPLOY_KEY }}
```

### 5.2 Configurer Secrets

**GitHub Settings** → Secrets → New Secret

```
RENDER_SERVICE_ID:  srv-••••••••••••••  (from Render URL)
RENDER_DEPLOY_KEY:  rnd_••••••••••••••  (from Render settings)
```

---

## 📊 Étape 6: Monitoring & Logs

### 6.1 Logs Render

**Naviguer à**: Web Service → Logs

```
Options:
  ├── Live tail (logs en temps réel)
  ├── Older logs (historique)
  └── Download logs (télécharger)
```

**Commandes utiles**:

```bash
# Voir logs API
curl "https://accidents-api-prod.onrender.com/api/v1/health" -v

# Voir erreurs
# Dans Render console: chercher ERROR

# Voir perf metrics
# Render Dashboard → Metrics
```

### 6.2 Alertes Email

**Render Settings** → Notifications

```
Configure:
  ├── Deployment notifications (on)
  ├── Error notifications (on)
  └── Email: your_email@example.com
```

### 6.3 Monitoring API

**Créer endpoint de monitoring**:

```python
# Dans src/api/routes.py
@app.get("/api/v1/metrics")
async def get_metrics():
    """Métriques d'exécution"""
    return {
        "uptime_seconds": time.time() - START_TIME,
        "requests_total": METRICS["total_requests"],
        "requests_per_minute": METRICS["requests_pm"],
        "avg_response_ms": METRICS["avg_response_ms"],
        "db_connections_active": METRICS["db_connections"]
    }
```

---

## 🌍 Étape 7: Custom Domain (Optionnel)

### 7.1 Ajouter Domain

**Web Service** → Settings → Custom Domain

```
Add custom domain:
  Domain: accidents-api.your-domain.com
  (ou utiliser domaine Render auto: accidents-api-prod.onrender.com)
```

### 7.2 DNS Configuration

Si domaine personnalisé:

```
Ajouter DNS record:
  Type:  CNAME
  Name:  accidents-api
  Value: accidents-api-prod.onrender.com
```

---

## 🔐 Sécurité Production

### Checklist Sécurité

- [ ] **Secrets**: Tous les passwords dans variables d'env Render
- [ ] **HTTPS**: Activé par défaut sur Render
- [ ] **CORS**: Restreindre origins (ne pas `["*"]`)
- [ ] **Rate Limiting**: À implémenter Phase 5b
- [ ] **Auth**: JWT à implémenter Phase 5b
- [ ] **Validation**: Déjà fait (Pydantic)
- [ ] **Logging**: Actif pour audit trail

### Configuration CORS Sécurisée

```python
# src/api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://accidents-api-prod.onrender.com",
        "https://your-frontend-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## 📈 Performance Optimization

### Render Tier Comparison

| Aspect | Free | Pro | Business |
|--------|------|-----|----------|
| Cost | $0 | ~$10/mo | ~$25+/mo |
| CPU | Shared | 0.5 | 1+ |
| Memory | 512MB | 2GB | 4GB+ |
| Uptime | 99.5% | 99.9% | 99.95% |
| DB Size | 100MB | 10GB | Unlimited |
| Auto-scaling | No | Yes | Yes |

**Recommandation Phase 5**: Commencer en Free, upgrader si nécessaire

### Optimisations

#### 1. Connection Pooling (déjà fait Phase 4)
```python
# src/database/database_utils.py
SimpleConnectionPool(minconn=1, maxconn=5)
```

#### 2. Database Query Optimization
```python
# Ajouter indexes si absent
CREATE INDEX idx_accidents_annee ON accidents(annee);
CREATE INDEX idx_accidents_commune ON accidents_communes(code_com);
```

#### 3. Caching (Phase 5b)
```python
# À faire: Redis pour danger_scores
from functools import lru_cache

@lru_cache(maxsize=100)
async def get_danger_scores(limit: int = 20):
    # Cache 1 heure
    pass
```

#### 4. Response Compression
```python
# src/api/main.py
from fastapi.middleware.gzip import GZIPMiddleware

app.add_middleware(GZIPMiddleware, minimum_size=1000)
```

---

## 🐛 Troubleshooting

### Problème 1: Build Échoue

**Symptôme**: Logs affichent erreur de build

**Solutions**:
```bash
# 1. Vérifier requirements.txt
pip install -r requirements.txt

# 2. Vérifier Python version
python --version  # Doit être 3.9+

# 3. Vérifier syntaxe
python -m py_compile src/api/main.py

# 4. Vérifier imports
python -c "from src.api.main import app"
```

### Problème 2: Connection DB Échoue

**Symptôme**: Logs: "connection failed for user postgres"

**Solutions**:
```bash
# 1. Vérifier variables d'env dans Render
# Web Service → Environment → vérifier chaque variable

# 2. Vérifier IP PostgreSQL accessible
ping accidents-db-prod.c99xyz.postgres.render.com

# 3. Tester psql local
psql -h [HOST] -U postgres -d accidents_db -c "SELECT 1"

# 4. Vérifier password exact (copier/coller)
```

### Problème 3: Timeout Requêtes

**Symptôme**: Requêtes lentes > 30s (Render timeout)

**Solutions**:
```python
# 1. Optimiser queries DB
EXPLAIN ANALYZE SELECT ... FROM accidents WHERE ...;

# 2. Ajouter limit par défaut
@app.get("/api/v1/accidents")
async def list_accidents(limit: int = Query(100, le=10000)):
    # Limiter à 10k même si client demande 100k
    pass

# 3. Implémenter caching
# Voir section Performance Optimization
```

### Problème 4: Memory Leak

**Symptôme**: Logs memory croissant, restart automatiques

**Solutions**:
```python
# 1. Fermer connections DB
async def close_db():
    db.close()  # Dans shutdown event

# 2. Vérifier pas de variables globales
# Éviter: global_list = []

# 3. Limiter cache size
@lru_cache(maxsize=100)  # Pas illimité
```

---

## 📝 Checklist Déploiement

### Avant Déploiement
- [ ] Phase 4 commits pushés sur main
- [ ] `requirements.txt` à jour
- [ ] Tests passants localement (15/15)
- [ ] Variables d'env dans `.env.example`
- [ ] `.gitignore` inclut `.env`
- [ ] README.md mis à jour

### Création Render
- [ ] Compte Render créé
- [ ] PostgreSQL créée
- [ ] Database initialisée (schema + data)
- [ ] Variables d'env configurées
- [ ] Web Service connectée à GitHub
- [ ] Build réussi (pas d'erreurs)

### Après Déploiement
- [ ] Health check OK
- [ ] Endpoints testés
- [ ] Swagger docs accessible
- [ ] Logs sans erreurs
- [ ] Performance acceptable
- [ ] Monitoring configuré
- [ ] Documentation mise à jour

---

## 🚀 Commandes de Référence

### Local Development
```bash
# Démarrer API
uvicorn src.api.main:app --reload

# Tests
pytest tests/test_api.py -v

# Check code
python -m py_compile src/api/main.py
```

### GitHub
```bash
# Push Phase 5
git add .
git commit -m "Phase 5: Render deployment configuration"
git push origin main
```

### Render CLI (Optionnel)
```bash
# Installer Render CLI
npm install -g @render-com/cli

# Deployer depuis CLI
render deploy --key $RENDER_DEPLOY_KEY
```

---

## 📚 Documentation URLs

### Après Déploiement
```
API Base:           https://accidents-api-prod.onrender.com
Swagger Docs:       https://accidents-api-prod.onrender.com/docs
ReDoc Docs:         https://accidents-api-prod.onrender.com/redoc
OpenAPI JSON:       https://accidents-api-prod.onrender.com/openapi.json
Health Check:       https://accidents-api-prod.onrender.com/api/v1/health
```

### Resources Externes
- [Render Docs](https://render.com/docs)
- [FastAPI on Render](https://render.com/docs/deploy-fastapi)
- [PostgreSQL on Render](https://render.com/docs/postgresql)
- [Render CLI Reference](https://render.com/docs/cli)

---

## 🎯 Prochaines Étapes (Phase 5b)

Après déploiement successful:

1. **SDK Python Client**
   - Client library pour consommer API
   - Caching local
   - Retry logic

2. **Authentication**
   - JWT tokens
   - API keys management
   - OAuth2 integration

3. **Rate Limiting**
   - slowapi middleware
   - Per-user limits
   - Public vs authenticated

4. **Monitoring Avancé**
   - Prometheus metrics
   - Grafana dashboards
   - Alert thresholds
   - SLA tracking

5. **Performance**
   - Redis caching
   - Elasticsearch search
   - Async database driver
   - Load testing

---

## 📋 Résumé

**Phase 5** déploie l'API sur Render:

### Livrables
- ✅ API production sur Render
- ✅ PostgreSQL géréé sur Render
- ✅ CI/CD depuis GitHub automatisé
- ✅ HTTPS activé
- ✅ Monitoring actif
- ✅ Documentation mise à jour

### URL Production
```
https://accidents-api-prod.onrender.com
```

### Prochaine Étape
**Phase 5b**: SDK Python + Authentication + Monitoring

---

**Status: PRÊT POUR DÉPLOIEMENT** ✅
