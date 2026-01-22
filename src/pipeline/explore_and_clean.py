"""
Exploration et nettoyage des données d'accidents routiers
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Tuple
from datetime import datetime

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Chemins
BASE_DIR = Path(__file__).parent.parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
CLEAN_DATA_DIR = BASE_DIR / "data" / "clean"


def ensure_clean_data_dir():
    """Crée le répertoire des données nettoyées"""
    CLEAN_DATA_DIR.mkdir(parents=True, exist_ok=True)


def explore_csv(file_path: Path) -> Dict:
    """
    Explore un fichier CSV et retourne des statistiques
    
    Args:
        file_path: Chemin du fichier CSV
    
    Returns:
        Dict avec infos sur le fichier
    """
    try:
        logger.info(f"\n📂 Exploration: {file_path.name}")
        logger.info("-" * 60)
        
        df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
        
        info = {
            "filename": file_path.name,
            "rows": len(df),
            "columns": len(df.columns),
            "size_mb": file_path.stat().st_size / (1024 * 1024),
            "columns_list": df.columns.tolist(),
            "dtypes": df.dtypes.to_dict(),
            "missing": df.isnull().sum().to_dict(),
            "duplicates": len(df) - len(df.drop_duplicates()),
            "shape": df.shape
        }
        
        logger.info(f"  Lignes: {info['rows']:,}")
        logger.info(f"  Colonnes: {info['columns']}")
        logger.info(f"  Taille: {info['size_mb']:.2f} MB")
        logger.info(f"  Doublons: {info['duplicates']}")
        
        logger.info(f"\n  📋 Colonnes:")
        for col in df.columns:
            missing = df[col].isnull().sum()
            missing_pct = (missing / len(df)) * 100
            dtype = df[col].dtype
            logger.info(f"    - {col:30} | {str(dtype):15} | Missing: {missing:6} ({missing_pct:5.2f}%)")
        
        logger.info(f"\n  📊 Statistiques descriptives (numériques):")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            logger.info(df[numeric_cols].describe().to_string())
        
        logger.info(f"\n  🔤 Exemples de données (5 premières lignes):")
        logger.info(df.head().to_string())
        
        return df, info
        
    except Exception as e:
        logger.error(f"✗ Erreur lors de l'exploration: {e}")
        return None, None


def explore_all_datasets():
    """Explore tous les fichiers CSV dans le répertoire raw"""
    
    ensure_clean_data_dir()
    
    logger.info("\n" + "=" * 80)
    logger.info("🔍 EXPLORATION DONNÉES BRUTES")
    logger.info("=" * 80)
    
    csv_files = list(RAW_DATA_DIR.glob("*.csv"))
    
    if not csv_files:
        logger.warning("⚠ Aucun fichier CSV trouvé dans data/raw/")
        return {}
    
    exploration_results = {}
    
    for csv_file in csv_files:
        df, info = explore_csv(csv_file)
        if df is not None:
            exploration_results[csv_file.name] = {
                "dataframe": df,
                "info": info
            }
    
    return exploration_results


def clean_accidents_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie les données d'accidents
    
    Args:
        df: DataFrame brut
    
    Returns:
        DataFrame nettoyé
    """
    logger.info("\n🧹 Nettoyage données accidents")
    logger.info("-" * 60)
    
    df = df.copy()
    initial_rows = len(df)
    
    # Supprimer les doublons complets
    df = df.drop_duplicates()
    logger.info(f"  Doublons supprimés: {initial_rows - len(df)}")
    
    # Supprimer les colonnes complètement vides
    df = df.dropna(axis=1, how='all')
    logger.info(f"  Colonnes vides supprimées")
    
    # Normaliser les noms de colonnes
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
    logger.info(f"  Noms de colonnes normalisés")
    
    # Gérer les valeurs manquantes
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            
            if missing_pct > 50:
                logger.warning(f"    {col}: {missing_pct:.1f}% manquant - suppression")
                df = df.drop(columns=[col])
            elif df[col].dtype == 'object':
                df[col] = df[col].fillna('UNKNOWN')
            elif df[col].dtype in ['int64', 'float64']:
                df[col] = df[col].fillna(df[col].median())
    
    logger.info(f"  Valeurs manquantes traitées")
    
    # Convertir les types de données
    date_cols = [col for col in df.columns if 'date' in col.lower() or 'jour' in col.lower()]
    for col in date_cols:
        try:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            logger.info(f"  {col} converti en datetime")
        except Exception as e:
            logger.warning(f"  ⚠ Erreur conversion {col}: {e}")
    
    # Supprimer les espaces des colonnes texte
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip()
    
    logger.info(f"✓ Nettoyage terminé: {len(df)} lignes")
    
    return df


def clean_caracteristiques_data(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie les données de caractéristiques"""
    
    logger.info("\n🧹 Nettoyage données caractéristiques")
    logger.info("-" * 60)
    
    df = df.copy()
    
    # Normaliser noms colonnes
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
    
    # Supprimer doublons
    df = df.drop_duplicates()
    
    # Gérer valeurs manquantes
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna('UNKNOWN')
        else:
            df[col] = df[col].fillna(0)
    
    logger.info(f"✓ Nettoyage terminé: {len(df)} lignes")
    
    return df


def clean_lieux_data(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie les données de lieux"""
    
    logger.info("\n🧹 Nettoyage données lieux")
    logger.info("-" * 60)
    
    df = df.copy()
    
    # Normaliser noms colonnes
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
    
    # Supprimer doublons
    df = df.drop_duplicates()
    
    # Gérer coordonnées GPS (si présentes)
    geo_cols = [col for col in df.columns if 'lat' in col.lower() or 'lon' in col.lower()]
    for col in geo_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    logger.info(f"✓ Nettoyage terminé: {len(df)} lignes")
    
    return df


def clean_usagers_data(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie les données d'usagers"""
    
    logger.info("\n🧹 Nettoyage données usagers")
    logger.info("-" * 60)
    
    df = df.copy()
    
    # Normaliser noms colonnes
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
    
    # Supprimer doublons
    df = df.drop_duplicates()
    
    logger.info(f"✓ Nettoyage terminé: {len(df)} lignes")
    
    return df


def clean_vehicules_data(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie les données de véhicules"""
    
    logger.info("\n🧹 Nettoyage données véhicules")
    logger.info("-" * 60)
    
    df = df.copy()
    
    # Normaliser noms colonnes
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
    
    # Supprimer doublons
    df = df.drop_duplicates()
    
    logger.info(f"✓ Nettoyage terminé: {len(df)} lignes")
    
    return df


def save_clean_data(df: pd.DataFrame, filename: str):
    """Sauvegarde un DataFrame nettoyé en CSV"""
    
    ensure_clean_data_dir()
    
    output_path = CLEAN_DATA_DIR / filename
    
    try:
        df.to_csv(output_path, index=False, encoding='utf-8')
        logger.info(f"✓ Fichier sauvegardé: {output_path.name}")
        return output_path
    except Exception as e:
        logger.error(f"✗ Erreur sauvegarde: {e}")
        return None


def generate_quality_report(exploration_results: Dict) -> str:
    """
    Génère un rapport de qualité des données
    
    Args:
        exploration_results: Résultats de l'exploration
    
    Returns:
        Rapport formaté
    """
    
    report = "\n" + "=" * 80 + "\n"
    report += "📊 RAPPORT DE QUALITÉ DES DONNÉES\n"
    report += "=" * 80 + "\n"
    
    for filename, data in exploration_results.items():
        info = data['info']
        report += f"\n📁 {filename}\n"
        report += f"  Lignes: {info['rows']:,}\n"
        report += f"  Colonnes: {info['columns']}\n"
        report += f"  Taille: {info['size_mb']:.2f} MB\n"
        report += f"  Doublons: {info['duplicates']}\n"
        
        # Colonnes avec données manquantes
        missing_cols = {col: count for col, count in info['missing'].items() if count > 0}
        if missing_cols:
            report += f"  Données manquantes:\n"
            for col, count in missing_cols.items():
                pct = (count / info['rows']) * 100
                report += f"    - {col}: {count} ({pct:.1f}%)\n"
    
    report += "\n" + "=" * 80 + "\n"
    
    return report


def main():
    """Fonction principale"""
    
    logger.info("\n" + "=" * 80)
    logger.info("🔍 EXPLORATION ET NETTOYAGE DONNÉES ACCIDENTS")
    logger.info("=" * 80)
    
    # Étape 1: Explorer
    exploration_results = explore_all_datasets()
    
    if not exploration_results:
        logger.error("✗ Aucune donnée à explorer")
        return False
    
    # Étape 2: Nettoyer et sauvegarder
    logger.info("\n" + "=" * 80)
    logger.info("🧹 NETTOYAGE DES DONNÉES")
    logger.info("=" * 80)
    
    cleaning_results = {}
    
    for filename, data in exploration_results.items():
        df = data['dataframe']
        
        # Appliquer le nettoyage approprié selon le type de fichier
        if 'accident' in filename.lower():
            cleaned_df = clean_accidents_data(df)
        elif 'caracteristique' in filename.lower():
            cleaned_df = clean_caracteristiques_data(df)
        elif 'lieu' in filename.lower():
            cleaned_df = clean_lieux_data(df)
        elif 'usager' in filename.lower():
            cleaned_df = clean_usagers_data(df)
        elif 'vehicule' in filename.lower():
            cleaned_df = clean_vehicules_data(df)
        else:
            cleaned_df = clean_accidents_data(df)  # Nettoyage générique par défaut
        
        # Sauvegarder
        output_path = save_clean_data(cleaned_df, f"clean_{filename}")
        if output_path:
            cleaning_results[filename] = {
                "output": output_path,
                "rows": len(cleaned_df),
                "columns": len(cleaned_df.columns)
            }
    
    # Étape 3: Générer rapport
    logger.info(generate_quality_report(exploration_results))
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ NETTOYAGE TERMINÉ")
    logger.info("=" * 80)
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
