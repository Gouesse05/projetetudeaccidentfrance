# 🚀 Phase 4: API REST FastAPI - Guide Démarrage

## 📋 Vue d'ensemble

**Phase 4** fournit une **API REST complète** pour accéder aux données d'accidents et analyses.

**Features:**
- ✅ 15+ endpoints analytiques
- ✅ Swagger/ReDoc auto-généré
- ✅ Pydantic models (validation + docs)
- ✅ Connection pooling à PostgreSQL
- ✅ Error handling professionnel
- ✅ CORS enabled
- ✅ Tests complets (pytest)

---

## 🎯 Endpoints Disponibles

### Health & Monitoring

```bash
GET  /health              # État service + DB
GET  /status              # Status détaillé
GET  /report/quality      # Rapport qualité données
GET  /metadata            # Métadonnées projet
```

### Accidents (Queries Simples)

```bash
GET  /api/v1/accidents              # Liste avec filtres
GET  /api/v1/accidents/{id}         # Détail 1 accident
GET  /api/v1/accidents/commune/{code_com}  # Par commune
```

**Paramètres:**
- `annee`: Année (ex: 2022)
- `mois`: Mois 1-12
- `dept`: Code département (ex: 75)
- `gravite_min`: Gravité minimale (1-4)
- `limit`: Max résultats (1-10000)

**Exemples:**
```bash
curl "http://localhost:8000/api/v1/accidents?annee=2022&limit=10"
curl "http://localhost:8000/api/v1/accidents?dept=75&gravite_min=3"
curl "http://localhost:8000/api/v1/accidents/commune/75056?limit=100"
```

### Scores de Danger (Risk Assessment)

```bash
GET  /api/v1/danger-scores              # Top communes par score
GET  /api/v1/danger-scores/{code_com}   # Score 1 commune
```

**Score = (Fréquence × 50%) + (Gravité × 30%) + (Personnes × 20%)**

**Exemple:**
```bash
curl "http://localhost:8000/api/v1/danger-scores?limit=20"
```

### Statistiques (Analyses Agrégées)

```bash
GET  /api/v1/stats/temporelles   # Par jour/heure
GET  /api/v1/stats/communes      # Top communes
GET  /api/v1/stats/departements  # Top depts
GET  /api/v1/stats/usagers       # Par âge/sexe
GET  /api/v1/stats/vehicules     # Par catégorie véhicule
```

**Exemples:**
```bash
curl http://localhost:8000/api/v1/stats/communes?limit=50
curl http://localhost:8000/api/v1/stats/usagers?limit=100
curl http://localhost:8000/api/v1/stats/temporelles?annee=2022
```

### Géolocalisation (Heatmaps & Proximité)

```bash
GET  /api/v1/heatmap                # Données pour heatmap (lat/lon)
POST /api/v1/accidents/near         # Accidents proches
```

**Exemple heatmap:**
```bash
curl "http://localhost:8000/api/v1/heatmap?annee=2023&limit=5000"
```

**Exemple proximité:**
```bash
curl -X POST http://localhost:8000/api/v1/accidents/near \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 48.8566,
    "longitude": 2.3522,
    "distance_km": 5.0
  }'
```

### Analyses Custom

```bash
POST /api/v1/analyze    # Analyses personnalisées
```

**Types:** univariee, bivariee, temporelle, spatiale, clustering

---

## 🚀 Installation & Démarrage

### 1. Prérequis

```bash
✓ PostgreSQL lancé
✓ Données chargées (Phase 3)
✓ .env configuré
```

### 2. Installer dépendances

Les packages FastAPI sont déjà dans `requirements.txt`:

```bash
pip install fastapi uvicorn pydantic
# ou complet:
pip install -r requirements.txt
```

### 3. Vérifier configuration

Éditer `.env` si nécessaire:

```ini
DB_HOST=localhost
DB_PORT=5432
DB_NAME=accidents_db
DB_USER=postgres
DB_PASSWORD=postgres

API_HOST=localhost
API_PORT=8000
```

### 4. Lancer l'API

**Mode développement (avec rechargement auto):**
```bash
uvicorn src.api.main:app --reload
```

**Mode production:**
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

**Avec Gunicorn (production):**
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.api.main:app
```

### 5. Vérifier qu'ça marche

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Liste accidents
curl "http://localhost:8000/api/v1/accidents?limit=5"

# Danger scores
curl "http://localhost:8000/api/v1/danger-scores?limit=10"
```

---

## 📚 Documentation Interactive

Une fois lancé, accéder à:

### **Swagger UI** (Recommandé)
```
http://localhost:8000/docs
```

✨ Interface interactive pour:
- Voir tous les endpoints
- Tester directement dans le navigateur
- Voir les réponses en temps réel
- Télécharger schéma OpenAPI

### **ReDoc** (Lisible)
```
http://localhost:8000/redoc
```

Présentation alternative - meilleure pour la lecture

### **OpenAPI Schema** (JSON)
```
http://localhost:8000/openapi.json
```

Pour intégrations programmatiques

---

## 🧪 Tests

### Lancer tests API

```bash
pytest tests/test_api.py -v

# Ou avec couverture
pytest tests/test_api.py --cov=src.api --cov-report=html
```

### Résultats attendus

```
tests/test_api.py::test_health_check PASSED
tests/test_api.py::test_list_accidents_no_filters PASSED
tests/test_api.py::test_danger_scores PASSED
tests/test_api.py::test_stats_communes PASSED
tests/test_api.py::test_heatmap_data PASSED
tests/test_api.py::test_swagger_docs PASSED
...
```

---

## 💡 Exemples Pratiques

### 1. **Top 10 communes les plus dangereuses**

```bash
curl "http://localhost:8000/api/v1/danger-scores?limit=10" | jq
```

**Réponse:**
```json
[
  {
    "nom_com": "Paris",
    "score_danger": 85.5,
    "categorie_risque": "TRÈS_ÉLEVÉ",
    "nombre_accidents": 1200,
    "nombre_deces": 45
  },
  ...
]
```

### 2. **Accidents graves en Île-de-France (2022)**

```bash
curl "http://localhost:8000/api/v1/accidents?dept=75&annee=2022&gravite_min=3&limit=50" | jq
```

### 3. **Statistiques par âge**

```bash
curl "http://localhost:8000/api/v1/stats/usagers" | jq '.[] | select(.age == 25)'
```

### 4. **Heatmap: Accidents à Paris**

```bash
curl "http://localhost:8000/api/v1/heatmap?annee=2023" > heatmap.json
# Visualiser avec Folium/Leaflet
```

### 5. **Python - Client HTTP**

```python
import requests

api_url = "http://localhost:8000"

# Lister accidents
resp = requests.get(f"{api_url}/api/v1/accidents", params={
    "annee": 2022,
    "limit": 100
})
accidents = resp.json()

# Danger scores
resp = requests.get(f"{api_url}/api/v1/danger-scores", params={"limit": 20})
scores = resp.json()

# Accidents proches
resp = requests.post(f"{api_url}/api/v1/accidents/near", json={
    "latitude": 48.8566,
    "longitude": 2.3522,
    "distance_km": 5.0
})
nearby = resp.json()
```

---

## 🔧 Configuration Avancée

### CORS (Cross-Origin Requests)

Actuellement permissif (`*`). Pour production:

```python
# Dans src/api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Rate Limiting

À ajouter (Phase 5):

```bash
pip install slowapi
```

### Authentification JWT

À implémenter (Phase 5):

```python
from fastapi.security import HTTPBearer
```

---

## 📊 Structure Fichiers

```
src/api/
├── __init__.py        # Module metadata
├── main.py            # Application FastAPI + config
├── models.py          # Schémas Pydantic (validation + docs)
├── routes.py          # Tous les endpoints (1000+ lignes)
└── __pycache__/

tests/
└── test_api.py        # Tests avec TestClient (250+ lignes)
```

---

## ⚙️ Performance & Scalabilité

### Connection Pooling

Déjà implémenté dans DatabaseManager:

```python
self.pool = SimpleConnectionPool(1, 5, ...)  # 5 connexions
```

### Caching (Futur)

À ajouter pour danger_scores (cache 1h):

```python
from functools import lru_cache

@app.get("/danger-scores")
@cache(expire=3600)
async def list_danger_scores(...):
```

### Pagination (Futur)

Pour requêtes volumineuses:

```bash
GET /api/v1/accidents?page=1&page_size=100
```

---

## 🐛 Troubleshooting

### Erreur: "Connection refused"

```bash
# Vérifier PostgreSQL
psql -U postgres -c "SELECT 1"

# Vérifier config .env
cat .env | grep DB_
```

### Erreur: "ModuleNotFoundError"

```bash
# Vérifier imports
export PYTHONPATH=/home/sdd/projetetudeapi:$PYTHONPATH
uvicorn src.api.main:app --reload
```

### Lent?

```bash
# Chercher requête lente dans logs
# Ajouter indexes (Phase 3 - déjà fait)
# Vérifier limite results
```

---

## 📈 Métriques & Monitoring

À implémenter (Phase 5):

```bash
pip install prometheus-client
```

Endpoints:
- `GET /metrics` - Métriques Prometheus
- Requêtes/sec
- Latence p99
- Erreurs/min

---

## 🚀 Déploiement

### Docker (À créer)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Lancer:
```bash
docker build -t accidents-api .
docker run -p 8000:8000 accidents-api
```

### AWS Lambda (Serverless)

Avec Mangum:
```bash
pip install mangum
```

---

## ✅ Checklist Démarrage

- [ ] PostgreSQL lancé et données chargées
- [ ] `.env` configuré correctement
- [ ] `pip install -r requirements.txt`
- [ ] `uvicorn src.api.main:app --reload`
- [ ] http://localhost:8000/docs accessible
- [ ] `curl http://localhost:8000/api/v1/health` → OK
- [ ] Tests passent: `pytest tests/test_api.py -v`
- [ ] Requête test: `curl http://localhost:8000/api/v1/accidents?limit=5`

---

## 📞 Prochaines Étapes (Phase 5)

1. **SDK Python**: Client library pour consommer l'API
2. **Authentication**: JWT tokens
3. **Rate Limiting**: slowapi
4. **Caching**: Redis
5. **Monitoring**: Prometheus + Grafana
6. **Documentation**: Postman collection

---

**Phase 4 Complète! ✅**  
API Production-Ready prête pour consumption
