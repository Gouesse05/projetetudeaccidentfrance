# 🚗 Pipeline Data Accidents Routiers

Architecture professionnelle d'ingestion, transformation et exposition de données d'accidents routiers.

## 📊 Architecture

```
data.gouv.fr
   ↓ (download auto)
CSV bruts (raw)
   ↓
Nettoyage / normalisation (Python)
   ↓
PostgreSQL (core data)
   ↓
API REST FastAPI
   ↓
SDK (Python / JS)
   ↓
Analyses / Dashboards
```

## 🚀 Démarrage rapide

### 1. Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration

```bash
cp .env.example .env
# Éditer .env avec vos paramètres PostgreSQL
```

### 3. Initialiser la base de données

```bash
python src/database/init_schema.py
```

### 4. Télécharger et charger les données

```bash
python src/pipeline/download_data.py
python src/pipeline/clean_data.py
python src/pipeline/load_postgresql.py
```

### 5. Lancer l'API

```bash
uvicorn src.api.main:app --reload
```

API disponible sur `http://localhost:8000`

Documentation Swagger: `http://localhost:8000/docs`

## 📁 Structure du projet

```
.
├── data/
│   ├── raw/              # CSV téléchargés (bruts)
│   └── clean/            # CSV nettoyés
├── src/
│   ├── api/              # API FastAPI
│   ├── database/         # Schéma PostgreSQL
│   ├── pipeline/         # ETL (extraction, transformation, chargement)
│   ├── sdk/              # SDK Python & JavaScript
│   └── analyses/         # Analyses & visualisations
├── tests/                # Tests unitaires
├── docs/                 # Documentation
├── .github/workflows/    # CI/CD (GitHub Actions)
├── requirements.txt      # Dépendances Python
└── README.md
```

## 🔄 Pipeline automatisé

Mise à jour hebdomadaire via GitHub Actions ou cron local:

```bash
0 3 * * 1 cd /path/to/projetetudeapi && python src/pipeline/download_data.py && python src/pipeline/clean_data.py && python src/pipeline/load_postgresql.py
```

## 🧪 Tests

```bash
pytest tests/ -v --cov=src
```

## 📚 Documentation

- [Schema PostgreSQL](docs/SCHEMA.md)
- [API Reference](docs/API.md)
- [SDK Python Documentation](docs/SDK.md)

## 🔑 Features

- ✅ Téléchargement automatique avec vérification de hash
- ✅ Normalisation et nettoyage des données
- ✅ Base de données PostgreSQL optimisée
- ✅ API REST avec documentation Swagger
- ✅ SDK Python réutilisable
- ✅ Mise à jour automatique
- ✅ Analyses exploratoires

## 📊 Analyses possibles

- Évolution des accidents/morts/blessés par année
- Zones à risque (heatmap spatial)
- Clustering des accidents
- Score de danger par commune
- Corrélations (heure, conditions météo, infrastructure)

## 👨‍💼 Portfolio value

Ce projet démontre:
- Ingestion de données automatisée
- Data quality & validation
- SQL avancé (PostgreSQL)
- API documentée (FastAPI)
- SDK réutilisable
- Analyses données sérieuses

## 📞 Support

Issues & discussions sur [GitHub](https://github.com)

---

**Status**: En construction 🔨
