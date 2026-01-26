"""
Script principal du pipeline ETL
Orchestre téléchargement → exploration → nettoyage
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.download_data import download_all_datasets
from pipeline.explore_and_clean import main as explore_and_clean

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_pipeline(force_download: bool = False, skip_download: bool = False) -> bool:
    """
    Exécute le pipeline ETL complet
    
    Args:
        force_download: Force le téléchargement même si fichiers existent
        skip_download: Ignore l'étape de téléchargement
    
    Returns:
        True si succès
    """
    
    logger.info("\n" + "=" * 80)
    logger.info(" DÉMARRAGE PIPELINE ETL - ACCIDENTS ROUTIERS")
    logger.info("=" * 80)
    logger.info(f"Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Étape 1: Téléchargement
        if not skip_download:
            logger.info("\n ÉTAPE 1: TÉLÉCHARGEMENT")
            logger.info("-" * 80)
            
            results = download_all_datasets(force=force_download)
            
            # Vérifier si au moins un dataset a réussi
            success_count = sum(1 for r in results.values() if r.get("success"))
            if success_count == 0:
                logger.error(" Aucun téléchargement réussi")
                return False
            
            logger.info(f" {success_count}/{len(results)} datasets téléchargés")
        else:
            logger.info("\n⏭  Téléchargement ignoré (--skip-download)")
        
        # Étape 2: Exploration et nettoyage
        logger.info("\n ÉTAPE 2: EXPLORATION ET NETTOYAGE")
        logger.info("-" * 80)
        
        success = explore_and_clean()
        
        if not success:
            logger.error(" Erreur lors de l'exploration/nettoyage")
            return False
        
        # Succès
        logger.info("\n" + "=" * 80)
        logger.info(" PIPELINE COMPLÉTÉ AVEC SUCCÈS")
        logger.info("=" * 80)
        logger.info("\n Données nettoyées disponibles dans: data/clean/")
        logger.info(" Logs disponibles dans: pipeline.log")
        
        return True
        
    except Exception as e:
        logger.error(f"\n ERREUR PIPELINE: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Pipeline ETL pour données accidents routiers"
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Force le téléchargement même si fichiers existent"
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Ignore l'étape de téléchargement"
    )
    
    args = parser.parse_args()
    
    success = run_pipeline(
        force_download=args.force_download,
        skip_download=args.skip_download
    )
    
    exit(0 if success else 1)
