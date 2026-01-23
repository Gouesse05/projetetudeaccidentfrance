# 📦 Archive - Fichiers Anciens/Obsolètes

Ce dossier contient les fichiers qui ont été **archivés et ne sont plus utilisés**.

## 📋 Contenu

### Orchestration Files (Airflow & Dagster)

**analysis_pipeline.py** (13 KB)
- Ancien DAG Airflow pour orchestration des analyses
- Statut: ✗ Deprecated (remplacé par run_pipeline.py)

**analysis_pipeline_dagster.py** (11 KB)
- DAG Dagster (tentative de migration)
- Statut: ✗ Deprecated (conflit Pydantic)

**accidents_pipeline.py** (7 KB)
- Ancien DAG Airflow pour pipeline accidents
- Statut: ✗ Deprecated

**maintenance.py** (7 KB)
- Tâches de maintenance Airflow
- Statut: ✗ Deprecated

**setup_airflow.sh** (7 KB)
- Script de setup Airflow
- Statut: ✗ Deprecated

## ❌ Pourquoi archivé?

### Airflow
- ❌ Trop de dépendances conflictuelles
- ❌ Complexe pour un small project
- ❌ Overhead d'installation importante
- ✅ Remplacé par: `run_pipeline.py`

### Dagster
- ❌ Conflit avec Pydantic 2.x
- ❌ dbt-semantic-interfaces nécessite Pydantic 1.x
- ❌ FastAPI nécessite Pydantic 2.x
- ✅ Remplacé par: `run_pipeline.py`

## 🚀 Nouvelle Solution

Tous les orchestrateurs ont été remplacés par:

```
/home/sdd/projetetudeapi/run_pipeline.py
```

**Avantages:**
- ✅ Aucune dépendance externe
- ✅ Exécution simple et directe
- ✅ Logs détaillés
- ✅ Model persistence
- ✅ Report generation
- ✅ Step-by-step execution
- ✅ CLI arguments support

## 📖 Comment Utiliser

```bash
# Pipeline complet
python run_pipeline.py

# Étape unique
python run_pipeline.py --step data_cleaning

# Voir l'aide
python run_pipeline.py --help
```

## 📚 Références

Pour plus d'informations:
- `PIPELINE_README.md` - Guide d'utilisation
- `ANALYSIS_REPORT.md` - Analyse du projet
- `run_pipeline.py` - Code source (335 lignes)

## 🔄 Migration Future

Si vous avez besoin d'orchestration avancée à l'avenir:
1. Intégrer **Prefect** (plus moderne)
2. Ou utiliser **Apache Airflow 2.10+** (avec venv séparé)
3. Ou migrer vers **Kubernetes Jobs**

---

**Archivé:** 2026-01-23  
**Raison:** Simplification et élimination des conflits de dépendances  
**Status:** ✅ Nettoyage complet du projet
