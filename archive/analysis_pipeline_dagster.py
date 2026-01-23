"""
Dagster pipeline pour l'orchestration des analyses avancées.
Exécute PCA, MCA, clustering, ML et sauvegarde les modèles.

Pipeline: accidents_analysis_pipeline
Schedule: Tous les dimanche 5h du matin
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import pickle
import json

from dagster import (
    job,
    op,
    Out,
    Field,
    String,
    In,
    DependencyDefinition,
    GraphDefinition,
    Nothing,
    resource,
    Field as ConfigField,
    DynamicOut,
    DynamicOutput,
)
from dagster._core.definitions.asset import asset
from dagster_postgres.io_manager import PostgresIOManager

# Ajouter le projet au path
project_path = str(Path(__file__).parent.parent)
if project_path not in sys.path:
    sys.path.insert(0, project_path)

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
# Configuration des répertoires
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = DATA_DIR / "models"
REPORTS_DIR = DATA_DIR / "reports"

# Créer les répertoires s'ils n'existent pas
MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# Opérations Dagster
# ============================================================================

@op(
    description="Charger et nettoyer les données d'accidents",
    config_schema={
        "data_path": ConfigField(
            String,
            default_value=str(DATA_DIR / "raw"),
            description="Chemin vers les fichiers CSV bruts"
        )
    }
)
def load_and_clean_data(context) -> dict:
    """Charge et nettoie les données d'accidents."""
    context.log.info("🔄 Chargement et nettoyage des données...")
    
    try:
        data = clean_all_data()
        quality_report = get_data_quality_report()
        
        result = {
            "data": data,
            "quality_report": quality_report,
            "status": "success"
        }
        
        context.log.info(f"✅ Données chargées: {len(data)} lignes")
        return result
        
    except Exception as e:
        context.log.error(f"❌ Erreur lors du chargement: {str(e)}")
        raise


@op(
    description="Analyse statistique des données",
    ins={"cleaned_data": In(dict)}
)
def statistical_analysis_op(context, cleaned_data: dict) -> dict:
    """Effectue l'analyse statistique."""
    context.log.info("📊 Exécution de l'analyse statistique...")
    
    try:
        data = cleaned_data["data"]
        
        # Statistiques descriptives
        desc_stats = descriptive_statistics(data)
        
        # Analyse de corrélation
        corr_analysis = correlation_analysis(data)
        
        # Sauvegarder le rapport
        report = {
            "descriptive_stats": desc_stats,
            "correlation_analysis": corr_analysis,
            "timestamp": datetime.now().isoformat()
        }
        
        report_path = REPORTS_DIR / "statistical_analysis.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        context.log.info(f"✅ Analyse statistique complète - Rapport sauvegardé: {report_path}")
        return report
        
    except Exception as e:
        context.log.error(f"❌ Erreur lors de l'analyse statistique: {str(e)}")
        raise


@op(
    description="Analyse dimensionnelle (PCA, K-Means, Elbow)",
    ins={"cleaned_data": In(dict)}
)
def dimensionality_analysis_op(context, cleaned_data: dict) -> dict:
    """Effectue l'analyse dimensionnelle."""
    context.log.info("🔍 Exécution de l'analyse dimensionnelle...")
    
    try:
        data = cleaned_data["data"]
        
        # Sélectionner les colonnes numériques
        numeric_data = data.select_dtypes(include=['float64', 'int64'])
        
        # PCA
        pca_result = pca_analysis(numeric_data)
        context.log.info(f"PCA explique {pca_result['explained_variance_ratio'].sum():.2%} variance")
        
        # K-Means
        kmeans_result = kmeans_clustering(numeric_data, n_clusters=3)
        context.log.info(f"K-Means silhouette score: {kmeans_result['silhouette_score']:.3f}")
        
        # Elbow curve
        elbow_result = elbow_curve(numeric_data, max_k=10)
        
        # Sauvegarder les résultats
        results = {
            "pca": pca_result,
            "kmeans": kmeans_result,
            "elbow": elbow_result,
            "timestamp": datetime.now().isoformat()
        }
        
        # Sauvegarder les modèles
        pca_path = MODELS_DIR / "pca_model.pkl"
        kmeans_path = MODELS_DIR / "kmeans_model.pkl"
        
        with open(pca_path, 'wb') as f:
            pickle.dump(pca_result['model'], f)
        
        with open(kmeans_path, 'wb') as f:
            pickle.dump(kmeans_result['model'], f)
        
        context.log.info(f"✅ Analyse dimensionnelle complète - Modèles sauvegardés")
        return results
        
    except Exception as e:
        context.log.error(f"❌ Erreur lors de l'analyse dimensionnelle: {str(e)}")
        raise


@op(
    description="Apprentissage automatique (Random Forest, feature selection)",
    ins={"cleaned_data": In(dict)}
)
def machine_learning_op(context, cleaned_data: dict) -> dict:
    """Effectue l'apprentissage automatique."""
    context.log.info("🤖 Exécution de l'apprentissage automatique...")
    
    try:
        data = cleaned_data["data"]
        
        # Feature selection
        feature_sel_result = feature_selection(data, n_features=10)
        context.log.info(f"Sélection: {len(feature_sel_result['selected_features'])} features sélectionnées")
        
        # Préparer les données
        numeric_data = data.select_dtypes(include=['float64', 'int64'])
        X = numeric_data[feature_sel_result['selected_features']]
        
        # Créer une cible (si possible)
        if len(data.columns) > 0:
            y = (data.iloc[:, 0] > data.iloc[:, 0].median()).astype(int)
            
            # Random Forest
            rf_result = train_random_forest_classifier(
                X, y,
                n_estimators=100,
                test_size=0.2
            )
            
            context.log.info(f"Random Forest accuracy: {rf_result['accuracy']:.3f}")
            
            # Sauvegarder le modèle
            rf_path = MODELS_DIR / "random_forest_model.pkl"
            with open(rf_path, 'wb') as f:
                pickle.dump(rf_result['model'], f)
        
        # Sauvegarder les résultats
        results = {
            "feature_selection": feature_sel_result,
            "random_forest": rf_result if 'rf_result' in locals() else None,
            "timestamp": datetime.now().isoformat()
        }
        
        context.log.info("✅ Apprentissage automatique complète")
        return results
        
    except Exception as e:
        context.log.error(f"❌ Erreur lors de l'apprentissage automatique: {str(e)}")
        raise


@op(
    description="Génération du rapport récapitulatif",
    ins={
        "data_loading": In(dict),
        "stats_analysis": In(dict),
        "dim_analysis": In(dict),
        "ml_analysis": In(dict)
    }
)
def generate_summary_report(
    context,
    data_loading: dict,
    stats_analysis: dict,
    dim_analysis: dict,
    ml_analysis: dict
) -> dict:
    """Génère un rapport récapitulatif."""
    context.log.info("📝 Génération du rapport récapitulatif...")
    
    try:
        summary = {
            "pipeline_execution": {
                "start_time": datetime.now().isoformat(),
                "status": "completed"
            },
            "data_quality": data_loading.get("quality_report", {}),
            "statistical_analysis": {
                "timestamp": stats_analysis.get("timestamp")
            },
            "dimensionality_reduction": {
                "pca_variance": dim_analysis.get("pca", {}).get("explained_variance_ratio", []).sum(),
                "kmeans_silhouette": dim_analysis.get("kmeans", {}).get("silhouette_score"),
                "timestamp": dim_analysis.get("timestamp")
            },
            "machine_learning": {
                "features_selected": len(ml_analysis.get("feature_selection", {}).get("selected_features", [])),
                "timestamp": ml_analysis.get("timestamp")
            }
        }
        
        # Sauvegarder le rapport complet
        report_path = REPORTS_DIR / "pipeline_summary.json"
        with open(report_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        context.log.info(f"✅ Rapport sauvegardé: {report_path}")
        return summary
        
    except Exception as e:
        context.log.error(f"❌ Erreur lors de la génération du rapport: {str(e)}")
        raise


# ============================================================================
# Pipeline Dagster (Job)
# ============================================================================

@job(
    description="Pipeline complet d'analyse des accidents"
)
def accidents_analysis_pipeline():
    """Pipeline complet d'orchestration des analyses."""
    
    # Étape 1: Chargement et nettoyage
    data_loading = load_and_clean_data()
    
    # Étape 2: Analyses parallèles
    stats_analysis = statistical_analysis_op(data_loading)
    dim_analysis = dimensionality_analysis_op(data_loading)
    ml_analysis = machine_learning_op(data_loading)
    
    # Étape 3: Rapport récapitulatif
    summary = generate_summary_report(
        data_loading=data_loading,
        stats_analysis=stats_analysis,
        dim_analysis=dim_analysis,
        ml_analysis=ml_analysis
    )
    
    return summary


# ============================================================================
# Configuration et exécution
# ============================================================================

if __name__ == "__main__":
    # Exécution locale
    from dagster import execute_job
    
    result = execute_job(accidents_analysis_pipeline)
    print("\n" + "="*80)
    print("Pipeline exécution complète!")
    print("="*80)
