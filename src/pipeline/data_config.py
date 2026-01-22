"""
Configuration des sources de données réelles
Données accidents routiers France (open data)
"""

# Format: {nom_dataset: {url_api_dataset, fichiers_csv_attendus}}

DATASETS_CONFIG = {
    # Dataset principal: Base de données des accidents de la circulation
    # Source: Ministère de l'Intérieur / Sécurité Routière
    "accidents_securite_routiere": {
        "api_url": "https://www.data.gouv.fr/api/1/organizations/securite-routiere/datasets",
        "dataset_slug": "base-de-donnees-accidents-de-la-circulation",
        "description": "Base de données d'accidents de la circulation depuis 2005",
        "csv_files": [
            "accidents.csv",
            "caracteristiques.csv",
            "lieux.csv",
            "usagers.csv",
            "vehicules.csv"
        ],
        "encoding": "utf-8",
        "separator": ",",
        "date_format": "%Y-%m-%d %H:%M:%S"
    },
    
    # Dataset alternatif: Baromètre de la sécurité routière
    "barometre_securite": {
        "api_url": "https://www.data.gouv.fr/api/1/organizations/securite-routiere/datasets",
        "dataset_slug": "barometre-de-la-securite-routiere",
        "description": "Données de sécurité routière et sinistralité",
        "csv_files": [
            "donnees_sinistralite.csv"
        ]
    },
    
    # Dataset secondaire: Données détaillées de communes
    "accidents_par_commune": {
        "api_url": "https://www.data.gouv.fr/api/1/organizations/securite-routiere/datasets",
        "dataset_slug": "accidents-par-commune",
        "description": "Synthèse des accidents par commune",
        "csv_files": [
            "accidents_communes.csv"
        ]
    }
}

# Configuration des ressources de données directes (URLs)
# Ces URLs peuvent changer, à mettre à jour selon la source réelle

DATA_URLS = {
    # URLs actuelles (à vérifier/mettre à jour)
    "accidents_2024": {
        "url": "https://www.data.gouv.fr/fr/datasets/r/...",  # À mettre à jour
        "format": "csv",
        "encoding": "utf-8"
    },
    "caracteristiques_2024": {
        "url": "https://www.data.gouv.fr/fr/datasets/r/...",  # À mettre à jour
        "format": "csv",
        "encoding": "utf-8"
    },
    "lieux_2024": {
        "url": "https://www.data.gouv.fr/fr/datasets/r/...",  # À mettre à jour
        "format": "csv",
        "encoding": "utf-8"
    }
}

# Configuration du nettoyage des données
CLEANING_CONFIG = {
    "accidents": {
        "primary_key": ["Num_Acc"],
        "date_columns": ["Date", "jour"],
        "numeric_columns": ["Num_Acc", "an", "mois"],
        "categorical_columns": ["dep", "com", "grav"],
        "remove_duplicates": True,
        "handle_missing": {
            "columns_to_drop": [],  # Colonnes à supprimer si trop de valeurs manquantes
            "threshold_pct": 50  # Seuil de % de données manquantes
        }
    },
    "caracteristiques": {
        "primary_key": ["Num_Acc"],
        "date_columns": ["Date"],
        "numeric_columns": ["Num_Acc"],
        "remove_duplicates": True
    },
    "lieux": {
        "primary_key": ["Num_Acc", "Num_Veh"],
        "numeric_columns": ["Num_Acc", "Num_Veh", "Latitude", "Longitude"],
        "remove_duplicates": True
    },
    "usagers": {
        "primary_key": ["Num_Acc", "Num_Veh", "num_occupant"],
        "date_columns": ["Date_naiss"],
        "numeric_columns": ["Num_Acc", "Num_Veh", "num_occupant"],
        "remove_duplicates": True
    },
    "vehicules": {
        "primary_key": ["Num_Acc", "Num_Veh"],
        "numeric_columns": ["Num_Acc", "Num_Veh", "num_occupant"],
        "remove_duplicates": True
    }
}

# Configuration de validation
VALIDATION_CONFIG = {
    "min_rows_per_file": {
        "accidents": 100,
        "caracteristiques": 100,
        "lieux": 100,
        "usagers": 100,
        "vehicules": 100
    },
    "required_columns": {
        "accidents": ["Num_Acc", "Date", "an", "mois", "jour", "dep", "com"],
        "caracteristiques": ["Num_Acc", "Date"],
        "lieux": ["Num_Acc"],
        "usagers": ["Num_Acc"],
        "vehicules": ["Num_Acc"]
    }
}

# Configuration de l'importation PostgreSQL
POSTGRESQL_CONFIG = {
    "batch_size": 10000,
    "use_copy": True,  # Utiliser COPY pour import (plus rapide)
    "ignore_conflicts": True,  # Ignorer les doublons
    "indexes": {
        "accidents": [
            "annee",
            "mois",
            "jour",
            "departement",
            "commune"
        ],
        "caracteristiques": [
            "num_accident"
        ],
        "lieux": [
            "num_accident",
            "latitude",
            "longitude"
        ]
    }
}

# Configuration des analyses
ANALYSIS_CONFIG = {
    "temporal_analysis": {
        "enabled": True,
        "group_by": ["year", "month", "day_of_week"],
        "metrics": ["accident_count", "injuries", "deaths"]
    },
    "spatial_analysis": {
        "enabled": True,
        "use_clustering": True,
        "clustering_algorithm": "dbscan"
    },
    "categorical_analysis": {
        "enabled": True,
        "group_by": ["department", "commune", "accident_type"]
    }
}

def get_dataset_config(name: str) -> dict:
    """Récupère la configuration d'un dataset"""
    return DATASETS_CONFIG.get(name, {})

def get_cleaning_config(file_type: str) -> dict:
    """Récupère la configuration de nettoyage"""
    return CLEANING_CONFIG.get(file_type, {})

def validate_config():
    """Valide la configuration des URLs"""
    missing_urls = []
    for name, config in DATA_URLS.items():
        if config.get("url", "").endswith("..."):
            missing_urls.append(name)
    
    if missing_urls:
        print(f"⚠️  URLs à mettre à jour: {missing_urls}")
        return False
    return True
