#!/usr/bin/env python3
"""
Script d'exécution manuelle du pipeline d'analyse des accidents.
Pas de dépendance à Airflow ou Dagster.

Usage:
    python run_pipeline.py
    python run_pipeline.py --step data_cleaning
    python run_pipeline.py --step statistical_analysis
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
import pickle
import logging
import argparse
from typing import Optional

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ajouter le projet au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.analyses.data_cleaning import clean_all_data, get_data_quality_report
from src.analyses.statistical_analysis import (
    descriptive_statistics, correlation_analysis
)
from src.analyses.dimensionality_reduction import (
    pca_analysis, kmeans_clustering, elbow_curve
)
from src.analyses.machine_learning import (
    feature_selection, train_random_forest_classifier
)

# ============================================================================
# Configuration des chemins
# ============================================================================

DATA_DIR = project_root / "data"
MODELS_DIR = DATA_DIR / "models"
REPORTS_DIR = DATA_DIR / "reports"

# Créer les répertoires
MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# Étapes du pipeline
# ============================================================================

def step_data_cleaning() -> dict:
    """Étape 1: Charger et nettoyer les données."""
    logger.info("=" * 80)
    logger.info("ÉTAPE 1: CHARGEMENT ET NETTOYAGE DES DONNÉES")
    logger.info("=" * 80)
    
    try:
        logger.info(" Chargement des données brutes...")
        data = clean_all_data()
        logger.info(f" {len(data)} lignes chargées")
        
        logger.info(" Génération du rapport qualité...")
        quality_report = get_data_quality_report()
        
        # Sauvegarder les données nettoyées
        data_path = DATA_DIR / "cleaned_data.pkl"
        with open(data_path, 'wb') as f:
            pickle.dump(data, f)
        logger.info(f" Données sauvegardées: {data_path}")
        
        # Sauvegarder le rapport
        report_path = REPORTS_DIR / "data_quality_report.json"
        with open(report_path, 'w') as f:
            json.dump(quality_report, f, indent=2, default=str)
        logger.info(f" Rapport qualité sauvegardé: {report_path}")
        
        return {
            "status": "success",
            "data": data,
            "quality_report": quality_report,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f" Erreur lors du nettoyage: {str(e)}")
        raise


def step_statistical_analysis(data=None) -> dict:
    """Étape 2: Analyse statistique."""
    logger.info("=" * 80)
    logger.info("ÉTAPE 2: ANALYSE STATISTIQUE")
    logger.info("=" * 80)
    
    try:
        # Charger les données si nécessaire
        if data is None:
            data_path = DATA_DIR / "cleaned_data.pkl"
            if not data_path.exists():
                raise FileNotFoundError(f"Données nettoyées non trouvées: {data_path}")
            with open(data_path, 'rb') as f:
                data = pickle.load(f)
            logger.info(f" Données chargées: {len(data)} lignes")
        
        logger.info(" Statistiques descriptives...")
        desc_stats = descriptive_statistics(data)
        logger.info(f" {len(desc_stats)} colonnes analysées")
        
        logger.info(" Analyse de corrélation...")
        corr_analysis = correlation_analysis(data)
        logger.info(f" Corrélations calculées")
        
        # Sauvegarder les résultats
        report = {
            "descriptive_stats": desc_stats,
            "correlation_analysis": corr_analysis,
            "timestamp": datetime.now().isoformat()
        }
        
        report_path = REPORTS_DIR / "statistical_analysis.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f" Rapport sauvegardé: {report_path}")
        
        return {
            "status": "success",
            "report": report,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f" Erreur lors de l'analyse statistique: {str(e)}")
        raise


def step_dimensionality_reduction(data=None) -> dict:
    """Étape 3: Analyse dimensionnelle (PCA, K-Means)."""
    logger.info("=" * 80)
    logger.info("ÉTAPE 3: ANALYSE DIMENSIONNELLE")
    logger.info("=" * 80)
    
    try:
        # Charger les données si nécessaire
        if data is None:
            data_path = DATA_DIR / "cleaned_data.pkl"
            if not data_path.exists():
                raise FileNotFoundError(f"Données nettoyées non trouvées: {data_path}")
            with open(data_path, 'rb') as f:
                data = pickle.load(f)
            logger.info(f" Données chargées: {len(data)} lignes")
        
        # Sélectionner les colonnes numériques
        numeric_data = data.select_dtypes(include=['float64', 'int64'])
        logger.info(f" {len(numeric_data.columns)} colonnes numériques")
        
        logger.info(" PCA...")
        pca_result = pca_analysis(numeric_data)
        variance_explained = pca_result['explained_variance_ratio'].sum()
        logger.info(f" PCA explique {variance_explained:.2%} variance")
        
        logger.info(" K-Means clustering...")
        kmeans_result = kmeans_clustering(numeric_data, n_clusters=3)
        logger.info(f" Silhouette score: {kmeans_result['silhouette_score']:.3f}")
        
        logger.info(" Elbow curve...")
        elbow_result = elbow_curve(numeric_data, max_k=10)
        logger.info(f" Elbow calculé")
        
        # Sauvegarder les modèles
        pca_path = MODELS_DIR / "pca_model.pkl"
        with open(pca_path, 'wb') as f:
            pickle.dump(pca_result['model'], f)
        logger.info(f" Modèle PCA sauvegardé: {pca_path}")
        
        kmeans_path = MODELS_DIR / "kmeans_model.pkl"
        with open(kmeans_path, 'wb') as f:
            pickle.dump(kmeans_result['model'], f)
        logger.info(f" Modèle K-Means sauvegardé: {kmeans_path}")
        
        # Sauvegarder le rapport
        report = {
            "pca_variance_explained": float(variance_explained),
            "pca_components": len(pca_result['components']),
            "kmeans_silhouette": float(kmeans_result['silhouette_score']),
            "kmeans_clusters": int(kmeans_result['n_clusters']),
            "timestamp": datetime.now().isoformat()
        }
        
        report_path = REPORTS_DIR / "dimensionality_reduction.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f" Rapport sauvegardé: {report_path}")
        
        return {
            "status": "success",
            "report": report,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f" Erreur lors de l'analyse dimensionnelle: {str(e)}")
        raise


def step_machine_learning(data=None) -> dict:
    """Étape 4: Apprentissage automatique."""
    logger.info("=" * 80)
    logger.info("ÉTAPE 4: APPRENTISSAGE AUTOMATIQUE")
    logger.info("=" * 80)
    
    try:
        # Charger les données si nécessaire
        if data is None:
            data_path = DATA_DIR / "cleaned_data.pkl"
            if not data_path.exists():
                raise FileNotFoundError(f"Données nettoyées non trouvées: {data_path}")
            with open(data_path, 'rb') as f:
                data = pickle.load(f)
            logger.info(f" Données chargées: {len(data)} lignes")
        
        # Sélectionner les colonnes numériques
        numeric_data = data.select_dtypes(include=['float64', 'int64'])
        logger.info(f" {len(numeric_data.columns)} colonnes numériques")
        
        logger.info(" Sélection des features...")
        feature_sel_result = feature_selection(numeric_data, n_features=10)
        selected_features = feature_sel_result['selected_features']
        logger.info(f" {len(selected_features)} features sélectionnées")
        
        # Préparer les données pour le modèle
        X = numeric_data[selected_features]
        
        # Créer une cible binaire
        if len(data.columns) > 0:
            y = (numeric_data.iloc[:, 0] > numeric_data.iloc[:, 0].median()).astype(int)
            
            logger.info(" Entraînement Random Forest...")
            rf_result = train_random_forest_classifier(
                X, y,
                n_estimators=100,
                test_size=0.2,
                random_state=42
            )
            
            accuracy = rf_result['accuracy']
            logger.info(f" Accuracy: {accuracy:.3f}")
            
            # Sauvegarder le modèle
            rf_path = MODELS_DIR / "random_forest_model.pkl"
            with open(rf_path, 'wb') as f:
                pickle.dump(rf_result['model'], f)
            logger.info(f" Modèle RF sauvegardé: {rf_path}")
        
        # Sauvegarder le rapport
        report = {
            "features_selected": len(selected_features),
            "selected_features_list": selected_features[:5] + (['...'] if len(selected_features) > 5 else []),
            "random_forest_accuracy": float(accuracy) if 'accuracy' in locals() else None,
            "timestamp": datetime.now().isoformat()
        }
        
        report_path = REPORTS_DIR / "machine_learning.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f" Rapport sauvegardé: {report_path}")
        
        return {
            "status": "success",
            "report": report,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f" Erreur lors de l'apprentissage automatique: {str(e)}")
        raise


def step_summary_report(pipeline_results: dict) -> dict:
    """Étape 5: Génération du rapport récapitulatif."""
    logger.info("=" * 80)
    logger.info("ÉTAPE 5: RAPPORT RÉCAPITULATIF")
    logger.info("=" * 80)
    
    try:
        summary = {
            "pipeline_execution": {
                "status": "completed",
                "start_time": pipeline_results.get("start_time"),
                "end_time": datetime.now().isoformat(),
                "total_steps": 5
            },
            "data_quality": pipeline_results.get("data_cleaning", {}).get("quality_report", {}),
            "statistical_analysis": pipeline_results.get("statistical_analysis", {}).get("report", {}),
            "dimensionality_reduction": pipeline_results.get("dimensionality_reduction", {}).get("report", {}),
            "machine_learning": pipeline_results.get("machine_learning", {}).get("report", {}),
        }
        
        # Sauvegarder le rapport complet
        report_path = REPORTS_DIR / "pipeline_summary.json"
        with open(report_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        logger.info(f" Rapport récapitulatif sauvegardé: {report_path}")
        
        # Afficher un résumé
        logger.info("\n" + "=" * 80)
        logger.info(" PIPELINE COMPLÉTÉ AVEC SUCCÈS")
        logger.info("=" * 80)
        logger.info(f"\n Résumé:")
        logger.info(f"  - Données: {pipeline_results.get('data_cleaning', {}).get('status')} ({len(pipeline_results.get('data_cleaning', {}).get('data', []))} lignes)")
        logger.info(f"  - Analyse statistique: {pipeline_results.get('statistical_analysis', {}).get('status')}")
        logger.info(f"  - Analyse dimensionnelle: {pipeline_results.get('dimensionality_reduction', {}).get('status')}")
        logger.info(f"  - ML: {pipeline_results.get('machine_learning', {}).get('status')}")
        logger.info(f"\n Fichiers sauvegardés:")
        logger.info(f"  - Modèles: {MODELS_DIR}")
        logger.info(f"  - Rapports: {REPORTS_DIR}")
        
        return summary
        
    except Exception as e:
        logger.error(f" Erreur lors de la génération du rapport: {str(e)}")
        raise


# ============================================================================
# Exécution
# ============================================================================

def run_full_pipeline():
    """Exécute le pipeline complet."""
    logger.info("\n" + " " * 20)
    logger.info("DÉMARRAGE DU PIPELINE D'ANALYSE DES ACCIDENTS")
    logger.info(" " * 20 + "\n")
    
    pipeline_results = {
        "start_time": datetime.now().isoformat()
    }
    
    try:
        # Étape 1
        logger.info("\n[1/5] Nettoyage des données...\n")
        pipeline_results["data_cleaning"] = step_data_cleaning()
        
        # Étape 2
        logger.info("\n[2/5] Analyse statistique...\n")
        pipeline_results["statistical_analysis"] = step_statistical_analysis(
            pipeline_results["data_cleaning"]["data"]
        )
        
        # Étape 3
        logger.info("\n[3/5] Analyse dimensionnelle...\n")
        pipeline_results["dimensionality_reduction"] = step_dimensionality_reduction(
            pipeline_results["data_cleaning"]["data"]
        )
        
        # Étape 4
        logger.info("\n[4/5] Apprentissage automatique...\n")
        pipeline_results["machine_learning"] = step_machine_learning(
            pipeline_results["data_cleaning"]["data"]
        )
        
        # Étape 5
        logger.info("\n[5/5] Rapport récapitulatif...\n")
        step_summary_report(pipeline_results)
        
    except Exception as e:
        logger.error(f"\n ERREUR FATALE: {str(e)}")
        sys.exit(1)


def run_single_step(step_name: str):
    """Exécute une étape unique du pipeline."""
    steps = {
        "data_cleaning": step_data_cleaning,
        "statistical_analysis": step_statistical_analysis,
        "dimensionality_reduction": step_dimensionality_reduction,
        "machine_learning": step_machine_learning,
    }
    
    if step_name not in steps:
        logger.error(f" Étape inconnue: {step_name}")
        logger.error(f"Étapes disponibles: {', '.join(steps.keys())}")
        sys.exit(1)
    
    logger.info(f"\n Exécution de l'étape: {step_name}\n")
    
    try:
        result = steps[step_name]()
        logger.info(f"\n Étape {step_name} complétée")
        return result
    except Exception as e:
        logger.error(f"\n Erreur: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pipeline d'analyse des accidents - Exécution manuelle"
    )
    parser.add_argument(
        "--step",
        type=str,
        choices=["data_cleaning", "statistical_analysis", "dimensionality_reduction", "machine_learning"],
        help="Exécuter une étape spécifique (par défaut: pipeline complet)"
    )
    
    args = parser.parse_args()
    
    if args.step:
        run_single_step(args.step)
    else:
        run_full_pipeline()

