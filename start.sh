#!/bin/bash

# Script de démarrage rapide du projet
# Usage: bash start.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="${PROJECT_ROOT}/venv_clean"

echo "🚀 Démarrage du projet..."
echo ""

# Activer l'environnement virtuel
if [ -d "$VENV_PATH" ]; then
    echo "✅ Activation de l'environnement virtuel..."
    source "$VENV_PATH/bin/activate"
else
    echo "❌ Environnement virtuel non trouvé: $VENV_PATH"
    echo "   Création en cours..."
    python3 -m venv "$VENV_PATH"
    source "$VENV_PATH/bin/activate"
    pip install --upgrade pip setuptools wheel -q
    pip install -r requirements.txt -q
fi

echo ""
echo "=" * 80
echo "Options disponibles:"
echo "=" * 80
echo ""
echo "1️⃣  Lancer l'API FastAPI:"
echo "    uvicorn src.api.main:app --reload --port 8000"
echo ""
echo "2️⃣  Lancer le pipeline complet:"
echo "    python run_pipeline.py"
echo ""
echo "3️⃣  Lancer une étape spécifique:"
echo "    python run_pipeline.py --step data_cleaning"
echo "    python run_pipeline.py --step statistical_analysis"
echo "    python run_pipeline.py --step dimensionality_reduction"
echo "    python run_pipeline.py --step machine_learning"
echo ""
echo "4️⃣  Lancer les tests:"
echo "    pytest -v"
echo ""
echo "=" * 80
echo ""
echo "💡 Conseil: Ouvre un nouvel onglet terminal pour le développement!"
echo ""
