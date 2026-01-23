"""
Airflow DAG pour l'orchestration des analyses avancées.
Exécute PCA, MCA, clustering, ML et sauvegarde les modèles.

DAG: accidents_analysis_pipeline
Schedule: Tous les dimanche 5h du matin
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import sys
import os
from pathlib import Path

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
# Configuration du DAG
# ============================================================================

default_args = {
    'owner': 'accidents_team',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}

dag = DAG(
    'accidents_analysis_pipeline',
    default_args=default_args,
    description='Orchestration des analyses avancées (PCA, MCA, ML, clustering)',
    schedule_interval='0 5 * * 0',  # Dimanche 5h du matin
    start_date=days_ago(1),
    catchup=False,
    tags=['analysis', 'machine-learning', 'data-science'],
)

# ============================================================================
# Configuration des chemins
# ============================================================================

DATA_PATH = os.path.join(project_path, 'data', 'clean')
MODELS_PATH = os.path.join(project_path, 'data', 'models')
REPORTS_PATH = os.path.join(project_path, 'data', 'reports')

# Créer les répertoires s'ils n'existent pas
os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(MODELS_PATH, exist_ok=True)
os.makedirs(REPORTS_PATH, exist_ok=True)


# ============================================================================
# Task Functions
# ============================================================================

def task_load_and_clean_data():
    """Charge et nettoie tous les datasets"""
    print("📊 Chargement et nettoyage des données d'accidents...")
    
    try:
        data = clean_all_data(DATA_PATH)
        quality_report = get_data_quality_report(data)
        
        # Sauvegarder le rapport
        import json
        report_path = os.path.join(REPORTS_PATH, f'data_quality_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(report_path, 'w') as f:
            json.dump(quality_report, f, indent=2)
        
        print(f"✅ Données nettoyées et validées")
        print(f"📁 Rapport sauvegardé: {report_path}")
        
        return {'status': 'success', 'report': report_path}
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        raise


def task_statistical_analysis():
    """Effectue les analyses statistiques descriptives"""
    print("📈 Analyses statistiques descriptives...")
    
    try:
        import pandas as pd
        
        # Charger les données nettoyées
        merged_df = None
        for file in os.listdir(DATA_PATH):
            if file.endswith('.csv'):
                merged_df = pd.read_csv(os.path.join(DATA_PATH, file), delimiter=";")
                break
        
        if merged_df is None:
            raise FileNotFoundError("Aucun fichier CSV trouvé dans data/clean")
        
        # Statistiques descriptives
        stats = descriptive_statistics(merged_df)
        
        # Corrélations
        corr = correlation_analysis(merged_df)
        
        # Sauvegarder
        report = {
            'timestamp': datetime.now().isoformat(),
            'descriptive_stats_count': len(stats),
            'correlation_shape': corr.shape if hasattr(corr, 'shape') else 'N/A'
        }
        
        import json
        report_path = os.path.join(REPORTS_PATH, f'statistical_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"✅ Analyses statistiques complétées")
        print(f"📁 Rapport: {report_path}")
        
        return {'status': 'success', 'report': report_path}
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        raise


def task_pca_analysis():
    """Effectue l'analyse PCA"""
    print("🔍 Analyse en Composantes Principales (PCA)...")
    
    try:
        import pandas as pd
        import pickle
        
        # Charger les données
        merged_df = None
        for file in os.listdir(DATA_PATH):
            if file.endswith('.csv'):
                merged_df = pd.read_csv(os.path.join(DATA_PATH, file), delimiter=";")
                break
        
        if merged_df is None:
            raise FileNotFoundError("Aucun fichier CSV trouvé")
        
        # PCA avec 5 composantes
        pca_result = pca_analysis(merged_df, n_components=5)
        
        # Sauvegarder le modèle
        model_path = os.path.join(MODELS_PATH, f'pca_model_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': pca_result['model'],
                'scaler': pca_result['scaler'],
                'loadings': pca_result['loadings']
            }, f)
        
        # Rapport
        report = {
            'timestamp': datetime.now().isoformat(),
            'n_components': 5,
            'explained_variance_ratio': pca_result['explained_variance_ratio'],
            'cumulative_variance': pca_result['cumulative_variance'],
            'model_path': model_path
        }
        
        report_path = os.path.join(REPORTS_PATH, f'pca_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        import json
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ PCA complétée ({pca_result['explained_variance_ratio'][0]:.2%} variance expliquée)")
        print(f"📁 Modèle: {model_path}")
        
        return {'status': 'success', 'model_path': model_path}
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        raise


def task_clustering_analysis():
    """Effectue l'analyse de clustering"""
    print("🎯 Analyse de Clustering (K-Means)...")
    
    try:
        import pandas as pd
        import pickle
        
        # Charger les données
        merged_df = None
        for file in os.listdir(DATA_PATH):
            if file.endswith('.csv'):
                merged_df = pd.read_csv(os.path.join(DATA_PATH, file), delimiter=";")
                break
        
        if merged_df is None:
            raise FileNotFoundError("Aucun fichier CSV trouvé")
        
        # Courbe du coude pour déterminer le nombre optimal de clusters
        elbow = elbow_curve(merged_df, max_clusters=10)
        
        # Clustering K-Means avec 4 clusters
        kmeans_result = kmeans_clustering(merged_df, n_clusters=4)
        
        # Sauvegarder le modèle
        model_path = os.path.join(MODELS_PATH, f'kmeans_model_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': kmeans_result['model'],
                'scaler': kmeans_result['scaler'],
                'labels': kmeans_result['cluster_labels']
            }, f)
        
        # Rapport
        report = {
            'timestamp': datetime.now().isoformat(),
            'n_clusters': 4,
            'inertia': kmeans_result['inertia'],
            'silhouette_score': kmeans_result.get('silhouette', None),
            'elbow_inertias': elbow['inertias'],
            'model_path': model_path
        }
        
        report_path = os.path.join(REPORTS_PATH, f'clustering_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        import json
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Clustering complété (silhouette={kmeans_result.get('silhouette', 'N/A'):.3f})")
        print(f"📁 Modèle: {model_path}")
        
        return {'status': 'success', 'model_path': model_path}
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        raise


def task_ml_analysis():
    """Entraîne les modèles Machine Learning"""
    print("🤖 Entraînement des modèles Machine Learning...")
    
    try:
        import pandas as pd
        import pickle
        
        # Charger les données
        merged_df = None
        for file in os.listdir(DATA_PATH):
            if file.endswith('.csv'):
                merged_df = pd.read_csv(os.path.join(DATA_PATH, file), delimiter=";")
                break
        
        if merged_df is None:
            raise FileNotFoundError("Aucun fichier CSV trouvé")
        
        # Sélectionner les colonnes numériques
        numeric_cols = merged_df.select_dtypes(include=['number']).columns.tolist()
        
        if len(numeric_cols) < 2:
            raise ValueError("Pas assez de colonnes numériques")
        
        # Feature selection
        if len(numeric_cols) > 3:
            target_col = numeric_cols[0]
            feature_cols = numeric_cols[1:]
            
            feature_result = feature_selection(merged_df, feature_cols, target_col)
            
            # Sauvegarder
            report_path = os.path.join(REPORTS_PATH, f'feature_selection_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            import json
            with open(report_path, 'w') as f:
                json.dump(feature_result, f, indent=2)
            
            print(f"✅ Feature Selection complétée")
            print(f"📁 Rapport: {report_path}")
        else:
            print("⚠️  Pas assez de features pour ML")
        
        return {'status': 'success'}
    except Exception as e:
        print(f"⚠️  Erreur ML (non-bloquante): {str(e)}")
        return {'status': 'skipped', 'reason': str(e)}


def task_generate_summary_report():
    """Génère un rapport de synthèse"""
    print("📋 Génération du rapport de synthèse...")
    
    try:
        # Lister tous les rapports générés
        reports = os.listdir(REPORTS_PATH)
        reports = [f for f in reports if f.endswith('.json')]
        
        # Créer une synthèse
        summary = {
            'timestamp': datetime.now().isoformat(),
            'pipeline': 'accidents_analysis_pipeline',
            'reports_generated': len(reports),
            'reports': reports,
            'data_path': DATA_PATH,
            'models_path': MODELS_PATH,
            'reports_path': REPORTS_PATH
        }
        
        summary_path = os.path.join(REPORTS_PATH, f'pipeline_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        import json
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✅ Pipeline complété avec succès!")
        print(f"📁 Synthèse: {summary_path}")
        print(f"📊 Rapports générés: {len(reports)}")
        
        return {'status': 'success', 'summary_path': summary_path}
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        raise


# ============================================================================
# Tasks Airflow
# ============================================================================

start_task = PythonOperator(
    task_id='start_analysis_pipeline',
    python_callable=lambda: print("🚀 Démarrage du pipeline d'analyse..."),
    dag=dag
)

load_clean = PythonOperator(
    task_id='load_and_clean_data',
    python_callable=task_load_and_clean_data,
    dag=dag
)

stats_task = PythonOperator(
    task_id='statistical_analysis',
    python_callable=task_statistical_analysis,
    dag=dag
)

pca_task = PythonOperator(
    task_id='pca_analysis',
    python_callable=task_pca_analysis,
    dag=dag
)

clustering_task = PythonOperator(
    task_id='clustering_analysis',
    python_callable=task_clustering_analysis,
    dag=dag
)

ml_task = PythonOperator(
    task_id='ml_analysis',
    python_callable=task_ml_analysis,
    dag=dag
)

summary_task = PythonOperator(
    task_id='generate_summary_report',
    python_callable=task_generate_summary_report,
    dag=dag
)

end_task = PythonOperator(
    task_id='end_analysis_pipeline',
    python_callable=lambda: print("✅ Pipeline d'analyse terminé!"),
    dag=dag
)

# ============================================================================
# Dépendances DAG
# ============================================================================

# Chaîne linéaire: start -> load_clean
# Puis parallèle: stats, pca, clustering, ml
# Puis: summary -> end

start_task >> load_clean
load_clean >> [stats_task, pca_task, clustering_task, ml_task]
[stats_task, pca_task, clustering_task, ml_task] >> summary_task
summary_task >> end_task
