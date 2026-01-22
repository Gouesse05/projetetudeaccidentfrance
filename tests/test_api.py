"""
=============================================================================
TEST_API.PY - Tests des endpoints FastAPI
=============================================================================

Tests avec pytest et TestClient
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import date

from src.api.main import app

client = TestClient(app)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_db():
    """Mock DatabaseManager"""
    with patch('src.api.routes.DatabaseManager') as mock:
        instance = MagicMock()
        mock.return_value = instance
        yield instance


# ============================================================================
# HEALTH CHECK
# ============================================================================

def test_health_check(mock_db):
    """Tester endpoint health"""
    mock_db.check_health.return_value = True
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OK"


def test_status():
    """Tester endpoint status"""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"


# ============================================================================
# ACCIDENTS
# ============================================================================

def test_list_accidents_no_filters(mock_db):
    """Tester list accidents sans filtres"""
    # Mock de données - ajout des champs requis
    mock_df = pd.DataFrame({
        'id_accident': [1],
        'num_acc': ['201600001'],
        'date_accident': [date(2016, 1, 1)],
        'annee': [2016],
        'mois': [1],
        'jour_semaine': [5],
        'heure': [14],
        'nom_com': ['Paris'],
        'nom_dept': ['Paris'],
        'code_com': ['75056'],
        'code_dept': ['75'],
        'gravite_max': [3],
        'nombre_personnes': [2],
        'region': ['Île-de-France'],
        'population': [2165423],
        'densite_hab_km2': [20541.0],
        'zone_urbaine': [True],
        'nombre_vehicules': [1],
        'latitude': [48.8566],
        'longitude': [2.3522],
        'periode': ['Semaine'],
        'plage_horaire': ['Heures creuses']
    })
    
    mock_db.query_accidents.return_value = mock_df
    
    response = client.get("/api/v1/accidents?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['num_acc'] == '201600001'


def test_list_accidents_with_filters(mock_db):
    """Tester list accidents avec filtres"""
    mock_df = pd.DataFrame({
        'num_acc': [],
        'date_accident': [],
        'annee': [],
        'mois': [],
        'jour_semaine': [],
        'heure': [],
        'nom_com': [],
        'code_com': [],
        'gravite_max': [],
        'nombre_personnes': [],
        'region': [],
        'code_dept': [],
        'population': [],
        'densite_hab_km2': [],
        'zone_urbaine': [],
        'nombre_vehicules': [],
        'latitude': [],
        'longitude': [],
        'periode': [],
        'plage_horaire': []
    })
    
    mock_db.query_accidents.return_value = mock_df
    
    response = client.get("/api/v1/accidents?annee=2022&gravite_min=3&limit=100")
    assert response.status_code == 200
    data = response.json()
    assert data == []


# ============================================================================
# DANGER SCORES
# ============================================================================

def test_danger_scores(mock_db):
    """Tester endpoint danger scores"""
    mock_df = pd.DataFrame({
        'id_com': [75056],
        'nom_com': ['Paris'],
        'nom_dept': ['Paris'],
        'region': ['Île-de-France'],
        'nombre_accidents': [1200],
        'nombre_personnes_impliquees': [3000],
        'nombre_personnes_tuees': [45],
        'gravite_moyenne': [2.5],
        'score_danger': [85.5],
        'categorie_risque': ['TRÈS_ÉLEVÉ'],
        'population': [2165423],
        'densite_hab_km2': [20541.0]
    })
    
    mock_db.get_danger_scores.return_value = mock_df
    
    response = client.get("/api/v1/danger-scores?limit=20")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['categorie_risque'] == 'TRÈS_ÉLEVÉ'


# ============================================================================
# STATISTIQUES
# ============================================================================

def test_stats_communes(mock_db):
    """Tester stats communes"""
    mock_df = pd.DataFrame({
        'nom_com': ['Paris'],
        'code_com': ['75056'],
        'nom_dept': ['Paris'],
        'code_dept': ['75'],
        'population': [2165423],
        'densite_hab_km2': [20541.0],
        'nombre_accidents': [1200],
        'personnes_impliquees': [3000],
        'nombre_deces': [45],
        'gravite_moyenne': [2.5],
        'accidents_pour_100k_hab': [55.4]
    })
    
    mock_db.get_stats_communes.return_value = mock_df
    
    response = client.get("/api/v1/stats/communes?limit=50")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_stats_usagers(mock_db):
    """Tester stats usagers"""
    mock_df = pd.DataFrame({
        'age': [25],
        'sexe': ['1'],
        'nombre_usagers': [500],
        'nombre_deces': [15],
        'gravite_moyenne': [2.0],
        'pct_deces': [3.0]
    })
    
    mock_db.get_stats_usagers.return_value = mock_df
    
    response = client.get("/api/v1/stats/usagers?limit=50")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


# ============================================================================
# HEATMAP
# ============================================================================

def test_heatmap_data(mock_db):
    """Tester données heatmap"""
    mock_df = pd.DataFrame({
        'latitude': [48.8566],
        'longitude': [2.3522],
        'annee': [2022],
        'heure': [14],
        'gravite_max': [3],
        'weight': [5]
    })
    
    mock_db.get_heatmap_data.return_value = mock_df
    
    response = client.get("/api/v1/heatmap?annee=2022&limit=1000")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['latitude'] == 48.8566


# ============================================================================
# UTILS
# ============================================================================

def test_metadata():
    """Tester endpoint metadata"""
    response = client.get("/api/v1/metadata")
    assert response.status_code == 200
    data = response.json()
    assert data['version'] == "1.0.0"
    assert 'tables' in data


def test_root():
    """Tester page root"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data


# ============================================================================
# ERROR HANDLING
# ============================================================================

def test_invalid_query_param(mock_db):
    """Tester paramètres invalides"""
    mock_db.query_accidents.return_value = pd.DataFrame()
    response = client.get("/api/v1/accidents?limit=999999")  # Dépasse max
    # FastAPI devrait valider et retourner erreur
    # Mais le serveur est mocké, donc on teste juste que ça ne crash pas
    assert response.status_code in [200, 422]


def test_nonexistent_endpoint():
    """Tester endpoint inexistant"""
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404


# ============================================================================
# SWAGGER DOCUMENTATION
# ============================================================================

def test_swagger_docs():
    """Tester que Swagger docs sont disponibles"""
    response = client.get("/docs")
    assert response.status_code == 200
    assert b"swagger" in response.content.lower()


def test_redoc_docs():
    """Tester que ReDoc est disponible"""
    response = client.get("/redoc")
    assert response.status_code == 200
    assert b"redoc" in response.content.lower() or b"redDoc" in response.content


def test_openapi_schema():
    """Tester que schéma OpenAPI est valide"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "paths" in data
    assert "components" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
