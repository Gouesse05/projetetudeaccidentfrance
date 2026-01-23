#!/bin/bash

# Streamlit Dashboard Launcher
# Accidents Routiers Analysis Dashboard

source venv_clean/bin/activate

echo "🚀 Lancement du dashboard Streamlit..."
echo "📍 Accès: http://localhost:8501"
echo ""

streamlit run streamlit_app.py --logger.level=warning
