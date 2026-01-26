# 🛠️ SPÉCIFICATIONS TECHNIQUES

## Plateforme d'Analyse des Accidents Routiers

**Version**: 2.0  
**Date**: 26 Janvier 2026  
**Auteur**: Technical Lead  
**Audience**: Développeurs, DevOps, Architectes

---

## 1. ARCHITECTURE GÉNÉRALE

### 1.1 Architecture Système

```
┌─────────────────────────────────────────────────────────┐
│                    UTILISATEUR FINAL                     │
└────────────────────────┬────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐   ┌──────────┐   ┌───────────┐
    │Streamlit│   │  FastAPI │   │ Jupyter   │
    │Dashboard│   │   REST   │   │ Notebook  │
    │(Port 85)│   │(Port 80) │   │           │
    └────┬────┘   └─────┬────┘   └─────┬─────┘
         │              │              │
         └──────────────┼──────────────┘
                        │
         ┌──────────────┴──────────────┐
         │                             │
         ▼                             ▼
    ┌─────────────────┐      ┌──────────────────┐
    │  ETL Pipeline   │      │  Analysis Modules│
    │  (data_cleaning)│      │  (4 modules)     │
    └────────┬────────┘      └────────┬─────────┘
             │                        │
             └────────────┬───────────┘
                          │
                   ┌──────▼──────┐
                   │   Data      │
                   │  (Pandas)   │
                   └─────────────┘
```

### 1.2 Composants Principaux

| Composant | Technologie | Rôle |
|-----------|------------|------|
| **Frontend** | Streamlit | Interface utilisateur interactive |
| **API** | FastAPI + Uvicorn | Service web pour intégrations |
| **ETL** | Python 3.12 + Pandas | Pipeline chargement/nettoyage |
| **Analyses** | SciPy, Scikit-learn, Statsmodels | Calculs statistiques/ML |
| **Visualisation** | Plotly | Graphiques interactifs |
| **Testing** | Pytest + Pytest-cov | Tests unitaires |
| **VCS** | Git + GitHub | Versioning & collaboration |

---

## 2. STACK TECHNOLOGIQUE

### 2.1 Dépendances Principales

```
Python: 3.12
├── Data Processing
│   ├── pandas==1.5.3
│   ├── numpy==1.26.0
│   └── scipy==1.14.0
├── Visualization
│   ├── plotly==5.x
│   └── streamlit==1.x
├── Analytics
│   ├── scikit-learn==1.5.0
│   ├── statsmodels==0.14.0
│   └── prince==0.10.0 (MCA)
├── API
│   ├── fastapi==0.104.1
│   └── uvicorn==0.24.0
├── Testing
│   ├── pytest==7.4.3
│   └── pytest-cov==4.1.0
└── Code Quality
    ├── black==23.12.0
    └── flake8==6.1.0
```

### 2.2 Versions Minimales

- Python: **3.12.0**+
- Pandas: **1.5.0**+
- Streamlit: **1.20.0**+
- FastAPI: **0.104.0**+

### 2.3 Absence Intentionnelle

❌ **Airflow** - Orchestration complexe non nécessaire  
❌ **Dagster** - Alternative orchestration retirée  
❌ **TensorFlow** - Deep Learning non requis  
❌ **Spark** - Big Data non applicable  

---

## 3. STRUCTURE DES FICHIERS

```
/home/sdd/projetetudeapi/
├── streamlit_app.py                    # Application Streamlit (734 lignes)
├── api.py                              # API FastAPI (25+ endpoints)
├── run_pipeline.py                     # Orchestrateur pipeline (335 lignes)
│
├── src/
│   ├── analyses/
│   │   ├── __init__.py
│   │   ├── data_cleaning.py           # Nettoyage données (180 lignes)
│   │   ├── statistical_analysis.py    # Analyses stats (210 lignes)
│   │   ├── dimensionality_reduction.py# PCA/MCA/CA (314 lignes)
│   │   └── machine_learning.py        # ML models (310 lignes)
│   └── utils/
│       ├── __init__.py
│       └── helpers.py                 # Fonctions utilitaires
│
├── tests/
│   ├── __init__.py
│   ├── test_pipeline.py              # Tests e2e (163 lignes)
│   ├── test_data_cleaning.py
│   ├── test_statistical.py
│   └── test_ml.py
│
├── docs/
│   ├── 01_CAHIER_DE_CHARGES.md       # THIS FILE
│   ├── 02_SPECIFICATIONS_FONCTIONNELLES.md
│   ├── 03_SPECIFICATIONS_TECHNIQUES.md
│   ├── 04_BACKLOG.md
│   ├── 05_USER_STORIES.md
│   ├── 06_EPICS.md
│   ├── 07_ANOMALIES.md
│   └── ANALYSIS_REPORT.md
│
├── data/
│   └── accidents_sample.csv          # Données exemple
│
├── venv_clean/                        # Virtual environment
│   └── bin/
│       ├── activate
│       ├── python
│       ├── pip
│       ├── streamlit
│       └── uvicorn
│
├── .gitignore
├── requirements.txt                   # Dépendances (25 packages)
├── README.md                          # Documentation principale
├── PIPELINE_README.md                 # Guide pipeline
├── DASHBOARD_README.md                # Guide dashboard
├── LICENSE
└── .github/
    └── workflows/
        └── ci.yml                    # CI/CD pipeline (optionnel)
```

**Total Lines of Code**: ~2,500 (production) + ~800 (tests) = **3,300 lignes**

---

## 4. MODULES DÉTAILLÉS

### 4.1 Module: data_cleaning.py (180 lignes)

**Fonctions Clés**:

| Fonction | Input | Output | Logique |
|----------|-------|--------|---------|
| `load_accident_data()` | CSV path | DataFrame | Charge + validation basique |
| `clean_all_data()` | DataFrame | DataFrame clean | Normalise types, valeurs NULL |
| `get_data_quality_report()` | DataFrame | Dict stats | Profil qualité |
| `merge_datasets()` | List[DataFrame] | DataFrame | Join tables |

**Exemple Signature**:
```python
def clean_all_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie données accident.
    - Convertit types
    - Remplace valeurs invalides
    - Retire doublons
    """
    return df_clean
```

---

### 4.2 Module: statistical_analysis.py (210 lignes)

**Analyses Disponibles**:

| Analyse | Méthode | Use Case |
|---------|---------|----------|
| Descriptive | Mean, Median, Std | Résumé rapide |
| Correlation | Pearson/Spearman | Liens variables continues |
| Chi-Carré | χ² test | Liens variables catégories |
| Régression | OLS (statsmodels) | Prédiction linéaire |
| Logistique | sklearn | Prédiction binaire gravité |

**Exemple**:
```python
def correlation_analysis(df: pd.DataFrame, method='pearson') -> np.ndarray:
    """Matrice corrélation de toutes colonnes numériques"""
    return df.corr(method=method)
```

---

### 4.3 Module: dimensionality_reduction.py (314 lignes)

**Réductions de Dimension**:

| Technique | Entrée | Sortie | Application |
|-----------|--------|--------|-------------|
| **PCA** | Numériques | n composantes | Visualisation 2D/3D |
| **K-Means** | Numériques | Labels clusters | Segmentation conducteurs |
| **MCA** | Catégories | n axes | Analyse var. catégories |
| **CA** | Contingency | n axes | Analyse profils |
| **Elbow** | K range | Graphique | Choix K optimal |

---

### 4.4 Module: machine_learning.py (310 lignes)

**Modèles Implémentés**:

| Modèle | Task | Features | Métriques |
|--------|------|----------|-----------|
| Random Forest Classifier | Gravité (multi-class) | 15+ | Accuracy, F1, Confusion |
| Random Forest Regressor | Coût assurance | 15+ | RMSE, R², MAE |
| Feature Selection | Feature ranking | Auto | Gini importance |

---

## 5. API REST SPECIFICATION

### 5.1 Endpoints Principaux

**Base URL**: `http://localhost:8000/api`

#### Catégorie 1: Data Management

```
POST /load-data
  Body: {file: upload CSV}
  Response: {rows: int, columns: []}

GET /data/sample
  Query: ?limit=100&offset=0
  Response: [{...}, {...}]
```

#### Catégorie 2: Statistiques

```
GET /stats/descriptive
  Query: ?columns=age,gravite,vitesse
  Response: {
    age: {mean: 40.5, median: 38, ...},
    gravite: {...}
  }

GET /stats/correlation
  Response: [[1.0, 0.32, ...], [0.32, 1.0, ...]]

GET /stats/chi2
  Query: ?var1=classe_age&var2=gravite
  Response: {chi2: 45.23, p_value: 0.001}
```

#### Catégorie 3: Analyses

```
POST /analysis/clustering
  Body: {k: 5, method: 'kmeans', features: [...]}
  Response: {labels: [], centers: [], inertia: 1234}

GET /analysis/pca
  Query: ?n_components=2
  Response: {components: [], variance_explained: [0.45, 0.25]}
```

#### Catégorie 4: ML

```
POST /ml/predict-severity
  Body: {age: 35, experience: 10, alcool: false, ...}
  Response: {prediction: 2, probability: [0.2, 0.3, 0.35, 0.15]}

GET /ml/feature-importance
  Response: {age: 0.25, alcool: 0.22, ...}
```

### 5.2 Format des Réponses

**Success (200)**:
```json
{
  "status": "success",
  "data": {...},
  "timestamp": "2026-01-26T10:30:00Z"
}
```

**Error (400/500)**:
```json
{
  "status": "error",
  "error_code": "INVALID_INPUT",
  "message": "Age must be between 18 and 100",
  "timestamp": "2026-01-26T10:30:00Z"
}
```

### 5.3 Authentification

**Type**: Basic Auth (optionnel)  
**Headers**:
```
Authorization: Basic dXNlcjpwYXNzd29yZA==
```

---

## 6. BASE DE DONNÉES (Schéma Logique)

### 6.1 Table: accidents

```sql
CREATE TABLE accidents (
  id INT PRIMARY KEY,
  date DATETIME,
  heure INT CHECK (heure BETWEEN 0 AND 23),
  jour_semaine VARCHAR(10),
  
  -- Profil conducteur
  age INT CHECK (age BETWEEN 18 AND 100),
  classe_age VARCHAR(20),
  genre VARCHAR(10),
  annee_permis INT CHECK (annee_permis BETWEEN 1980 AND 2024),
  experience INT,
  
  -- Accident
  gravite INT CHECK (gravite BETWEEN 1 AND 4),
  nombre_victimes INT,
  nombre_vehicles INT,
  
  -- Conditions
  type_route VARCHAR(30),
  luminosite VARCHAR(20),
  conditions_meteo VARCHAR(20),
  
  -- Facteurs risque
  alcoolémie BOOLEAN,
  fatigue BOOLEAN,
  vitesse INT,
  
  -- Géographie
  departement VARCHAR(5),
  agglomeration VARCHAR(50),
  
  -- Coûts
  cout_assurance_annuel INT,
  
  INDEXES:
    - date (range queries)
    - age (demographic filters)
    - gravite (severity analysis)
    - alcoolémie (risk factor)
);
```

---

## 7. INTÉGRATION STREAMLIT

### 7.1 Architecture Streamlit

```python
# streamlit_app.py (734 lignes)
├── Configuration
│   └── st.set_page_config()
├── Data Generation
│   └── @st.cache_data generate_smart_accident_data()
├── Sidebar Filters (15+ critères)
├── Main Dashboard
│   ├── KPI Row (6 metrics)
│   ├── Tabs Container
│   │   ├── Tab 1: Tendances (4 charts)
│   │   ├── Tab 2: Démographie (4 charts)
│   │   ├── Tab 3: Assurance (4 charts + table)
│   │   ├── Tab 4: Causalité (6 charts + interpretations)
│   │   ├── Tab 5: Facteurs Risque (3 charts + table)
│   │   └── Tab 6: Insights (3 info boxes + profile)
```

### 7.2 Caching Strategy

```python
@st.cache_data  # Recalc 1x/jour par défaut
def generate_smart_accident_data():
    # 5000 records avec patterns réalistes
    return df

@st.cache_resource  # Recalc 1x/session
def get_model():
    # Charge modèles ML
    return model
```

**Impact Performance**: Dashboard charge <3s

---

## 8. GESTION ERREURS

### 8.1 Types Erreurs

| Type | Code HTTP | Exemple |
|------|-----------|---------|
| Input Invalid | 400 | Age < 18 |
| Not Found | 404 | Dataset inexistant |
| Server Error | 500 | Crash calcul |
| Timeout | 504 | Requête >30s |

### 8.2 Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Pipeline started")
logger.warning("Missing values in column X: 5 rows")
logger.error("Failed to load CSV", exc_info=True)
```

**Log Levels**: DEBUG < INFO < WARNING < ERROR < CRITICAL

---

## 9. TESTS

### 9.1 Stratégie Testing

```
Unit Tests (85% coverage)
├── test_data_cleaning.py (45 tests)
├── test_statistical_analysis.py (30 tests)
├── test_dimensionality_reduction.py (25 tests)
└── test_machine_learning.py (20 tests)

Integration Tests
├── test_pipeline.py (163 lignes)
└── test_api.py (API endpoints)

E2E Tests (Manual)
└── User journey testing
```

### 9.2 Exemple Test

```python
def test_chi2_analysis():
    """Test chi-square independence test"""
    df = pd.DataFrame({
        'age_group': ['18-25', '25-35', '35+'] * 10,
        'gravite': ['Léger', 'Grave'] * 15
    })
    
    result = chi2_test(df, 'age_group', 'gravite')
    
    assert result['chi2'] > 0
    assert 0 <= result['p_value'] <= 1
    assert 'significance' in result
```

**Coverage**: Actuellement **85%** (3,300 lignes code testées)

---

## 10. DÉPLOIEMENT

### 10.1 Environnement Local

```bash
# Setup
python3.12 -m venv venv_clean
source venv_clean/bin/activate
pip install -r requirements.txt

# Run
streamlit run streamlit_app.py              # Port 8503
python api.py                              # Port 8000
pytest tests/                              # Tests
```

### 10.2 Environnement Production (Optionnel)

```bash
# Service systemd
[Unit]
Description=Streamlit Accidents Dashboard
After=network.target

[Service]
Type=simple
User=sdd
WorkingDirectory=/home/sdd/projetetudeapi
ExecStart=/home/sdd/projetetudeapi/venv_clean/bin/streamlit run streamlit_app.py

[Install]
WantedBy=multi-user.target
```

### 10.3 Ports

| Service | Port | Status |
|---------|------|--------|
| Streamlit Dashboard | 8503 | ✅ Active |
| FastAPI | 8000 | ✅ Available |
| Jupyter | 8888 | ✅ Available |

---

## 11. SÉCURITÉ

### 11.1 Validations

```python
# Input validation
def validate_age(age):
    if not isinstance(age, int):
        raise ValueError("Age must be integer")
    if age < 18 or age > 100:
        raise ValueError("Age must be 18-100")
    return age
```

### 11.2 Gestion Données Sensibles

- ❌ Pas de données personnelles loggées
- ✓ Données anonymisées
- ✓ Pas d'export CSV raw (agrégations)

---

## 12. MONITORING & PERFORMANCE

### 12.1 Métriques

```python
import time

@app.get("/metrics")
def get_metrics():
    return {
        "uptime_seconds": time.time() - start_time,
        "active_users": len(active_sessions),
        "api_calls_total": api_call_counter,
        "avg_response_time_ms": avg_response_time
    }
```

### 12.2 Bottlenecks Connus

1. **Génération données** (5000 records): ~2s → Solution: Cache
2. **PCA sur 5000 rows**: ~0.5s → Acceptable
3. **Corrélation matrice**: ~0.1s → OK

---

## 13. ROADMAP TECHNIQUE FUTURE

**Phase 6 (Q2 2026)**:
- [ ] Connexion vraies données SNCDA/DGCN
- [ ] PostgreSQL + SQLAlchemy ORM
- [ ] Redis caching
- [ ] Docker containerization
- [ ] CI/CD GitHub Actions
- [ ] Monitoring Prometheus/Grafana

**Phase 7 (Q3 2026)**:
- [ ] Prédictions temps réel ML
- [ ] Alertes anomalies
- [ ] Export rapports PDF
- [ ] Mobile app React Native

---

**Approuvé par**: Technical Lead  
**Date**: 26/01/2026  
**Statut**: ✅ FINAL
