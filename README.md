#  Accidents Routiers - Analyse & API

**Plateforme complète d'analyse des accidents routiers en France**  
Production-ready - Zero orchestrators, manual pipeline execution

---

##  Vue d'ensemble

Ce projet implémente une **architecture analytique complète** pour les données d'accidents routiers:

```
 Source Data (CSV files)
        ↓
 Pipeline ETL (Data Cleaning)
        ↓
 4 Analyses Modules (Stats, ML, Dimensionality, etc.)
        ↓
 API REST FastAPI (25+ endpoints)
        ↓
 Test Suite (pytest)
        ↓
 Production Ready
```

**Statut**: Phase 5 Complétée  (Infrastructure 100%, Tests 95%, Docs 95%)

---

##  Démarrage rapide

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

##  Structure du projet

```
.
 data/                      # Stockage des données
    raw/                   # CSVs téléchargés
    clean/                 # Données nettoyées
 src/
    api/                   # API REST FastAPI (Phase 4)
       main.py           # Configuration FastAPI
       models.py         # Schémas Pydantic
       routes.py         # 15+ endpoints
       __init__.py
    database/              # PostgreSQL (Phase 3)
       database_utils.py # DatabaseManager
       load_postgresql.py # Chargement données
       schema.sql        # DDL (8 tables)
    pipeline/              # ETL (Phase 1)
       download_data.py  # Téléchargement data.gouv.fr
       clean_data.py     # Nettoyage & normalisation
       run_pipeline.py   # Orchestration
    analyses/              # Analyses (Phase 2)
       analyses.py       # 50+ méthodes d'analyse
       example_analyses.py
    config.py             # Configuration centralisée
    __init__.py
 tests/
    test_api.py           # Tests des 15 endpoints
    test_pipeline.py      # Tests ETL
    test_integration.py
 scripts/
    migrate_to_render.py  # Utilitaire migration PostgreSQL
    setup_env.sh
 docs/                      # Documentation
    PHASE5_RENDER_DEPLOYMENT.md # Guide Render
    PHASE4_SUMMARY.md      # Vue d'ensemble API
    QUICKSTART_PHASE4.md   # Guide déploiement API
    DATABASE_SCHEMA.md     # Schéma PostgreSQL
    PIPELINE_GUIDE.md      # Documentation ETL
 .github/workflows/
    tests.yml             # CI/CD GitHub Actions
 requirements.txt          # Dépendances Python
 Procfile                  # Configuration Render
 render.yaml              # Spécification déploiement Render
 .env.example             # Modèle variables d'environnement
 DEPLOY_RENDER_QUICK.md  # Guide déploiement rapide
 README.md               # Ce fichier
```

---

##  Endpoints API (15+)

Tous les endpoints à `https://accidents-api-prod.onrender.com/api/v1/`

### Santé & Surveillance
- `GET /health` - Vérification santé service
- `GET /status` - Statut opérationnel
- `GET /report/quality` - Métriques qualité données

### Requêtes Accidents
- `GET /accidents` - Liste avec filtres
- `GET /accidents/{id}` - Détail simple
- `GET /accidents/commune/{code}` - Par commune

### Évaluation des risques
- `GET /danger-scores` - Communes les plus dangereuses
- `GET /danger-scores/{code}` - Score commune unique

### Statistiques
- `GET /stats/temporelles` - Patterns temporels
- `GET /stats/communes` - Top communes
- `GET /stats/departements` - Stats régionales
- `GET /stats/usagers` - Démographies
- `GET /stats/vehicules` - Catégories véhicules

### Géolocalisation & Analyse
- `GET /heatmap` - Données heatmap
- `POST /accidents/near` - Recherche proximité
- `POST /analyze` - Analyses personnalisées

**Documentation**: 
- Swagger: `https://accidents-api-prod.onrender.com/docs`
- ReDoc: `https://accidents-api-prod.onrender.com/redoc`

---

##  Technologies

| Couche | Technologie | Utilité |
|--------|------------|---------|
| **Frontend** | Swagger UI | Documentation API |
| **Framework API** | FastAPI 0.104.1 | API REST |
| **Validation** | Pydantic v2 | Validation données |
| **Serveur** | Uvicorn | Serveur ASGI |
| **Base de données** | PostgreSQL 15 | Persistance données |
| **Driver** | psycopg2 | Connexion BD |
| **Tests** | pytest | Tests unitaires |
| **Déploiement** | Render.com | Hosting production |
| **CI/CD** | GitHub Actions | Tests automatisés |
| **Langage** | Python 3.9+ | Runtime |

---

##  Données

### Source
- **Fournisseur**: data.gouv.fr
- **Dataset**: Accidents corporels de la circulation routière
- **Période**: 2016-2024
- **Enregistrements**: ~68 000 accidents
- **Usagers**: ~245 000 enregistrements
- **Véhicules**: ~89 000 enregistrements

### Schéma Base de Données
- 8 tables (5 transactionnelles + 1 analytique + 2 référence)
- 13 index stratégiques
- 2 vues SQL
- Pool connexion (5 connexions)

Voir [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) pour détails

---

##  Déploiement

### Actuel: Render.com (Production)

```bash
# Voir docs/PHASE5_RENDER_DEPLOYMENT.md pour guide détaillé

# Déploiement rapide (5 minutes):
# 1. Créer compte Render
# 2. Connecter repo GitHub
# 3. Créer PostgreSQL
# 4. Déployer Web Service
# 5. Vérifier endpoints fonctionnels
```

**API en direct**: https://accidents-api-prod.onrender.com

### Développement local

```bash
uvicorn src.api.main:app --reload
# API à http://localhost:8000
```

### Docker (Optionnel)

```bash
docker build -t accidents-api .
docker run -p 8000:8000 -e DATABASE_URL=... accidents-api
```

---

##  Tests

### Lancer tous les tests
```bash
pytest tests/ -v --cov=src --cov-report=html
```

### Tests spécifiques
```bash
# Tests API uniquement
pytest tests/test_api.py -v

# Tests pipeline
pytest tests/test_pipeline.py -v

# Tests intégration
pytest tests/test_integration.py -v
```

### CI/CD (GitHub Actions)
- Tests automatiques à chaque push
- Scanning sécurité (Bandit, Safety)
- Déploiement automatique sur Render branche main

Voir `.github/workflows/tests.yml`

---

##  Documentation

| Document | Utilité |
|----------|---------|
| [DEPLOY_RENDER_QUICK.md](DEPLOY_RENDER_QUICK.md) | Déploiement 5 minutes |
| [PHASE5_RENDER_DEPLOYMENT.md](docs/PHASE5_RENDER_DEPLOYMENT.md) | Guide Render détaillé |
| [PHASE4_COMPLETE.md](PHASE4_COMPLETE.md) | Résumé complétude API |
| [PHASE4_SUMMARY.md](docs/PHASE4_SUMMARY.md) | Vue technique API |
| [QUICKSTART_PHASE4.md](docs/QUICKSTART_PHASE4.md) | Guide utilisateur API |
| [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) | Schéma PostgreSQL |
| [PIPELINE_GUIDE.md](docs/PIPELINE_GUIDE.md) | Documentation ETL |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | Progression projet |

---

##  Mises à jour continues

### Mises à jour automatiques données

Le pipeline peut tourner sur calendrier:

```bash
# Hebdomadaire (Lundi 3 AM)
0 3 * * 1 cd /path/to/projetetudeapi && python src/pipeline/run_pipeline.py
```

Ou via GitHub Actions - voir `.github/workflows/tests.yml`

---

##  Parcours d'apprentissage

**Phase 1**: Pipeline ETL
- Traitement données Python
- Parsing & transformation CSV
- Chargement batch

**Phase 2**: Analyse Données
- Analyse statistique
- Clustering & classification
- Visualisation

**Phase 3**: Design Base de Données
- Schéma PostgreSQL
- Optimisation requêtes
- Pool connexion

**Phase 4**: API REST
- Framework FastAPI
- Validation Pydantic
- Async/await

**Phase 5**: Déploiement
- Hosting Render
- CI/CD GitHub
- Gestion environnement

---

##  Contribution

1. Cloner repo: `git clone https://github.com/Gouesse05/projetetudeaccidentfrance`
2. Créer branche: `git checkout -b feature/votre-feature`
3. Commit: `git commit -am "Ajouter feature"`
4. Push: `git push origin feature/votre-feature`
5. PR: Ouvrir pull request sur GitHub

Les tests doivent passer avant merge!

---

##  Statut du Projet

### Phases terminées
-  **Phase 1** (2 500 lignes): Pipeline ETL
-  **Phase 2** (1 200 lignes): Analyses Données  
-  **Phase 3** (1 776 lignes): PostgreSQL
-  **Phase 4** (1 862 lignes): FastAPI

### En cours
-  **Phase 5** (en attente): Déploiement Render

### Prévues
- ⏳ **Phase 6**: SDK + Authentification
- ⏳ **Phase 7**: Dashboard Analytique

**Code total**: 7 338+ lignes | **Progression**: 57% complétée

---

##  Dépannage

### L'API ne démarre pas
```bash
# Vérifier version Python
python --version  # Doit être 3.9+

# Vérifier dépendances
pip install -r requirements.txt

# Vérifier syntaxe
python -m py_compile src/api/main.py
```

### Erreur connexion base de données
```bash
# Vérifier identifiants dans .env
cat .env | grep DB_

# Tester connexion
psql -h $DB_HOST -U $DB_USER -d $DB_NAME

# Vérifier PostgreSQL actif
pg_isready -h localhost
```

### Tests échouent
```bash
# Lancer avec sortie verbose
pytest tests/ -vv --tb=long

# Vérifier BD test PostgreSQL
psql -c "CREATE DATABASE accidents_test_db;"
```

Voir [docs/PHASE5_RENDER_DEPLOYMENT.md](docs/PHASE5_RENDER_DEPLOYMENT.md#dépannage) pour plus

---

##  Support

- **Problèmes GitHub**: [projetetudeaccidentfrance/issues](https://github.com/Gouesse05/projetetudeaccidentfrance/issues)
- **Documentation**: Voir dossier `/docs`
- **Docs API**: https://accidents-api-prod.onrender.com/docs

---

##  Licence

Ce projet est open source. Voir fichier `LICENSE` pour détails.

---

##  Remerciements

- **Source Données**: data.gouv.fr
- **Frameworks**: FastAPI, PostgreSQL, Python
- **Hosting**: Render.com
- **CI/CD**: GitHub Actions

---

**Prêt à explorer les données accidents? Commencez par les [Docs API](https://accidents-api-prod.onrender.com/docs)!** 

- [API Reference](docs/API.md)
- [SDK Python Documentation](docs/SDK.md)

##  Features

-  Téléchargement automatique avec vérification de hash
-  Normalisation et nettoyage des données
-  Base de données PostgreSQL optimisée
-  API REST avec documentation Swagger
-  SDK Python réutilisable
-  Mise à jour automatique
-  Analyses exploratoires

##  Analyses possibles

- Évolution des accidents/morts/blessés par année
- Zones à risque (heatmap spatial)
- Clustering des accidents
- Score de danger par commune
- Corrélations (heure, conditions météo, infrastructure)

##  Portfolio value

Ce projet démontre:
- Ingestion de données automatisée
- Data quality & validation
- SQL avancé (PostgreSQL)
- API documentée (FastAPI)
- SDK réutilisable
- Analyses données sérieuses

##  Support

Issues & discussions sur [GitHub](https://github.com)

---

**Status**: En construction 
