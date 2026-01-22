# 🚗 Pipeline Données Accidents Routiers

Pipeline ETL complet pour ingestion, exploration et nettoyage des données d'accidents routiers France.

## 📋 Contenu

- `download_data.py` - Téléchargement automatique avec vérification de hash
- `explore_and_clean.py` - Exploration et nettoyage des données
- `explore_datasources.py` - Script d'exploration des sources data.gouv.fr
- `data_config.py` - Configuration centralisée des datasets
- `run_pipeline.py` - Orchestration du pipeline ETL complet

## 🚀 Utilisation rapide

### 1. Explorer les sources de données

```bash
python explore_datasources.py
```

Affiche les datasets disponibles sur data.gouv.fr et leurs ressources.

### 2. Télécharger les données

```bash
# Téléchargement normal
python download_data.py

# Forcer le re-téléchargement
python download_data.py --force

# Afficher les URLs et explorer
python explore_datasources.py
```

**Résultat**: Fichiers téléchargés dans `data/raw/` avec métadonnées en `.metadata.json`

### 3. Explorer et nettoyer

```bash
python explore_and_clean.py
```

Affiche les statistiques des données brutes et génère les fichiers nettoyés dans `data/clean/`

### 4. Pipeline complet

```bash
# Pipeline complet
python run_pipeline.py

# Avec options
python run_pipeline.py --force-download
python run_pipeline.py --skip-download  # Sauter téléchargement
```

## 📊 Flux du pipeline

```
data.gouv.fr
     ↓
download_data.py (télécharge + vérif hash)
     ↓
data/raw/*.csv
     ↓
explore_and_clean.py (exploration + nettoyage)
     ↓
data/clean/*.csv
     ↓
(prêt pour PostgreSQL)
```

## 🔧 Configuration

Éditer `data_config.py` pour:
- Ajouter/modifier les URLs des datasets
- Configurer le nettoyage (colonnes à garder, traitement valeurs manquantes)
- Définir les validations
- Configurer l'import PostgreSQL

## 📝 Fonctionnalités

### `download_data.py`

✅ Téléchargement depuis data.gouv.fr
✅ Vérification de hash MD5
✅ Détection des changements
✅ Métadonnées de tracking
✅ Gestion des erreurs réseau
✅ Barre de progression

**Métadonnées sauvegardées**:
- Hash du fichier (MD5)
- Hash distant
- Date de téléchargement
- Taille du fichier
- URL de source

### `explore_and_clean.py`

✅ Exploration complète des CSV
✅ Statistiques descriptives
✅ Détection des valeurs manquantes
✅ Suppression des doublons
✅ Normalisation des noms de colonnes
✅ Conversion des types de données
✅ Rapport de qualité

**Nettoyages appliqués**:
- Supprimer les doublons
- Supprimer les colonnes vides
- Normaliser les noms (minuscules, underscores)
- Gérer les valeurs manquantes
- Convertir les dates
- Convertir les numériques
- Supprimer les espaces inutiles

### `explore_datasources.py`

✅ Exploration de l'API data.gouv.fr
✅ Lister les datasets de Sécurité Routière
✅ Récupérer les URLs de ressources
✅ Informations de mise à jour

## 📂 Structure des données

### Raw (avant nettoyage)

```
data/raw/
├── accidents.csv          # Données d'accidents
├── caracteristiques.csv   # Caractéristiques des accidents
├── lieux.csv             # Lieux (coordonnées, routes)
├── usagers.csv           # Données des usagers
├── vehicules.csv         # Données des véhicules
└── .metadata.json        # Métadonnées de téléchargement
```

### Clean (après nettoyage)

```
data/clean/
├── clean_accidents.csv
├── clean_caracteristiques.csv
├── clean_lieux.csv
├── clean_usagers.csv
└── clean_vehicules.csv
```

## 🔑 Colonnes principales

### accidents
- `Num_Acc` - Numéro d'accident (clé primaire)
- `Date` - Date de l'accident
- `an`, `mois`, `jour` - Décomposition temporelle
- `hrmn` - Heure et minute
- `dep` - Code département
- `com` - Code commune
- `grav` - Gravité de l'accident
- `nbv` - Nombre de véhicules

### caracteristiques
- `Num_Acc` - Référence accident
- `mois` - Mois
- `jour` - Jour
- `lumnos` - Luminosité
- `agglo` - Agglomération
- `int` - Intersection
- `atm` - Conditions atmosphériques
- `col` - Type de collision

### lieux
- `Num_Acc` - Référence accident
- `route` - Type de route
- `Latitude` - Coordonnée latitude
- `Longitude` - Coordonnée longitude
- `surf` - Surface de la route
- `infra` - Type d'infrastructure
- `situ` - Situation de l'accident

### usagers
- `Num_Acc` - Référence accident
- `Num_Veh` - Numéro véhicule
- `num_occupant` - Numéro occupant
- `Date_naiss` - Date de naissance
- `sexe` - Sexe
- `place` - Place dans le véhicule
- `actp` - Activité
- `secu` - Équipement de sécurité
- `grav` - Gravité des blessures

### vehicules
- `Num_Acc` - Référence accident
- `Num_Veh` - Numéro véhicule
- `senc` - Sens de circulation
- `catv` - Catégorie véhicule
- `occus` - Nombre occupants

## 📊 Exemple de rapport de qualité

```
📊 RAPPORT DE QUALITÉ DES DONNÉES

📁 accidents.csv
  Lignes: 1,234,567
  Colonnes: 28
  Taille: 245.50 MB
  Doublons: 1,234
  Données manquantes:
    - grav: 5,234 (0.4%)
    - agg: 12,345 (1.0%)
    - atm: 2,345 (0.2%)
```

## 🛠️ Logs

Les logs sont écrits dans:
- `pipeline.log` - Fichier de log
- Console - Affichage en temps réel

Niveau: INFO (tous les détails)

## ⚙️ Requirements

```
pandas>=1.3.0
requests>=2.26.0
numpy>=1.21.0
psycopg2-binary>=2.9.0
python-dotenv>=0.19.0
```

## 🚨 Troubleshooting

### Erreur de téléchargement
```
✗ Erreur téléchargement: Connection timeout
```
→ Vérifier la connexion réseau et les URLs

### Fichier non trouvé
```
⚠ Aucun fichier CSV trouvé dans data/raw/
```
→ Exécuter d'abord `python download_data.py`

### Erreur d'encodage
```
✗ Erreur lors de l'exploration: 'utf-8' codec can't decode
```
→ Modifier l'encodage dans `data_config.py`

## 📈 Prochaines étapes

1. ✅ Téléchargement + nettoyage
2. ⏭️ Import PostgreSQL
3. ⏭️ API FastAPI
4. ⏭️ Analyses et dashboards

## 📞 Support

Voir le README principal: `../../README.md`
