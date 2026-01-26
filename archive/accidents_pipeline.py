"""
DAG Airflow pour orchestrer le pipeline ETL Accidents Routiers
Phase 1: Téléchargement, nettoyage, chargement données
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.decorators import apply_defaults
import sys
import os

# Ajouter le path du projet
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Importer les fonctions ETL
from src.pipeline.download_data import main as download_data
from src.pipeline.clean_data import main as clean_data
from src.database.load_postgresql import main as load_postgresql


# ============================================================================
# Configuration par défaut de la DAG
# ============================================================================

default_args = {
    'owner': 'data-engineer',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 1, 1),
    'email': ['admin@accidents.local'],
    'email_on_failure': False,
    'email_on_retry': False,
}

# ============================================================================
# Définition de la DAG
# ============================================================================

dag = DAG(
    dag_id='accidents_etl_pipeline',
    default_args=default_args,
    description='Pipeline ETL complet: Télécharger → Nettoyer → Charger données accidents',
    schedule_interval='0 3 * * 1',  # Lundi 3h du matin (cron)
    catchup=False,
    tags=['accidents', 'etl', 'production'],
    doc_md=__doc__,
)


# ============================================================================
# TÂCHES PYTHON - Étapes ETL
# ============================================================================

def task_download_data(**context):
    """
    Télécharger les données depuis data.gouv.fr
    Télécharge les fichiers CSV dans data/raw/
    """
    print(" Démarrage téléchargement données...")
    try:
        download_data()
        print(" Téléchargement réussi")
        return {'status': 'success', 'stage': 'download'}
    except Exception as e:
        print(f" Erreur téléchargement: {str(e)}")
        raise


def task_clean_data(**context):
    """
    Nettoyer et normaliser les données
    Traite les fichiers CSV et les exporte en données propres
    """
    print(" Démarrage nettoyage données...")
    try:
        clean_data()
        print(" Nettoyage réussi")
        return {'status': 'success', 'stage': 'clean'}
    except Exception as e:
        print(f" Erreur nettoyage: {str(e)}")
        raise


def task_load_postgresql(**context):
    """
    Charger les données nettoyées dans PostgreSQL
    Crée les tables et insère les données
    """
    print(" Démarrage chargement PostgreSQL...")
    try:
        load_postgresql()
        print(" Chargement réussi")
        return {'status': 'success', 'stage': 'load'}
    except Exception as e:
        print(f" Erreur chargement: {str(e)}")
        raise


def task_validate_data(**context):
    """
    Valider que les données sont correctement chargées
    Vérifier les counts et la qualité
    """
    import psycopg2
    from src.config import DB_CONFIG
    
    print("  Validation des données...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Requêtes de validation
        cursor.execute("SELECT COUNT(*) FROM accidents;")
        count_accidents = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM usagers;")
        count_usagers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM vehicules;")
        count_vehicules = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        results = {
            'accidents': count_accidents,
            'usagers': count_usagers,
            'vehicules': count_vehicules,
        }
        
        print(f" Statistiques:")
        print(f"   Accidents: {count_accidents:,}")
        print(f"   Usagers: {count_usagers:,}")
        print(f"   Véhicules: {count_vehicules:,}")
        
        if count_accidents > 0 and count_usagers > 0 and count_vehicules > 0:
            print(" Validation réussie")
            return results
        else:
            raise ValueError("Données insuffisantes après chargement")
            
    except Exception as e:
        print(f" Erreur validation: {str(e)}")
        raise


# ============================================================================
# TÂCHES BASH - Tâches système
# ============================================================================

task_start = BashOperator(
    task_id='start_pipeline',
    bash_command='echo " Démarrage du pipeline ETL à $(date)"',
    dag=dag,
)

task_verify_dirs = BashOperator(
    task_id='verify_directories',
    bash_command='''
    echo "Vérification des répertoires..."
    [ -d "/home/sdd/projetetudeapi/data/raw" ] && echo " data/raw existe" || mkdir -p /home/sdd/projetetudeapi/data/raw
    [ -d "/home/sdd/projetetudeapi/data/clean" ] && echo " data/clean existe" || mkdir -p /home/sdd/projetetudeapi/data/clean
    ls -lh /home/sdd/projetetudeapi/data/
    ''',
    dag=dag,
)

task_cleanup_temp = BashOperator(
    task_id='cleanup_temp_files',
    bash_command='find /tmp -name "accidents*" -type f -mtime +7 -delete 2>/dev/null || true',
    dag=dag,
)

task_end = BashOperator(
    task_id='end_pipeline',
    bash_command='echo " Pipeline terminé à $(date)"',
    dag=dag,
)


# ============================================================================
# OPÉRATEURS PYTHON - Tâches ETL
# ============================================================================

download_op = PythonOperator(
    task_id='download_data',
    python_callable=task_download_data,
    provide_context=True,
    dag=dag,
)

clean_op = PythonOperator(
    task_id='clean_data',
    python_callable=task_clean_data,
    provide_context=True,
    dag=dag,
)

load_op = PythonOperator(
    task_id='load_postgresql',
    python_callable=task_load_postgresql,
    provide_context=True,
    dag=dag,
)

validate_op = PythonOperator(
    task_id='validate_data',
    python_callable=task_validate_data,
    provide_context=True,
    dag=dag,
)


# ============================================================================
# DÉPENDANCES - Ordre d'exécution
# ============================================================================

# Flux principal
task_start >> task_verify_dirs >> download_op >> clean_op >> load_op >> validate_op >> task_cleanup_temp >> task_end

# Ordre:
# 1. Démarrer
# 2. Vérifier répertoires
# 3. Télécharger données (data.gouv.fr → data/raw/)
# 4. Nettoyer données (data/raw/ → data/clean/)
# 5. Charger dans PostgreSQL (data/clean/ → PostgreSQL)
# 6. Valider les données chargées
# 7. Nettoyer fichiers temporaires
# 8. Terminer

if __name__ == "__main__":
    print("DAG 'accidents_etl_pipeline' définie avec succès!")
    print("Utilise: airflow dags list")
    print("Ou: airflow dags test accidents_etl_pipeline 2024-01-01")
