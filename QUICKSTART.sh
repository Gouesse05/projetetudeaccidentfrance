#!/bin/bash
# 🚀 QUICKSTART - Phase 5 Analyses Avancées
# Démarrage rapide en 5 étapes

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         🚀 PHASE 5 - ANALYSES AVANCÉES - QUICKSTART            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

# ============================================================================
# STEP 1: Vérifier venv
# ============================================================================
echo -e "${YELLOW}Step 1/5: Vérifier Python Virtual Environment${NC}"

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  venv non trouvé. Création...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate
echo -e "${GREEN}✅ venv activé${NC}\n"

# ============================================================================
# STEP 2: Installer dépendances
# ============================================================================
echo -e "${YELLOW}Step 2/5: Installer dépendances requirements.txt${NC}"
pip install -q -r requirements.txt
echo -e "${GREEN}✅ Dépendances installées${NC}\n"

# ============================================================================
# STEP 3: Vérifier imports
# ============================================================================
echo -e "${YELLOW}Step 3/5: Vérifier imports critiques${NC}"

python3 << 'PYTHON_CHECK'
try:
    import pandas as pd
    import numpy as np
    import scipy
    import sklearn
    import statsmodels
    print("  ✅ Core packages OK")
except ImportError as e:
    print(f"  ❌ Error: {e}")
    exit(1)

try:
    import prince
    print("  ✅ prince (MCA/CA) OK")
except ImportError:
    print("  ⚠️  prince not installed (MCA endpoint will fail)")

try:
    import h2o
    print("  ✅ h2o (H2O ML) OK")
except ImportError:
    print("  ⚠️  h2o not installed (H2O endpoints will fail)")
PYTHON_CHECK

echo ""

# ============================================================================
# STEP 4: Démarrer l'API
# ============================================================================
echo -e "${YELLOW}Step 4/5: Démarrer l'API FastAPI${NC}"
echo -e "${BLUE}Command:${NC} uvicorn src.api.main:app --reload --port 8000"
echo ""
echo -e "${GREEN}API démarrée!${NC}"
echo -e "${BLUE}Documentation:${NC}"
echo "  - Swagger UI: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"
echo "  - Health check: http://localhost:8000/api/v1/analyses/health"
echo ""

# ============================================================================
# STEP 5: Prochaines étapes
# ============================================================================
echo -e "${YELLOW}Step 5/5: Prochaines étapes${NC}"
echo -e "${GREEN}Dans un autre terminal:${NC}"
echo ""
echo "1️⃣  Tester les endpoints:"
echo "   curl http://localhost:8000/api/v1/analyses/health"
echo ""
echo "2️⃣  Lancer les tests endpoints:"
echo "   bash scripts/test_analyses.sh"
echo ""
echo "3️⃣  Déployer Airflow (optionnel):"
echo "   bash scripts/setup_airflow.sh"
echo ""
echo "4️⃣  Documentation complète:"
echo "   - docs/ANALYSIS_ENDPOINTS.md      (Guide endpoints)"
echo "   - PHASE5_COMPLETE.md               (Résumé complet)"
echo "   - PHASE5_ANALYSES.md               (Vue d'ensemble)"
echo "   - CHANGELOG_PHASE5.md              (Tous les changements)"
echo ""

# ============================================================================
# Lancer l'API
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Lancement de l'API...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

uvicorn src.api.main:app --reload --port 8000
