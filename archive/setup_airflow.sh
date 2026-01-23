#!/bin/bash

# Script de setup automatique Airflow
# Utilisation: bash scripts/setup_airflow.sh

set -e  # Arrêter en cas d'erreur

echo "🚀 Setup Airflow pour Accidents Routiers"
echo "========================================"

# Vérifier que le venv est activé
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "❌ Erreur: Venv non activé!"
    echo "Utilise: source venv/bin/activate"
    exit 1
fi

# Définir AIRFLOW_HOME
export AIRFLOW_HOME=/home/sdd/projetetudeapi/airflow_home
export PYTHONPATH=/home/sdd/projetetudeapi:$PYTHONPATH

echo "✓ AIRFLOW_HOME: $AIRFLOW_HOME"
echo "✓ PYTHONPATH: $PYTHONPATH"

# Créer les répertoires
echo ""
echo "📁 Création des répertoires..."
mkdir -p $AIRFLOW_HOME/logs
mkdir -p $AIRFLOW_HOME/plugins
mkdir -p /home/sdd/projetetudeapi/dags
mkdir -p /home/sdd/projetetudeapi/backups

echo "✓ Répertoires créés"

# Installer les dépendances
echo ""
echo "📦 Installation des dépendances..."
pip install apache-airflow==2.7.3 apache-airflow-providers-postgres==5.10.0 -q

echo "✓ Dépendances installées"

# Initialiser Airflow
echo ""
echo "🔧 Initialisation Airflow..."
airflow db init

echo "✓ Base de données initialisée"

# Créer l'utilisateur admin
echo ""
echo "👤 Création utilisateur admin..."

# Vérifier si l'utilisateur existe déjà
if airflow users list | grep -q "admin"; then
    echo "⚠️  Utilisateur admin existe déjà"
else
    airflow users create \
      --username admin \
      --firstname Admin \
      --lastname Airflow \
      --role Admin \
      --email admin@accidents.local \
      --password admin123
    
    echo "✓ Utilisateur admin créé"
    echo "  Identifiant: admin"
    echo "  Mot de passe: admin123"
fi

# Vérifier les DAGs
echo ""
echo "✓ DAGs disponibles:"
airflow dags list

echo ""
echo "✅ Setup Airflow terminé!"
echo ""
echo "Prochaines étapes:"
echo "1. Terminal 1: airflow webserver --port 8080"
echo "2. Terminal 2: airflow scheduler"
echo "3. Ouvrir: http://localhost:8080"
echo "   Identifiant: admin"
echo "   Mot de passe: admin123"
echo ""
echo "Teste une DAG:"
echo "  airflow dags test accidents_etl_pipeline 2024-01-01"
