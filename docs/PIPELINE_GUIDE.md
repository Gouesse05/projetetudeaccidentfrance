# 📥 Guide d'utilisation du Pipeline ETL

## Vue d'ensemble

Le pipeline ETL automatise:
1. **Téléchargement** des données d'accidents depuis data.gouv.fr
2. **Exploration** complète des datasets
3. **Nettoyage** intelligent des données
4. **Préparation** pour import PostgreSQL

## 🚀 Démarrage rapide

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Exploration des sources

```bash
cd src/pipeline
python explore_datasources.py
```

Cela affiche:
- Les datasets disponibles sur data.gouv.fr
- Les organisations de Sécurité Routière
- Les URLs des fichiers CSV

### Télécharger les données

```bash
python download_data.py
```

**Résultat**: Fichiers téléchargés dans `data/raw/`

### Explorer et nettoyer

```bash
python explore_and_clean.py
```

**Résultat**: 
- Statistiques complètes des données brutes
- Fichiers nettoyés dans `data/clean/`
- Rapport de qualité

### Pipeline complet (recommandé)

```bash
python run_pipeline.py
```

Combine tout en une seule commande avec logging complet.

## 📊 Exemple d'exécution

```bash
$ python run_pipeline.py

================================================================================
🚀 DÉMARRAGE PIPELINE ETL - ACCIDENTS ROUTIERS
================================================================================
Heure: 2024-01-22 14:30:45

📥 ÉTAPE 1: TÉLÉCHARGEMENT
────────────────────────────────────────────────────────────────────────────────

🔍 Dataset: accidents
────────────────────────────────────────────────────────────────────────────────
  Ressource trouvée: accidents.csv
✓ 1 ressources trouvées pour accidents
🔐 Calcul du hash distant...
📥 Téléchargement: accidents.csv
  Progression: 100.0%
✓ Téléchargement réussi: accidents.csv

... (autres datasets)

✓ 5/5 datasets téléchargés

🔍 ÉTAPE 2: EXPLORATION ET NETTOYAGE
────────────────────────────────────────────────────────────────────────────────

📂 Exploration: accidents.csv
────────────────────────────────────────────────────────────────────────────────
  Lignes: 1,234,567
  Colonnes: 28
  Taille: 245.50 MB
  Doublons: 1,234

  📋 Colonnes:
    - Num_Acc                     | int64           | Missing:      0 ( 0.00%)
    - Date                        | object          | Missing:    125 ( 0.01%)
    - an                          | int64           | Missing:      0 ( 0.00%)
    ...

🧹 Nettoyage données accidents
────────────────────────────────────────────────────────────────────────────────
  Doublons supprimés: 1,234
  Noms de colonnes normalisés
  Valeurs manquantes traitées
✓ Nettoyage terminé: 1,233,333 lignes

... (autres fichiers)

📊 RAPPORT DE QUALITÉ DES DONNÉES
════════════════════════════════════════════════════════════════════════════════

📁 accidents.csv
  Lignes: 1,233,333
  Colonnes: 27
  Taille: 244.23 MB
  Doublons: 0
  Données manquantes:
    - grav: 5,234 (0.4%)
    - agglo: 2,345 (0.2%)

...

════════════════════════════════════════════════════════════════════════════════
✅ PIPELINE COMPLÉTÉ AVEC SUCCÈS
════════════════════════════════════════════════════════════════════════════════

📂 Données nettoyées disponibles dans: data/clean/
📋 Logs disponibles dans: pipeline.log
```

## 🔧 Options avancées

### Forcer le re-téléchargement

```bash
python download_data.py --force
```

Ignore les métadonnées et retélécharge tous les fichiers.

### Sauter l'étape de téléchargement

```bash
python run_pipeline.py --skip-download
```

Utile pour tester le nettoyage sur des données existantes.

## 📁 Fichiers générés

### Métadonnées de téléchargement

`data/raw/.metadata.json`:
```json
{
  "files": {
    "accidents.csv": {
      "hash": "abc123def456...",
      "remote_hash": "abc123def456...",
      "download_url": "https://...",
      "downloaded_at": "2024-01-22T14:30:45.123456",
      "size": 256789012
    }
  }
}
```

### Logs du pipeline

`pipeline.log`:
```
2024-01-22 14:30:45 - INFO - 🚀 DÉMARRAGE PIPELINE ETL - ACCIDENTS ROUTIERS
2024-01-22 14:30:46 - INFO - ✓ Répertoire données: /path/to/data/raw
2024-01-22 14:30:47 - INFO - 🔍 Dataset: accidents
...
```

## 🎯 Configuration personnalisée

Éditer `src/pipeline/data_config.py` pour personnaliser:

### URLs des datasets

```python
DATASETS_CONFIG = {
    "accidents_securite_routiere": {
        "api_url": "https://...",
        "dataset_slug": "base-de-donnees-accidents-de-la-circulation",
        "csv_files": ["accidents.csv", ...]
    }
}
```

### Nettoyage

```python
CLEANING_CONFIG = {
    "accidents": {
        "primary_key": ["Num_Acc"],
        "date_columns": ["Date", "jour"],
        "remove_duplicates": True,
        "handle_missing": {
            "threshold_pct": 50
        }
    }
}
```

### Validation

```python
VALIDATION_CONFIG = {
    "min_rows_per_file": {
        "accidents": 100
    },
    "required_columns": {
        "accidents": ["Num_Acc", "Date", "an"]
    }
}
```

## 🔍 Dépannage

### Erreur de connexion réseau

```
✗ Erreur téléchargement: ('Connection aborted.', RemoteDisconnected(...))
```

**Solution**: Vérifier la connexion et les URLs dans `data_config.py`

### Fichier déjà téléchargé (hash identique)

```
  → Hash identique, pas de mise à jour
✓ Fichier déjà à jour, pas de téléchargement
```

**C'est normal!** Ajouter `--force` pour forcer.

### Erreur d'encodage UTF-8

```
✗ Erreur lors de l'exploration: 'utf-8' codec can't decode byte 0x...
```

**Solution**: Changer l'encodage dans `data_config.py`:
```python
"encoding": "latin-1"  # ou iso-8859-1
```

### Pas de fichiers trouvés

```
⚠ Aucun fichier CSV trouvé dans data/raw/
```

**Solution**: Exécuter d'abord `python download_data.py`

## 📊 Comprendre les résultats

### Structure des données nettoyées

```
data/clean/
├── clean_accidents.csv          # Accidents routiers
├── clean_caracteristiques.csv   # Caractéristiques détaillées
├── clean_lieux.csv              # Lieux (géolocalisation)
├── clean_usagers.csv            # Données d'usagers
└── clean_vehicules.csv          # Données de véhicules
```

### Format des colonnes nettoyées

- **Noms**: minuscules avec underscores (`num_accident` au lieu de `Num Acc`)
- **Types**: convertis automatiquement (dates → datetime, nombres → numeric)
- **Valeurs manquantes**: traitées intelligemment
- **Doublons**: supprimés
- **Espaces**: supprimés des valeurs texte

## 🔄 Automatisation

### Exécution quotidienne (cron)

```bash
# Éditer crontab
crontab -e

# Ajouter:
0 3 * * * cd /path/to/projetetudeapi && python src/pipeline/run_pipeline.py --skip-download
```

Exécute à 3h du matin chaque jour (exploration/nettoyage seulement)

### Avec téléchargement hebdomadaire

```bash
# Crontab
0 3 * * 1 cd /path/to/projetetudeapi && python src/pipeline/run_pipeline.py
```

Exécute le pipeline complet chaque lundi à 3h du matin

## ✅ Validation du pipeline

### Tests

```bash
pytest tests/test_pipeline.py -v
```

### Vérifier les métadonnées

```bash
cat data/raw/.metadata.json
```

### Vérifier les fichiers nettoyés

```bash
ls -lh data/clean/
```

## 📈 Prochaines étapes

Une fois le pipeline exécuté:

1. **Vérifier les données**: `data/clean/*.csv` contient les fichiers nettoyés
2. **Créer le schéma PostgreSQL**: Voir `src/database/`
3. **Charger les données**: `python src/pipeline/load_postgresql.py`
4. **Lancer l'API**: `uvicorn src.api.main:app`

## 🆘 Besoin d'aide?

- Consulter les logs: `tail -f pipeline.log`
- Vérifier la configuration: `src/pipeline/data_config.py`
- Lancer en mode verbeux: Les scripts affichent tous les détails en INFO level

## 📚 Ressources

- [data.gouv.fr - Accidents routiers](https://www.data.gouv.fr/)
- [Sécurité Routière - Open data](https://www.data.gouv.fr/organizations/securite-routiere/)
- [Pandas documentation](https://pandas.pydata.org/docs/)
- [Python requests](https://requests.readthedocs.io/)
