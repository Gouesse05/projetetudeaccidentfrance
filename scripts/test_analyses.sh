#!/bin/bash
# Test quickstart pour les endpoints d'analyse
# Usage: bash scripts/test_analyses.sh

set -e

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

API_URL="http://localhost:8000"
TEST_FILE="/home/sdd/projetetudeapi/data/clean/accidents_sample.csv"

echo -e "${BLUE}=== Tests Endpoints Analyse ===${NC}\n"

# Vérifier si l'API est running
echo -e "${YELLOW}1. Vérification API...${NC}"
if ! curl -s http://localhost:8000/api/v1/analyses/health > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  API non accessible. Lancer: uvicorn src.api.main:app --reload${NC}"
    exit 1
fi
echo -e "${GREEN}✅ API disponible${NC}\n"

# Health check
echo -e "${YELLOW}2. Health Check...${NC}"
curl -s $API_URL/api/v1/analyses/health | python -m json.tool
echo -e "${GREEN}✅${NC}\n"

# Créer un fichier de test si absent
if [ ! -f "$TEST_FILE" ]; then
    echo -e "${YELLOW}⚠️  Fichier test non trouvé: $TEST_FILE${NC}"
    echo "Créez un CSV de test dans data/clean/ ou téléchargez depuis data.gouv.fr"
    exit 1
fi

echo -e "${YELLOW}3. Data Quality Check...${NC}"
curl -s -F "file=@$TEST_FILE" $API_URL/api/v1/analyses/data-quality | python -m json.tool | head -20
echo -e "${GREEN}✅${NC}\n"

echo -e "${YELLOW}4. Correlation Analysis...${NC}"
curl -s -F "file=@$TEST_FILE" $API_URL/api/v1/analyses/correlation | python -m json.tool | head -20
echo -e "${GREEN}✅${NC}\n"

echo -e "${YELLOW}5. Descriptive Statistics...${NC}"
curl -s -F "file=@$TEST_FILE" $API_URL/api/v1/analyses/descriptive-statistics | python -m json.tool | head -20
echo -e "${GREEN}✅${NC}\n"

echo -e "${YELLOW}6. PCA (n_components=2)...${NC}"
curl -s -F "file=@$TEST_FILE" "$API_URL/api/v1/analyses/pca?n_components=2" | python -m json.tool
echo -e "${GREEN}✅${NC}\n"

echo -e "${YELLOW}7. Elbow Curve (K-Means)...${NC}"
curl -s -F "file=@$TEST_FILE" "$API_URL/api/v1/analyses/elbow-curve?max_clusters=10" | python -m json.tool
echo -e "${GREEN}✅${NC}\n"

echo -e "${YELLOW}8. K-Means Clustering (n_clusters=3)...${NC}"
curl -s -F "file=@$TEST_FILE" "$API_URL/api/v1/analyses/kmeans?n_clusters=3" | python -m json.tool
echo -e "${GREEN}✅${NC}\n"

echo -e "${BLUE}=== Tous les tests complétés! ===${NC}"
echo -e "${GREEN}Pour plus d'endpoints, voir docs/ANALYSIS_ENDPOINTS.md${NC}"
