"""
Test d'intégration du pipeline - Démonstration avec données de test
"""

import sys
import os
from pathlib import Path
import pandas as pd
import logging

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Chemins
BASE_DIR = Path(__file__).parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
CLEAN_DATA_DIR = BASE_DIR / "data" / "clean"

# Ajouter src au path
sys.path.insert(0, str(BASE_DIR / "src"))

from pipeline.explore_and_clean import (
    clean_accidents_data,
    clean_caracteristiques_data,
    clean_lieux_data,
    clean_usagers_data,
    clean_vehicules_data,
    save_clean_data
)


def create_sample_data():
    """Crée des fichiers CSV de test"""
    
    logger.info("\n" + "=" * 80)
    logger.info(" CRÉATION DE DONNÉES DE TEST")
    logger.info("=" * 80)
    
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Sample accidents
    accidents_data = {
        'Num_Acc': [1, 2, 3, 4, 5, 1],  # 1 doublon
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05', '2024-01-01'],
        'an': [2024, 2024, 2024, 2024, 2024, 2024],
        'mois': [1, 1, 1, 1, 1, 1],
        'jour': [1, 2, 3, 4, 5, 1],
        'hrmn': ['14:30', '09:15', '16:45', '08:00', '22:30', '14:30'],
        'dep': ['75', '75', '92', '93', '94', '75'],
        'com': ['75056', '75056', '92040', '93008', '94015', '75056'],
        'grav': [2, 3, 2, 1, 2, 2],
        'nbv': [2, 2, 3, 2, 2, 2],
        'nbp': [2, 2, 4, 3, 2, 2]
    }
    df_accidents = pd.DataFrame(accidents_data)
    df_accidents.to_csv(RAW_DATA_DIR / "accidents.csv", index=False)
    logger.info(" accidents.csv créé (6 lignes, 1 doublon)")
    
    # Sample caracteristiques
    caracteristiques_data = {
        'Num_Acc': [1, 2, 3, 4, 5],
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
        'lumnos': [1, 2, 1, 1, 3],
        'agglo': [1, 1, 0, 1, 0],
        'int': [1, 0, 1, 0, 1],
        'atm': [1, 1, 1, 2, 1],
        'col': [1, 2, 1, 1, 1]
    }
    df_caract = pd.DataFrame(caracteristiques_data)
    df_caract.to_csv(RAW_DATA_DIR / "caracteristiques.csv", index=False)
    logger.info(" caracteristiques.csv créé (5 lignes)")
    
    # Sample lieux
    lieux_data = {
        'Num_Acc': [1, 2, 3, 4, 5],
        'route': [1, 2, 1, 3, 1],
        'Latitude': ['48.8566', '48.9566', '48.7566', '48.8566', '48.8366'],
        'Longitude': ['2.3522', '2.3522', '2.3522', '2.4522', '2.3522'],
        'surf': [1, 1, 1, 2, 1],
        'infra': [0, 0, 0, 1, 0],
        'situ': [1, 1, 1, 1, 1]
    }
    df_lieux = pd.DataFrame(lieux_data)
    df_lieux.to_csv(RAW_DATA_DIR / "lieux.csv", index=False)
    logger.info(" lieux.csv créé (5 lignes)")
    
    # Sample usagers
    usagers_data = {
        'Num_Acc': [1, 1, 2, 3, 4],
        'Num_Veh': [1, 2, 1, 1, 1],
        'num_occupant': [1, 1, 1, 2, 1],
        'Date_naiss': ['1980-05-12', '1995-03-22', '1975-11-08', '1988-07-15', '1992-02-28'],
        'sexe': [1, 2, 1, 2, 1],
        'place': [1, 2, 1, 2, 1],
        'actp': [1, 1, 1, 1, 1],
        'secu': [1, 1, 0, 1, 1],
        'grav': [2, 2, 2, 1, 2]
    }
    df_usagers = pd.DataFrame(usagers_data)
    df_usagers.to_csv(RAW_DATA_DIR / "usagers.csv", index=False)
    logger.info(" usagers.csv créé (5 lignes)")
    
    # Sample vehicules
    vehicules_data = {
        'Num_Acc': [1, 1, 2, 3, 4],
        'Num_Veh': [1, 2, 1, 1, 1],
        'senc': [1, 1, 2, 1, 1],
        'catv': [1, 1, 2, 1, 1],
        'occus': [2, 2, 1, 2, 1]
    }
    df_vehicules = pd.DataFrame(vehicules_data)
    df_vehicules.to_csv(RAW_DATA_DIR / "vehicules.csv", index=False)
    logger.info(" vehicules.csv créé (5 lignes)")
    
    return True


def test_pipeline():
    """Test complet du pipeline"""
    
    logger.info("\n" + "=" * 80)
    logger.info(" TEST PIPELINE ETL")
    logger.info("=" * 80)
    
    # Créer données de test
    if not create_sample_data():
        logger.error(" Erreur création données de test")
        return False
    
    # Tester exploration et nettoyage
    logger.info("\n" + "=" * 80)
    logger.info(" NETTOYAGE ET VALIDATION")
    logger.info("=" * 80)
    
    CLEAN_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    test_files = [
        ("accidents.csv", clean_accidents_data, "accidents"),
        ("caracteristiques.csv", clean_caracteristiques_data, "caracteristiques"),
        ("lieux.csv", clean_lieux_data, "lieux"),
        ("usagers.csv", clean_usagers_data, "usagers"),
        ("vehicules.csv", clean_vehicules_data, "vehicules")
    ]
    
    results = {}
    
    for filename, clean_func, name in test_files:
        file_path = RAW_DATA_DIR / filename
        
        if not file_path.exists():
            logger.warning(f" {filename} non trouvé")
            continue
        
        logger.info(f"\n Traitement: {filename}")
        logger.info("-" * 60)
        
        # Charger
        df = pd.read_csv(file_path)
        logger.info(f"  Lignes avant: {len(df)}")
        logger.info(f"  Colonnes avant: {len(df.columns)}")
        
        # Nettoyer
        df_clean = clean_func(df)
        logger.info(f"  Lignes après: {len(df_clean)}")
        logger.info(f"  Colonnes après: {len(df_clean.columns)}")
        
        # Sauvegarder
        output_path = save_clean_data(df_clean, f"test_{filename}")
        
        results[name] = {
            "success": True,
            "rows": len(df_clean),
            "columns": len(df_clean.columns),
            "file": output_path
        }
    
    # Résumé
    logger.info("\n" + "=" * 80)
    logger.info(" RÉSUMÉ TEST")
    logger.info("=" * 80)
    
    for name, result in results.items():
        if result["success"]:
            logger.info(f" {name:20} | {result['rows']:4} lignes | {result['columns']:3} colonnes")
        else:
            logger.info(f" {name:20} | Erreur")
    
    logger.info("\n Fichiers nettoyés dans: " + str(CLEAN_DATA_DIR))
    
    # Vérification finale
    all_success = all(r.get("success") for r in results.values())
    
    if all_success:
        logger.info("\n TOUS LES TESTS PASSÉS")
        return True
    else:
        logger.error("\n CERTAINS TESTS ONT ÉCHOUÉ")
        return False


def cleanup_test_data():
    """Nettoie les données de test"""
    logger.info("\n" + "=" * 80)
    logger.info(" NETTOYAGE DES DONNÉES DE TEST")
    logger.info("=" * 80)
    
    import shutil
    
    for folder in [RAW_DATA_DIR, CLEAN_DATA_DIR]:
        if folder.exists():
            for file in folder.glob("*"):
                if file.is_file():
                    file.unlink()
                    logger.info(f"  Supprimé: {file.name}")
    
    logger.info(" Nettoyage terminé")


if __name__ == "__main__":
    import sys
    
    # Tests
    success = test_pipeline()
    
    # Nettoyage optionnel
    if "--cleanup" in sys.argv:
        cleanup_test_data()
    
    exit(0 if success else 1)
