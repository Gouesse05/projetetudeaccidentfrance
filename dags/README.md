#  Dossier dags/ - Archivé

Ce dossier était utilisé pour **Airflow DAGs** et **Dagster pipelines**.

##  Changement: Pipeline Manuel

À partir de **2026-01-23**, le projet utilise une **exécution manuelle simple** sans orchestrateur :

-  **Airflow** - Supprimé (trop de dépendances)
-  **Dagster** - Supprimé (conflits Pydantic)
-  **run_pipeline.py** - Exécution simple et directe

##  Nouvelle Approche

Tous les anciens fichiers DAG ont été archivés dans `/archive/`:

```
/archive/
 analysis_pipeline.py           # Ancien DAG Airflow
 analysis_pipeline_dagster.py   # Ancien DAG Dagster
 accidents_pipeline.py          # Ancien DAG Airflow
 maintenance.py                 # Maintenance Airflow
 setup_airflow.sh              # Setup script Airflow
```

##  Utilisation Actuelle

```bash
# Pipeline complet
python run_pipeline.py

# Étape spécifique
python run_pipeline.py --step data_cleaning
python run_pipeline.py --step statistical_analysis
python run_pipeline.py --step dimensionality_reduction
python run_pipeline.py --step machine_learning
```

## ℹ Pourquoi ce changement?

1. **Simplicité** - Pas de dépendances d'orchestration
2. **Maintenabilité** - Code plus facile à comprendre
3. **Flexibilité** - Exécution à la demande
4. **Performance** - Démarrage plus rapide
5. **Zéro Conflits** - Pas de conflits de dépendances

##  Documentation

- **PIPELINE_README.md** - Guide complet d'utilisation
- **run_pipeline.py** - Code du pipeline exécutable
- **ANALYSIS_REPORT.md** - Analyse du projet

---

**Mis à jour:** 2026-01-23  
**Status:**  Production-ready
