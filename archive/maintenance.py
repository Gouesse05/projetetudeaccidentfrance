"""
DAG Airflow pour maintenance et monitoring
Phase 5b: Santé du système, backups, monitoring
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.filesystem import FileSensor
import os
import psycopg2


# ============================================================================
# Configuration par défaut
# ============================================================================

default_args = {
    'owner': 'devops',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
}

dag = DAG(
    dag_id='accidents_maintenance',
    default_args=default_args,
    description='Maintenance, monitoring et backups du pipeline',
    schedule_interval='0 1 * * *',  # Chaque jour à 1h du matin
    catchup=False,
    tags=['maintenance', 'monitoring'],
)


# ============================================================================
# TÂCHES DE MONITORING
# ============================================================================

def check_database_health(**context):
    """Vérifier la santé de la base de données"""
    from src.config import DB_CONFIG
    
    print("🏥 Vérification santé base de données...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Requêtes de santé
        checks = {
            'database_connection': '✅',
            'accidents_table': None,
            'usagers_table': None,
            'vehicules_table': None,
        }
        
        try:
            cursor.execute("SELECT COUNT(*) FROM accidents;")
            checks['accidents_table'] = '✅'
        except:
            checks['accidents_table'] = '❌'
        
        try:
            cursor.execute("SELECT COUNT(*) FROM usagers;")
            checks['usagers_table'] = '✅'
        except:
            checks['usagers_table'] = '❌'
        
        try:
            cursor.execute("SELECT COUNT(*) FROM vehicules;")
            checks['vehicules_table'] = '✅'
        except:
            checks['vehicules_table'] = '❌'
        
        cursor.close()
        conn.close()
        
        print("\n📋 Résultats santé:")
        for check, status in checks.items():
            print(f"   {check}: {status}")
        
        return checks
        
    except Exception as e:
        print(f"❌ Erreur santé base: {str(e)}")
        raise


def check_disk_space(**context):
    """Vérifier l'espace disque"""
    import shutil
    
    print("💾 Vérification espace disque...")
    project_path = '/home/sdd/projetetudeapi'
    
    usage = shutil.disk_usage(project_path)
    percent_used = (usage.used / usage.total) * 100
    
    print(f"   Utilisé: {usage.used / (1024**3):.2f} GB")
    print(f"   Total: {usage.total / (1024**3):.2f} GB")
    print(f"   Pourcentage: {percent_used:.1f}%")
    
    if percent_used > 90:
        print("⚠️  ALERTE: Plus de 90% du disque utilisé!")
        raise Exception("Espace disque insuffisant")
    
    return {'percent_used': percent_used, 'status': 'ok'}


def backup_database(**context):
    """Sauvegarder la base de données PostgreSQL"""
    import subprocess
    from src.config import DB_CONFIG
    
    print("📦 Backup base de données...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"/home/sdd/projetetudeapi/backups/accidents_db_{timestamp}.sql"
    
    try:
        os.makedirs('/home/sdd/projetetudeapi/backups', exist_ok=True)
        
        cmd = [
            'pg_dump',
            '-h', DB_CONFIG.get('host', 'localhost'),
            '-U', DB_CONFIG.get('user', 'postgres'),
            '-d', DB_CONFIG.get('database', 'accidents'),
            '-f', backup_file
        ]
        
        # Ajouter mot de passe si présent
        env = os.environ.copy()
        if 'password' in DB_CONFIG:
            env['PGPASSWORD'] = DB_CONFIG['password']
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            file_size = os.path.getsize(backup_file) / (1024**2)  # en MB
            print(f"✅ Backup créé: {backup_file} ({file_size:.2f} MB)")
            return {'file': backup_file, 'size_mb': file_size}
        else:
            print(f"❌ Erreur backup: {result.stderr}")
            raise Exception(f"Erreur pg_dump: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Erreur backup: {str(e)}")
        raise


def cleanup_old_backups(**context):
    """Supprimer les backups de plus de 30 jours"""
    import glob
    
    print("🗑️  Nettoyage anciens backups...")
    backup_dir = '/home/sdd/projetetudeapi/backups'
    
    if not os.path.exists(backup_dir):
        print("   Aucun répertoire backups")
        return
    
    threshold = datetime.now() - timedelta(days=30)
    deleted = 0
    
    for backup_file in glob.glob(f"{backup_dir}/*.sql"):
        file_time = datetime.fromtimestamp(os.path.getmtime(backup_file))
        if file_time < threshold:
            os.remove(backup_file)
            deleted += 1
            print(f"   Supprimé: {os.path.basename(backup_file)}")
    
    print(f"✅ {deleted} anciens backups supprimés")
    return {'deleted': deleted}


# ============================================================================
# OPÉRATEURS
# ============================================================================

health_check = PythonOperator(
    task_id='check_database_health',
    python_callable=check_database_health,
    dag=dag,
)

disk_check = PythonOperator(
    task_id='check_disk_space',
    python_callable=check_disk_space,
    dag=dag,
)

backup_task = PythonOperator(
    task_id='backup_database',
    python_callable=backup_database,
    dag=dag,
)

cleanup_task = PythonOperator(
    task_id='cleanup_old_backups',
    python_callable=cleanup_old_backups,
    dag=dag,
)

report = BashOperator(
    task_id='generate_report',
    bash_command='echo "Rapport maintenance généré à $(date)" > /tmp/maintenance_report.txt',
    dag=dag,
)


# ============================================================================
# DÉPENDANCES
# ============================================================================

[health_check, disk_check] >> backup_task >> cleanup_task >> report

if __name__ == "__main__":
    print("DAG 'accidents_maintenance' définie!")
