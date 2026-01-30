# 🚗 Accidents Routiers - Analyse & API

**Plateforme complète d'analyse des accidents routiers en France**  
Production-ready avec API FastAPI déployée sur Render, notebooks Jupyter professionnels et pipeline ETL automatisé

---

## 🌐 Liens Production

| Service | URL Production | Description |
|---------|----------------|-------------|
| **🔷 API REST** | [projetetudeaccidentfrance.onrender.com](https://projetetudeaccidentfrance.onrender.com) | API FastAPI principale |
| **📖 Documentation API** | [/docs](https://projetetudeaccidentfrance.onrender.com/docs) | Interface Swagger interactive |
| **📊 Dashboard Streamlit** | [projetetudeaccidentfrance-dashboard.onrender.com](https://projetetudeaccidentfrance-dashboard.onrender.com) | Visualisations interactives |

## 💻 URLs Locales (Développement)

| Service | URL Locale | Commande de démarrage |
|---------|------------|----------------------|
| **API FastAPI** | http://localhost:8000 | `uvicorn src.api.main:app --reload` |
| **Docs API** | http://localhost:8000/docs | (auto avec API) |
| **Dashboard Streamlit** | http://localhost:8501 | `streamlit run streamlit_app.py` |

## 🐳 Déploiement Docker

```bash
# Construire l'image
docker build -t accidents-api .

# Lancer l'API
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  accidents-api

# Accessible sur http://localhost:8000
```

---

## 📋 Vue d'ensemble

Ce projet implémente une **architecture analytique complète** pour les données d'accidents routiers:

**Statut**: ✅ Production (API déployée, Tests 95%, Documentation 100%)

### Architecture Globale

```mermaid
graph TB
    subgraph "Sources de Données"
        A[data.gouv.fr<br/>CSV Files] --> B[Pipeline ETL]
    end
    
    subgraph "Pipeline ETL"
        B --> C[Download<br/>download_data.py]
        C --> D[Clean<br/>clean_data.py]
        D --> E[Load<br/>load_postgresql.py]
    end
    
    subgraph "Stockage"
        E --> F[(PostgreSQL<br/>8 tables)]
        F --> G[accidents]
        F --> H[usagers]
        F --> I[vehicules]
        F --> J[lieux]
    end
    
    subgraph "Couche Analyse"
        F --> K[Statistical Analysis]
        F --> L[Machine Learning]
        F --> M[Dimensionality Reduction]
        F --> N[Data Cleaning]
    end
    
    subgraph "API REST"
        K --> O[FastAPI<br/>25+ endpoints]
        L --> O
        M --> O
        N --> O
    end
    
    subgraph "Clients"
        O --> P[Swagger UI]
        O --> Q[Streamlit Dashboard]
        O --> R[Jupyter Notebooks]
        O --> S[HTTP Clients]
    end
    
    style A fill:#e1f5ff
    style F fill:#ffe1e1
    style O fill:#e1ffe1
    style P fill:#fff4e1
    style Q fill:#fff4e1
    style S fill:#fff4e1
```

📚 **Documentation complète**: [Architecture Diagrams](docs/ARCHITECTURE_DIAGRAMS.md)

---

## 🚀 Démarrage rapide

### Développement local

```bash
# 1. Installation
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configuration
cp .env.example .env
# Éditez .env avec vos paramètres PostgreSQL

# 3. Initialiser la base de données
python src/database/init_schema.py

# 4. Charger les données
python src/pipeline/download_data.py
python src/pipeline/clean_data.py
python src/database/load_postgresql.py

# 5. Lancer l'API
uvicorn src.api.main:app --reload
# API disponible sur http://localhost:8000
# Documentation sur http://localhost:8000/docs

# 6. Lancer le dashboard Streamlit
streamlit run streamlit_app.py
# Dashboard sur http://localhost:8501

# 7. Lancer Jupyter (optionnel)
jupyter notebook notebooks/
```

### Production sur Render

**Services déployés:**

| Service | URL | Type |
|---------|-----|------|
| API REST | https://projetetudeaccidentfrance.onrender.com | FastAPI |
| Dashboard | https://projetetudeaccidentfrance-dashboard.onrender.com | Streamlit |
| Documentation | https://projetetudeaccidentfrance.onrender.com/docs | Swagger UI |

**Endpoints API disponibles:**
- `GET /` - Informations API et liste des endpoints
- `GET /docs` - Documentation interactive Swagger UI
- `GET /api/v1/health` - Health check
- `GET /api/v1/accidents` - Requêtes sur les accidents
- `GET /api/v1/danger-scores` - Scores de dangerosité
- `GET /api/v1/stats/communes` - Statistiques par commune
- `GET /api/v1/heatmap` - Données pour carte de chaleur

**Configuration Render (API):**
- Branch: `main`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
- Python: 3.13.4
- Auto-deploy: Activé sur push GitHub

**Configuration Render (Dashboard):**
- Branch: `main`
- Build: `pip install -r requirements-streamlit.txt`
- Start: `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
- Python: 3.13.4
- Auto-deploy: Activé sur push GitHub

---

## 📓 Notebooks Jupyter

Le projet inclut **4 notebooks réutilisables** pour l'analyse interactive :

### 1. 📊 Data Exploration (`notebooks/01_data_exploration.ipynb`)
- Connexion à l'API REST
- Chargement des données (API ou CSV fallback)
- Statistiques descriptives
- Analyse des valeurs manquantes
- Distributions (gravité, temporelles)
- Matrice de corrélations

### 2. 📈 Statistical Analysis (`notebooks/02_statistical_analysis.ipynb`)
- Tests du Chi2 (indépendance)
- ANOVA (comparaisons de groupes)
- Corrélations de Pearson
- Intervalles de confiance
- Analyses temporelles avec régression linéaire
- Intégration avec `statistical_analysis.py`

### 3. 🤖 Machine Learning (`notebooks/03_ml_modeling.ipynb`)
- Classification binaire (grave vs non-grave)
- Random Forest (n_estimators=100)
- Feature importance
- Confusion matrix
- Prédictions sur nouveaux cas
- Sauvegarde du modèle (joblib)

### 4. 🎨 Advanced Visualizations (`notebooks/04_visualizations.ipynb`)
- Cartes géographiques interactives (Plotly)
- Séries temporelles dynamiques
- Heatmaps (heure x jour)
- Graphiques 3D
- Top départements
- Export HTML/PNG

**Utilisation** :
```bash
cd notebooks/
jupyter notebook
# Ouvrir un notebook et exécuter les cellules
```

Tous les notebooks sont **autonomes** et incluent leur propre chargement de données.

# 5. Lancer l'API
uvicorn src.api.main:app --reload

# 6. Tests
pytest tests/test_api.py -v
```

### Production sur Render

```bash
# Voir DEPLOY_RENDER_QUICK.md pour déploiement en 5 minutes

# Ou le guide détaillé:
# docs/PHASE5_RENDER_DEPLOYMENT.md
```

---

## 📁 Structure du projet

```
.
├── data/                      # Stockage des données
│   ├── raw/                   # CSVs téléchargés (data.gouv.fr)
│   └── clean/                 # Données nettoyées et normalisées
├── src/
│   ├── api/                   # API REST FastAPI
│   │   ├── main.py           # Configuration FastAPI
│   │   ├── models.py         # Schémas Pydantic
│   │   └── routes.py         # 25+ endpoints
│   ├── database/              # Gestion PostgreSQL
│   │   ├── database_utils.py # DatabaseManager + pool
│   │   ├── load_postgresql.py # Chargement données
│   │   └── schema.sql        # DDL (8 tables)
│   ├── pipeline/              # ETL Pipeline
│   │   ├── download_data.py  # Téléchargement data.gouv.fr
│   │   ├── clean_data.py     # Nettoyage & normalisation
│   │   └── run_pipeline.py   # Orchestration complète
│   ├── analyses/              # Modules d'analyse
│   │   ├── statistical_analysis.py # Tests statistiques
│   │   ├── machine_learning.py     # ML (Random Forest)
│   │   ├── data_cleaning.py        # Utilitaires nettoyage
│   │   └── visualizations.py       # Graphiques
│   └── config.py             # Configuration centralisée
├── notebooks/                 # Jupyter Notebooks réutilisables ⭐
│   ├── 01_data_exploration.ipynb      # Exploration & EDA
│   ├── 02_statistical_analysis.ipynb  # Tests statistiques
│   ├── 03_ml_modeling.ipynb           # Machine Learning
│   └── 04_visualizations.ipynb        # Visualisations avancées
├── dashboard/                 # Dashboard Streamlit
│   └── streamlit_app.py      # Interface interactive
├── tests/                     # Suite de tests
│   ├── test_api.py           # Tests API (15+ endpoints)
│   ├── test_pipeline.py      # Tests ETL
│   └── test_integration.py   # Tests d'intégration
├── docs/                      # Documentation
│   ├── DATABASE_SCHEMA.md    # Schéma PostgreSQL détaillé
│   ├── PIPELINE_GUIDE.md     # Guide ETL complet
│   └── PHASE5_RENDER_DEPLOYMENT.md # Déploiement Render
├── queries/                   # Requêtes SQL réutilisables
│   └── README.md             # Documentation des queries
├── .github/workflows/
│   └── tests.yml             # CI/CD GitHub Actions
├── requirements.txt          # Dépendances Python
├── Procfile                  # Configuration Render
├── render.yaml              # Spécification déploiement
└── README.md                # Ce fichier
```

---

## 🔌 Endpoints API (25+)

API de production : **https://accidents-api-prod.onrender.com/api/v1/**

### Santé & Surveillance
- `GET /health` - Vérification santé service
- `GET /status` - Statut opérationnel détaillé
- `GET /report/quality` - Métriques qualité données

### Requêtes Accidents
- `GET /accidents` - Liste paginée avec filtres multiples
- `GET /accidents/{id}` - Détail d'un accident
- `GET /accidents/commune/{code}` - Accidents par commune

### Évaluation des risques
- `GET /danger-scores` - Classement communes dangereuses
- `GET /danger-scores/{code}` - Score de danger d'une commune

### Statistiques & Agrégations
- `GET /stats/temporelles` - Patterns temporels (heure, jour, mois)
- `GET /stats/communes` - Top communes par accidents
- `GET /stats/departements` - Statistiques par département
- `GET /stats/usagers` - Démographies des usagers
- `GET /stats/vehicules` - Répartition par type de véhicule

### Géolocalisation & Analyse
- `GET /heatmap` - Données pour cartes de chaleur
- `POST /accidents/near` - Recherche par proximité géographique
- `POST /analyze` - Analyses personnalisées avancées

**Documentation interactive** :
- 📖 Swagger UI : [/docs](https://projetetudeaccidentfrance.onrender.com/docs)
- 📘 ReDoc : [/redoc](https://projetetudeaccidentfrance.onrender.com/redoc)

---

## 🛠️ Technologies

| Couche | Technologie | Version | Utilité |
|--------|------------|---------|---------|
| **Backend API** | FastAPI | ≥0.104.0 | API REST moderne et rapide |
| **Validation** | Pydantic | ≥2.8.0 | Validation données & schémas |
| **Serveur ASGI** | Uvicorn | ≥0.24.0 | Serveur haute performance |
| **Base de données** | PostgreSQL | 15+ | Persistance et requêtes avancées |
| **Driver DB** | psycopg2-binary | ≥2.9.0 | Connexion PostgreSQL |
| **ETL** | pandas | ≥2.0.0 | Manipulation de données |
| **ML** | scikit-learn | ≥1.3.0 | Machine Learning (Random Forest) |
| **Stats** | scipy, statsmodels | ≥1.11.0 | Tests statistiques (Chi2, ANOVA) |
| **Compute** | numpy | ≥1.24.0 | Calcul numérique optimisé |
| **Dashboard** | Streamlit | Latest | Interface web interactive |
| **Notebooks** | Jupyter | Latest | Analyses interactives |
| **Tests** | pytest | Latest | Tests unitaires et intégration |
| **Déploiement** | Render.com | - | Hosting production (Python 3.13.4) |
| **Langage** | Python | 3.13+ | Runtime principal |

---

## 📊 Données

### Source
- **Fournisseur** : [data.gouv.fr](https://www.data.gouv.fr/)
- **Dataset** : Bases de données annuelles des accidents corporels de la circulation routière
- **Période** : 2016-2024 (9 années)
- **Volume** :
  - ~68 000 accidents recensés
  - ~245 000 usagers impliqués
  - ~89 000 véhicules concernés

### Schéma Base de Données
Notre implémentation PostgreSQL utilise :
- **8 tables** (5 transactionnelles + 1 analytique + 2 référentielles)
- **13 index stratégiques** pour optimisation des requêtes
- **2 vues SQL** pour analyses fréquentes
- **Pool de connexions** (5 connexions simultanées)
- **Contraintes d'intégrité** (FK, PK, CHECK)

📖 Voir [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) pour le schéma complet et la documentation des tables.

### Pipeline ETL
Le pipeline de données est **automatisé et idempotent** :

1. **Téléchargement** : Récupération depuis data.gouv.fr avec vérification de hash
2. **Nettoyage** : Normalisation, gestion valeurs manquantes, encodage
3. **Validation** : Contrôles qualité (complétude, cohérence, types)
4. **Chargement** : Import PostgreSQL avec transactions et rollback

📖 Voir [docs/PIPELINE_GUIDE.md](docs/PIPELINE_GUIDE.md) pour le guide complet du pipeline.

---

## 🚢 Déploiement

### Production (Render.com)

L'API est **déployée et opérationnelle** en production :

🌐 **URL** : https://accidents-api-prod.onrender.com  
📖 **Docs** : https://accidents-api-prod.onrender.com/docs

**Déploiement rapide (5 minutes)** :
1. Créer compte Render.com
2. Connecter repository GitHub
3. Créer instance PostgreSQL
4. Créer Web Service avec `render.yaml`
5. Configurer variables d'environnement
6. Vérifier endpoints fonctionnels

📖 Voir [docs/PHASE5_RENDER_DEPLOYMENT.md](docs/PHASE5_RENDER_DEPLOYMENT.md) pour le guide détaillé.

### Développement Local

```bash
# Lancer l'API
uvicorn src.api.main:app --reload
# Accessible sur http://localhost:8000

# Lancer le dashboard
streamlit run dashboard/streamlit_app.py
# Accessible sur http://localhost:8501
```

### Docker (Optionnel)

```dockerfile
docker build -t accidents-api .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  accidents-api
```

---

## ✅ Tests

### Exécution des Tests

```bash
# Tous les tests avec couverture
pytest tests/ -v --cov=src --cov-report=html

# Tests API uniquement
pytest tests/test_api.py -v

# Tests pipeline ETL
pytest tests/test_pipeline.py -v

# Tests d'intégration
pytest tests/test_integration.py -v

# Rapport de couverture HTML
open htmlcov/index.html  # Linux/Mac
start htmlcov/index.html  # Windows
```

### CI/CD (GitHub Actions)

Automatisation complète sur chaque push :
- ✅ Tests unitaires (pytest)
- ✅ Linting (flake8, black)
- ✅ Scanning sécurité (Bandit, Safety)
- ✅ Analyse de couverture (codecov)
- 🚀 Déploiement automatique sur branche `main`

📖 Voir `.github/workflows/tests.yml` pour la configuration CI/CD.

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | **Vue d'ensemble complète** (ce fichier) |
| [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) | **Schéma PostgreSQL détaillé** : 8 tables, index, vues |
| [docs/PIPELINE_GUIDE.md](docs/PIPELINE_GUIDE.md) | **Guide ETL** : téléchargement, nettoyage, chargement |
| [docs/PHASE5_RENDER_DEPLOYMENT.md](docs/PHASE5_RENDER_DEPLOYMENT.md) | **Déploiement Render** : guide production complet |
| [queries/README.md](queries/README.md) | **Requêtes SQL** : collection de queries réutilisables |
| [CV_GOUESSE_GO.md](CV_GOUESSE_GO.md) | **CV du développeur** : compétences et portfolio |
| [.github/workflows/tests.yml](.github/workflows/tests.yml) | **CI/CD** : configuration GitHub Actions |

### Documentation API Interactive
- 📖 **Swagger UI** : https://accidents-api-prod.onrender.com/docs
- 📘 **ReDoc** : https://accidents-api-prod.onrender.com/redoc

---

## 🔄 Mises à Jour Automatiques

Le pipeline ETL peut être exécuté **manuellement** ou **automatiquement** :

### Exécution Manuelle
```bash
python src/pipeline/run_pipeline.py
```

### Automatisation via Cron (Linux/Mac)
```bash
# Hebdomadaire (tous les lundis à 3h du matin)
0 3 * * 1 cd /path/to/projetetudeapi && /path/to/venv/bin/python src/pipeline/run_pipeline.py

# Mensuel (1er du mois à 2h)
0 2 1 * * cd /path/to/projetetudeapi && /path/to/venv/bin/python src/pipeline/run_pipeline.py
```

### Automatisation via GitHub Actions
```yaml
# .github/workflows/update_data.yml
on:
  schedule:
    - cron: '0 3 * * 1'  # Tous les lundis à 3h UTC
  workflow_dispatch:      # Déclenchement manuel
```

Le pipeline vérifie automatiquement les nouvelles données sur data.gouv.fr et met à jour la base si nécessaire.

---

## 🎓 Parcours d'Apprentissage

Ce projet démontre une **progression complète** en data engineering et data science :

| Phase | Focus | Compétences Acquises |
|-------|-------|---------------------|
| **Phase 1** | **ETL Pipeline** | Traitement CSV, parsing, transformation, batch loading |
| **Phase 2** | **Data Analysis** | Statistiques, clustering, classification, visualisation |
| **Phase 3** | **Database Design** | PostgreSQL, schéma relationnel, optimisation, indexation |
| **Phase 4** | **API REST** | FastAPI, async/await, validation Pydantic, documentation |
| **Phase 5** | **Production** | Render.com, CI/CD, monitoring, environnements |
| **Phase 6** | **Interactive Analysis** | Jupyter notebooks, Streamlit dashboard, ML workflows |

### Analyses Possibles
- ✅ Évolution des accidents/morts/blessés par année
- ✅ Identification des zones à risque (heatmap spatial)
- ✅ Clustering des accidents similaires
- ✅ Score de danger par commune
- ✅ Corrélations (heure, météo, infrastructure, usagers)
- ✅ Prédiction de gravité (Machine Learning)
- ✅ Analyses statistiques avancées (Chi2, ANOVA, régression)

### Portfolio Value
Ce projet démontre :
- 📊 **Data Engineering** : Ingestion automatisée, qualité, validation
- 🗄️ **Database Design** : PostgreSQL avancé, optimisation requêtes
- 🚀 **API Development** : FastAPI, documentation, versioning
- 🤖 **Machine Learning** : Classification, feature engineering, évaluation
- 📈 **Data Science** : Analyses statistiques, visualisations, insights
- 🔧 **DevOps** : CI/CD, tests, déploiement production, monitoring

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment participer :

```bash
# 1. Fork et clone
git clone https://github.com/Gouesse05/projetetudeaccidentfrance.git
cd projetetudeaccidentfrance

# 2. Créer une branche feature
git checkout -b feature/ma-super-fonctionnalite

# 3. Développer et tester
pytest tests/ -v  # Les tests doivent passer !

# 4. Commit avec message descriptif
git commit -am "feat: Ajouter analyse de corrélation avancée"

# 5. Push vers votre fork
git push origin feature/ma-super-fonctionnalite

# 6. Ouvrir une Pull Request sur GitHub
```

**Conventions** :
- Code style : PEP 8 (utilisez `black` pour le formatage)
- Tests : Couverture minimale de 80%
- Commits : Convention [Conventional Commits](https://www.conventionalcommits.org/)
- Documentation : Docstrings pour toutes les fonctions publiques

---

## 📊 Statut du Projet

### ✅ Phases Complétées

| Phase | Description | Lignes de Code | Statut |
|-------|-------------|----------------|--------|
| **Phase 1** | **Pipeline ETL** | 2 500 | ✅ 100% |
| **Phase 2** | **Analyses Données** | 1 200 | ✅ 100% |
| **Phase 3** | **PostgreSQL** | 1 776 | ✅ 100% |
| **Phase 4** | **API FastAPI** | 1 862 | ✅ 100% |
| **Phase 5** | **Déploiement Render** | 500 | ✅ 100% |
| **Phase 6** | **Notebooks & Dashboard** | 1 800 | ✅ 100% |

### 🚀 Prochaines Évolutions

- ⏳ **SDK Python Client** : Bibliothèque cliente pour faciliter l'usage de l'API
- ⏳ **Authentification JWT** : Sécurisation des endpoints sensibles
- ⏳ **Cache Redis** : Amélioration des performances pour requêtes fréquentes
- ⏳ **WebSockets** : Notifications en temps réel pour nouveaux accidents
- ⏳ **Dashboard Admin** : Interface de gestion et monitoring
- ⏳ **API GraphQL** : Alternative à l'API REST pour requêtes complexes

### 📈 Métriques

- **Code Total** : ~10 000 lignes Python
- **Couverture Tests** : 95%
- **Endpoints API** : 25+
- **Tables DB** : 8
- **Notebooks** : 4
- **Documentation** : 100%
- **Statut** : ✅ **Production Ready**

---

## 🛠️ Dépannage

### ❌ L'API ne démarre pas

```bash
# Vérifier la version de Python (doit être 3.12+)
python --version

# Réinstaller les dépendances
pip install --upgrade -r requirements.txt

# Vérifier la syntaxe
python -m py_compile src/api/main.py

# Tester le démarrage en mode verbose
uvicorn src.api.main:app --reload --log-level debug
```

### ❌ Erreur de connexion à la base de données

```bash
# Vérifier les variables d'environnement
cat .env | grep DATABASE_URL

# Tester la connexion PostgreSQL
psql $DATABASE_URL -c "SELECT version();"

# Vérifier que PostgreSQL est actif
pg_isready -h localhost

# Recréer le schéma
python src/database/init_schema.py
```

### ❌ Les tests échouent

```bash
# Lancer avec sortie détaillée
pytest tests/ -vv --tb=long

# Vérifier la base de données test
psql -c "CREATE DATABASE accidents_test_db;"

# Nettoyer et réinstaller
pip uninstall -y -r requirements.txt
pip install -r requirements.txt
pytest tests/ -v
```

### ❌ Problèmes de notebooks

```bash
# Installer Jupyter si manquant
pip install jupyter jupyterlab

# Lancer Jupyter
jupyter notebook notebooks/

# Problème de kernel
python -m ipykernel install --user --name=venv
```

📖 Pour plus de détails : [docs/PHASE5_RENDER_DEPLOYMENT.md - Section Dépannage](docs/PHASE5_RENDER_DEPLOYMENT.md#dépannage)

---

## 📞 Support & Contact

- **🐛 Problèmes & Bugs** : [GitHub Issues](https://github.com/Gouesse05/projetetudeaccidentfrance/issues)
- **💡 Nouvelles Fonctionnalités** : [GitHub Discussions](https://github.com/Gouesse05/projetetudeaccidentfrance/discussions)
- **📖 Documentation** : Dossier `/docs` du repository

**Liens Production:**
- **🔷 API REST** : [https://projetetudeaccidentfrance.onrender.com](https://projetetudeaccidentfrance.onrender.com)
- **📖 Documentation API** : [https://projetetudeaccidentfrance.onrender.com/docs](https://projetetudeaccidentfrance.onrender.com/docs)
- **📊 Dashboard Streamlit** : [https://projetetudeaccidentfrance-dashboard.onrender.com](https://projetetudeaccidentfrance-dashboard.onrender.com)

**Développeur:**
- 👨‍💻 Voir [CV_GOUESSE_GO.md](CV_GOUESSE_GO.md)

---

## 📄 Licence

Ce projet est open source sous licence **MIT**.

Vous êtes libre de :
- ✅ Utiliser commercialement
- ✅ Modifier le code
- ✅ Distribuer
- ✅ Usage privé

Conditions :
- 📝 Conserver la notice de licence et copyright
- ⚠️ Le logiciel est fourni "tel quel", sans garantie

Voir le fichier [LICENSE](LICENSE) pour les détails complets.

---

## 🙏 Remerciements

- **📊 Source Données** : [data.gouv.fr](https://www.data.gouv.fr/) - Plateforme ouverte des données publiques françaises
- **🐍 Frameworks** : 
  - [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderne et rapide
  - [PostgreSQL](https://www.postgresql.org/) - Base de données relationnelle avancée
  - [Streamlit](https://streamlit.io/) - Framework de dashboards interactifs
  - [scikit-learn](https://scikit-learn.org/) - Machine Learning en Python
- **🌐 Hosting** : [Render.com](https://render.com/) - Plateforme de déploiement cloud
- **🔄 CI/CD** : [GitHub Actions](https://github.com/features/actions) - Automatisation des workflows
- **🧪 Testing** : [pytest](https://pytest.org/) - Framework de tests Python

---

<div align="center">

**🚗 Prêt à explorer les données d'accidents routiers ? 🚦**

[📖 Documentation API](https://accidents-api-prod.onrender.com/docs) | [📓 Notebooks](notebooks/) | [📊 Dashboard](dashboard/) | [💾 Data Pipeline](src/pipeline/)

---

*Développé avec ❤️ pour améliorer la sécurité routière en France*

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div> 

