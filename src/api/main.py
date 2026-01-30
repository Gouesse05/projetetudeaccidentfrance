"""
=============================================================================
MAIN.PY - Application FastAPI principale
=============================================================================

Point d'entrée pour serveur API
Usage:
    uvicorn src.api.main:app --reload
    uvicorn src.api.main:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any
from datetime import datetime
import os

from src.api.routes import router as api_router
from src.api.analysis_endpoints import router as analysis_router
from src.api.version_routes import router as version_router
from src.api.version import VERSION, API_VERSION, get_version_info
from src.config import API_HOST, API_PORT

# ============================================================================
# CONFIGURATION LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le cycle de vie de l'application"""
    # Startup
    logger.info(f" Starting Accidents API v{VERSION}")
    logger.info(f" API Version: {API_VERSION}")
    logger.info(f" Host: {API_HOST}, Port: {API_PORT}")
    logger.info(" Documentation: http://localhost:8000/docs")
    
    yield
    
    # Shutdown
    logger.info(f" Shutting down Accidents API v{VERSION}")


app = FastAPI(
    title="Accidents Routiers API",
    description="API pour analyse accidents routiers corporels - Data Analyst Insurance",
    version=VERSION,
    contact={
        "name": "Data Engineering Team",
        "url": "https://github.com/Gouesse05/projetetudeaccidentfrance",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# ============================================================================
# MIDDLEWARE CORS
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À adapter en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# CUSTOM OPENAPI SCHEMA
# ============================================================================

def custom_openapi() -> Dict[str, Any]:
    """Customiser documentation OpenAPI"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Accidents Routiers API",
        version=VERSION,
        description="""
#  Accidents Routiers API

API RESTful pour l'analyse des accidents corporels routiers en France.

##  Cas d'Usage

### Pour Assureurs
- **Évaluation Risque**: Scores de danger par commune/département
- **Tarification**: Statistiques par profil (âge, type véhicule, région)
- **Prévention**: Identification zones/heures à risque

### Pour Analystes
- **Explorations**: Requêtes flexibles avec filtres multiples
- **Heatmaps**: Visualisations géographiques
- **Rapports**: Exports statistiques

##  Données Disponibles

- **68,432 accidents** (2022-2024)
- **245,123 usagers** (décès, blessures, indemnes)
- **89,321 véhicules** (catégories, équipements)
- **12,234 communes** avec données INSEE

##  Authentification

Actuellement **publique**. À implémenter: JWT tokens (Phase 5)

##  Démarrage Rapide

### Installation
```bash
pip install -r requirements.txt
```

### Lancer serveur
```bash
uvicorn src.api.main:app --reload
```

### Accéder à l'API
- **Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Premier appel
```bash
curl http://localhost:8000/api/v1/health
curl "http://localhost:8000/api/v1/accidents?annee=2022&limit=10"
curl http://localhost:8000/api/v1/danger-scores?limit=20
```

##  Documentation

Chaque endpoint inclut:
- Description détaillée
- Paramètres avec contraintes
- Exemples de requêtes/réponses
- Codes HTTP possibles
        """,
        routes=app.routes,
    )
    
    openapi_schema["info"]["x-logo"] = {
        "url": "https://data.gouv.fr/static/img/home/logo-e-gouv.svg"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# ============================================================================
# MIDDLEWARE LOGGING
# ============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Logger toutes les requêtes"""
    logger.info(f"{request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        logger.info(f"→ {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Error: {e}")
        raise


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler pour exceptions non gérées"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


# ============================================================================
# LIFESPAN EVENTS
# ============================================================================

# ============================================================================
# MIDDLEWARE DE LOGGING DES REQUÊTES
# ============================================================================

app.include_router(api_router)
app.include_router(analysis_router)
app.include_router(version_router)


# ============================================================================
# ROUTES ROOT
# ============================================================================

@app.get("/", tags=["root"])
async def root():
    """Page d'accueil API"""
    version_info = get_version_info()
    return {
        "message": "Bienvenue sur Accidents Routiers API",
        "version": VERSION,
        "api_version": API_VERSION,
        "build_date": version_info["build_date"],
        "status": version_info["status"],
        "docs": "http://localhost:8000/docs",
        "version_endpoint": "/api/v1/version",
        "endpoints": [
            "/api/v1/health",
            "/api/v1/accidents",
            "/api/v1/danger-scores",
            "/api/v1/stats/communes",
            "/api/v1/heatmap",
        ]
    }


@app.get("/status", tags=["monitoring"])
async def status():
    """Status détaillé du service"""
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENV", "production"),
        "version": VERSION,
        "api_version": API_VERSION
    }


# ============================================================================
# EXEMPLE UTILISATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )

