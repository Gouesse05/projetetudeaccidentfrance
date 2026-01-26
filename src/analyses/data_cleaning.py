"""
Module de nettoyage et préparation des données d'accidents.
Refactorisé à partir du notebook d'analyse.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


def load_accident_data(data_path: str) -> Dict[str, pd.DataFrame]:
    """
    Charge les 5 fichiers CSV d'accidents routiers.
    
    Args:
        data_path: Chemin vers le dossier contenant les CSVs
        
    Returns:
        Dict avec clés: 'lieux', 'usagers', 'vehicules', 'charge', 'caracteristiques'
    """
    files = {
        'lieux': 'lieux.csv',
        'usagers': 'usagers.csv',
        'vehicules': 'vehicules.csv',
        'charge': 'PriseEnCharge.csv',
        'caracteristiques': 'caracteristiques.csv'
    }
    
    data = {}
    for key, filename in files.items():
        try:
            data[key] = pd.read_csv(f"{data_path}/{filename}", delimiter=";")
        except FileNotFoundError:
            print(f" Warning: {filename} not found")
            data[key] = pd.DataFrame()
    
    return data


def clean_lieux(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie la base de données 'lieux'.
    
    Args:
        df: DataFrame 'lieux' brut
        
    Returns:
        DataFrame nettoyé
    """
    # Copie pour éviter les avertissements
    df = df.copy()
    
    # Suppression des colonnes non pertinentes
    columns_to_drop = ['prof', 'voie', 'v1', 'v2', 'nbv', 'vosp', 'lartpc', 'pr', 'pr1', 'plan']
    df = df.drop([col for col in columns_to_drop if col in df.columns], axis=1)
    
    # Correction des vitesses maximales aberrantes
    if 'vma' in df.columns:
        df.loc[df['vma'] > 130, 'vma'] = 130
        df.loc[df['vma'] < 30, 'vma'] = 30
    
    # Suppression des doublons
    df = df.drop_duplicates()
    
    return df


def clean_usagers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie la base de données 'usagers'.
    
    Args:
        df: DataFrame 'usagers' brut
        
    Returns:
        DataFrame nettoyé
    """
    df = df.copy()
    
    # Suppression des doublons
    df = df.drop_duplicates()
    
    # Gestion des valeurs manquantes critiques
    if 'Num_Acc' in df.columns:
        df = df.dropna(subset=['Num_Acc'])
    
    return df


def clean_vehicules(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie la base de données 'vehicules'.
    
    Args:
        df: DataFrame 'vehicules' brut
        
    Returns:
        DataFrame nettoyé
    """
    df = df.copy()
    
    # Suppression des doublons
    df = df.drop_duplicates()
    
    # Gestion des valeurs manquantes critiques
    if 'Num_Acc' in df.columns:
        df = df.dropna(subset=['Num_Acc'])
    
    return df


def clean_caracteristiques(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie la base de données 'caracteristiques'.
    
    Args:
        df: DataFrame 'caracteristiques' brut
        
    Returns:
        DataFrame nettoyé
    """
    df = df.copy()
    
    # Suppression des doublons
    df = df.drop_duplicates()
    
    return df


def clean_all_data(data_path: str) -> Dict[str, pd.DataFrame]:
    """
    Effectue le nettoyage complet de toutes les bases de données.
    
    Args:
        data_path: Chemin vers le dossier contenant les CSVs
        
    Returns:
        Dict avec les DataFrames nettoyés
    """
    # Chargement brut
    raw_data = load_accident_data(data_path)
    
    # Nettoyage spécifique
    cleaned = {
        'lieux': clean_lieux(raw_data['lieux']),
        'usagers': clean_usagers(raw_data['usagers']),
        'vehicules': clean_vehicules(raw_data['vehicules']),
        'charge': raw_data['charge'].drop_duplicates(),
        'caracteristiques': clean_caracteristiques(raw_data['caracteristiques'])
    }
    
    return cleaned


def get_data_quality_report(data: Dict[str, pd.DataFrame]) -> Dict:
    """
    Génère un rapport de qualité des données.
    
    Args:
        data: Dict des DataFrames nettoyés
        
    Returns:
        Dict avec statistiques de qualité
    """
    report = {}
    
    for name, df in data.items():
        if df.empty:
            report[name] = {
                'rows': 0,
                'columns': 0,
                'missing_values': {},
                'duplicates': 0
            }
            continue
            
        report[name] = {
            'rows': len(df),
            'columns': len(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicates': df.duplicated().sum(),
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
        }
    
    return report


def merge_datasets(data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Fusionne tous les datasets sur la clé 'Num_Acc'.
    
    Args:
        data: Dict des DataFrames nettoyés
        
    Returns:
        DataFrame fusionné
    """
    # Démarrer avec caracteristiques comme base
    merged = data['caracteristiques'].copy()
    
    # Fusionner progressivement
    if not data['lieux'].empty:
        merged = merged.merge(data['lieux'], on='Num_Acc', how='left')
    
    if not data['usagers'].empty:
        merged = merged.merge(data['usagers'], on='Num_Acc', how='left')
    
    if not data['vehicules'].empty:
        merged = merged.merge(data['vehicules'], on='Num_Acc', how='left')
    
    if not data['charge'].empty:
        merged = merged.merge(data['charge'], on='Num_Acc', how='left')
    
    return merged
