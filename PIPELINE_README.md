# 🚀 Pipeline d'Analyse des Accidents - Guide Rapide

**Status:** ✅ Prêt à utiliser | Sans orchestrateurs | Exécution manuelle simple

## Installation

```bash
# Créer un nouvel environnement virtuel propre
python3 -m venv venv_clean
source venv_clean/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## Usage

### 1️⃣ Lancer le Pipeline Complet

```bash
python run_pipeline.py
```

**Sortie:**
- Charge et nettoie les données
- Effectue l'analyse statistique
- Exécute l'analyse dimensionnelle (PCA, K-Means)
- Entraîne les modèles ML (Random Forest)
- Génère les rapports

**Fichiers générés:**
```
data/
├── models/
│   ├── pca_model.pkl
│   ├── kmeans_model.pkl
│   └── random_forest_model.pkl
└── reports/
    ├── data_quality_report.json
    ├── statistical_analysis.json
    ├── dimensionality_reduction.json
    ├── machine_learning.json
    └── pipeline_summary.json
```

### 2️⃣ Lancer une Étape Spécifique

```bash
# Nettoyage des données
python run_pipeline.py --step data_cleaning

# Analyse statistique
python run_pipeline.py --step statistical_analysis

# Analyse dimensionnelle
python run_pipeline.py --step dimensionality_reduction

# Apprentissage automatique
python run_pipeline.py --step machine_learning
```

### 3️⃣ Lancer l'API FastAPI

```bash
uvicorn src.api.main:app --reload --port 8000
```

**Endpoints disponibles:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/api/v1/analyses/health

**Exemples d'endpoints:**
```bash
# Charger des données
curl -X POST http://localhost:8000/api/v1/analyses/data-quality \
  -F "file=@data.csv"

# Analyse statistique
curl http://localhost:8000/api/v1/analyses/correlation-analysis

# PCA
curl http://localhost:8000/api/v1/analyses/pca-analysis
```

### 4️⃣ Lancer les Tests

```bash
# Tous les tests
pytest -v

# Tests d'un fichier spécifique
pytest tests/test_analyses.py -v

# Avec couverture
pytest --cov=src tests/ -v
```

## Structure du Projet

```
projetetudeapi/
├── src/
│   ├── analyses/
│   │   ├── data_cleaning.py          # ETL et nettoyage
│   │   ├── statistical_analysis.py   # Stats descriptives
│   │   ├── dimensionality_reduction.py # PCA, K-Means
│   │   └── machine_learning.py       # Random Forest
│   └── api/
│       ├── main.py                   # FastAPI app
│       └── analysis_endpoints.py     # Routes API
│
├── run_pipeline.py                   # Exécution manuelle du pipeline
├── requirements.txt                  # Dépendances Python
├── start.sh                          # Script de démarrage
└── data/
    ├── raw/                          # Données brutes (CSV)
    ├── models/                       # Modèles sauvegardés (.pkl)
    └── reports/                      # Rapports JSON
```

## Dépendances Principales

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.104.1 | REST API framework |
| pandas | 1.5.3 | Data manipulation |
| numpy | 1.26.0 | Numerical computing |
| scikit-learn | 1.5.0 | Machine Learning |
| scipy | 1.14.0 | Scientific computing |
| statsmodels | 0.14.0 | Statistical modeling |
| prince | 0.10.0 | MCA/CA analysis |
| matplotlib | 3.10.0 | Visualization |
| seaborn | 0.13.0 | Statistical plots |

## Logs et Debugging

Le script utilise `logging` pour un suivi détaillé:

```
[INFO] ✅ 5000 lignes chargées
[INFO] ✅ Silhouette score: 0.456
[ERROR] ❌ Erreur lors de l'analyse: ...
```

## Prochaines Étapes

1. **Tests automatisés**: Ajouter des tests unitaires (`pytest`)
2. **Monitoring**: Intégrer Prometheus/Grafana
3. **CI/CD**: Setup GitHub Actions
4. **Dashboard**: Créer une UI avec Streamlit/Dash
5. **H2O**: Ajouter les modèles GLM (H2O optionnel)

## Support

- 📚 Documentation complète: `docs/ANALYSIS_ENDPOINTS.md`
- 🐛 Issues: Vérifier les logs dans `data/reports/`
- 💬 Questions: Consulter `PHASE5_COMPLETE.md`

---

**Dernière mise à jour:** 2026-01-23  
**Statut:** Production-ready (sans orchestrateurs)
