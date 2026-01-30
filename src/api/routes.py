"""
=============================================================================
ROUTES.PY - Endpoints FastAPI
=============================================================================

Définit tous les endpoints REST pour l'API accidents
"""

from fastapi import APIRouter, Query, HTTPException, Depends, status
from typing import List, Optional
import logging
from datetime import datetime
import pandas as pd

from src.api.models import (
    AccidentEnrichi, DangerScore, StatistiquesTemporelles,
    StatistiquesCommune, StatistiquesUsager, StatistiquesVehicule,
    HeatmapPoint, AccidentProximite, Health, ErrorResponse,
    QueryAccidents, QueryHeatmap, QueryProximite, AnalyseCustom,
    ResultatAnalyse
)
from src.database import DatabaseManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["accidents"])

# Dependency pour DatabaseManager
def get_db():
    """Dependency injection pour DB"""
    db = DatabaseManager()
    try:
        yield db
    finally:
        db.close_pool()


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health", response_model=Health, tags=["monitoring"])
async def health_check(db: DatabaseManager = Depends(get_db)):
    """
    Vérifier l'état du service et de la base de données
    
    **Returns:**
    - `status`: 'OK' si tout fonctionne
    - `database`: État de la connexion DB
    """
    try:
        stats = db.validate_data_integrity()
        return Health(
            status="OK",
            database="CONNECTED",
            messages=[f"Accidents: {stats.get('accidents', 0)}", 
                     f"Communes: {stats.get('communes', 0)}"]
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return Health(
            status="ERROR",
            database="DISCONNECTED",
            messages=[str(e)]
        )


# ============================================================================
# ACCIDENTS - REQUÊTES SIMPLES
# ============================================================================

@router.get("/accidents", response_model=List[AccidentEnrichi])
async def list_accidents(
    annee: Optional[int] = Query(None, description="Année (ex: 2022)"),
    mois: Optional[int] = Query(None, ge=1, le=12, description="Mois (1-12)"),
    dept: Optional[str] = Query(None, description="Code département (ex: 75)"),
    gravite_min: Optional[int] = Query(None, ge=1, le=4, description="Gravité min"),
    limit: int = Query(100, ge=1, le=10000, description="Max résultats"),
    db: DatabaseManager = Depends(get_db)
):
    """
    Lister les accidents avec filtres optionnels
    
    **Paramètres:**
    - `annee`: Filtrer par année
    - `mois`: Filtrer par mois (1-12)
    - `dept`: Filtrer par département
    - `gravite_min`: Gravité minimale (1=Indemne, 4=Tué)
    - `limit`: Nombre max de résultats (1-10000)
    
    **Exemple:** `/accidents?annee=2022&gravite_min=3&limit=50`
    """
    try:
        df = db.query_accidents(
            annee=annee,
            mois=mois,
            dep=dept,
            gravite_min=gravite_min,
            limit=limit
        )
        
        if df.empty:
            return []
        
        # Convertir DataFrame en modèles Pydantic
        return [AccidentEnrichi(**row.to_dict()) for _, row in df.iterrows()]
    
    except Exception as e:
        logger.error(f"Error listing accidents: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération des accidents"
        )


@router.get("/accidents/{id_accident}", response_model=AccidentEnrichi)
async def get_accident_detail(
    id_accident: int,
    db: DatabaseManager = Depends(get_db)
):
    """
    Détails d'un accident spécifique
    
    **Paramètres:**
    - `id_accident`: ID interne de l'accident
    """
    try:
        query = f"""
            SELECT * FROM {db.__class__.__name__.lower().replace('databasemanager', 'accidents_schema')}.v_accidents_enrichis
            WHERE id_accident = %s
        """
        # Simplification: retourner premier résultat
        df = db.query_to_dataframe(query, (id_accident,))
        
        if df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Accident {id_accident} non trouvé"
            )
        
        return AccidentEnrichi(**df.iloc[0].to_dict())
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting accident detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accidents/commune/{code_com}", response_model=List[AccidentEnrichi])
async def accidents_by_commune(
    code_com: str,
    limit: int = Query(100, ge=1, le=1000),
    db: DatabaseManager = Depends(get_db)
):
    """
    Tous les accidents d'une commune
    
    **Paramètres:**
    - `code_com`: Code INSEE commune (ex: 75056)
    - `limit`: Max résultats
    """
    try:
        df = db.get_accidents_by_commune(code_com=code_com, limit=limit)
        
        if df.empty:
            return []
        
        return [AccidentEnrichi(**row.to_dict()) for _, row in df.iterrows()]
    
    except Exception as e:
        logger.error(f"Error getting accidents by commune: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DANGER SCORES - ANALYSE DE RISQUE
# ============================================================================

@router.get("/danger-scores", response_model=List[DangerScore])
async def list_danger_scores(
    limit: int = Query(50, ge=1, le=500, description="Top N communes"),
    db: DatabaseManager = Depends(get_db)
):
    """
    Top communes par score de danger composite
    
    **Score = (Fréquence × 50%) + (Gravité × 30%) + (Personnes × 20%)**
    
    **Paramètres:**
    - `limit`: Nombre de communes à retourner
    
    **Catégories de risque:**
    - `TRÈS_ÉLEVÉ`: Score > 70
    - `ÉLEVÉ`: Score 50-70
    - `MOYEN`: Score 25-50
    - `FAIBLE`: Score < 25
    """
    try:
        df = db.get_danger_scores(limit=limit)
        
        if df.empty:
            return []
        
        return [DangerScore(**row.to_dict()) for _, row in df.iterrows()]
    
    except Exception as e:
        logger.error(f"Error getting danger scores: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/danger-scores/{code_com}", response_model=DangerScore)
async def get_danger_score_commune(
    code_com: str,
    db: DatabaseManager = Depends(get_db)
):
    """
    Score de danger pour une commune spécifique
    
    **Paramètres:**
    - `code_com`: Code INSEE (ex: 75056)
    """
    try:
        result = db.get_commune_danger_score(code_com=code_com)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Commune {code_com} non trouvée"
            )
        
        return DangerScore(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting danger score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# STATISTIQUES - ANALYSES AGRÉGÉES
# ============================================================================

@router.get("/stats/temporelles", response_model=List[StatistiquesTemporelles])
async def stats_temporelles(
    annee: Optional[int] = Query(None),
    db: DatabaseManager = Depends(get_db)
):
    """
    Statistiques par jour/heure
    
    **Utilité:**
    - Identifier les heures/jours critiques
    - Patterns de circulation
    
    **Paramètres:**
    - `annee`: Filtrer par année
    """
    try:
        df = db.get_stats_temporelles(annee=annee)
        
        if df.empty:
            return []
        
        return [StatistiquesTemporelles(**row.to_dict()) for _, row in df.iterrows()]
    
    except Exception as e:
        logger.error(f"Error getting temporal stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/communes", response_model=List[StatistiquesCommune])
async def stats_communes(
    limit: int = Query(50, ge=1, le=500),
    db: DatabaseManager = Depends(get_db)
):
    """
    Top communes par nombre d'accidents
    
    **Paramètres:**
    - `limit`: Nombre de communes à retourner
    """
    try:
        df = db.get_stats_communes(limit=limit)
        
        if df.empty:
            return []
        
        return [StatistiquesCommune(**row.to_dict()) for _, row in df.iterrows()]
    
    except Exception as e:
        logger.error(f"Error getting commune stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/departements", response_model=List[StatistiquesCommune])
async def stats_departements(
    limit: int = Query(50, ge=1, le=500),
    db: DatabaseManager = Depends(get_db)
):
    """
    Statistiques par département
    
    **Paramètres:**
    - `limit`: Nombre de départements
    """
    try:
        df = db.get_stats_departements(limit=limit)
        
        if df.empty:
            return []
        
        return [StatistiquesCommune(**row.to_dict()) for _, row in df.iterrows()]
    
    except Exception as e:
        logger.error(f"Error getting dept stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/usagers", response_model=List[StatistiquesUsager])
async def stats_usagers(
    limit: int = Query(50, ge=1, le=500),
    db: DatabaseManager = Depends(get_db)
):
    """
    Statistiques usagers par âge et sexe
    
    **Utilité:**
    - Identifier groupes à risque
    - Données pour politique tarifaire assurance
    
    **Paramètres:**
    - `limit`: Nombre de lignes
    """
    try:
        df = db.get_stats_usagers(limit=limit)
        
        if df.empty:
            return []
        
        return [StatistiquesUsager(**row.to_dict()) for _, row in df.iterrows()]
    
    except Exception as e:
        logger.error(f"Error getting usager stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/vehicules", response_model=List[StatistiquesVehicule])
async def stats_vehicules(
    db: DatabaseManager = Depends(get_db)
):
    """
    Statistiques par catégorie véhicule
    
    **Utilité:**
    - Risque par type de véhicule
    - Données pour tarification
    """
    try:
        df = db.get_stats_vehicules()
        
        if df.empty:
            return []
        
        return [StatistiquesVehicule(**row.to_dict()) for _, row in df.iterrows()]
    
    except Exception as e:
        logger.error(f"Error getting vehicule stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GÉOLOCALISATION - HEATMAPS & PROXIMITÉ
# ============================================================================

@router.get("/heatmap", response_model=List[HeatmapPoint])
async def heatmap_data(
    annee: Optional[int] = Query(None),
    limit: int = Query(5000, ge=100, le=50000),
    db: DatabaseManager = Depends(get_db)
):
    """
    Données pour heatmap (lat, lon, intensité)
    
    **Utilité:**
    - Visualiser clusters géographiques
    - Identifier zones à risque
    
    **Paramètres:**
    - `annee`: Filtrer par année
    - `limit`: Nombre points max (pour perfs)
    """
    try:
        df = db.get_heatmap_data(annee=annee, limit=limit)
        
        if df.empty:
            return []
        
        return [HeatmapPoint(**row.to_dict()) for _, row in df.iterrows()]
    
    except Exception as e:
        logger.error(f"Error getting heatmap data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/accidents/near", response_model=List[AccidentProximite])
async def accidents_near(
    query: QueryProximite,
    db: DatabaseManager = Depends(get_db)
):
    """
    Trouver accidents proches d'une localisation
    
    **Utilité:**
    - Recherche spatiale
    - Événements particuliers
    
    **Body JSON:**
    ```json
    {
      "latitude": 48.8566,
      "longitude": 2.3522,
      "distance_km": 5.0
    }
    ```
    
    **Retour:** Liste avec `distance_km` calculée
    """
    try:
        df = db.get_accidents_near(
            latitude=query.latitude,
            longitude=query.longitude,
            distance_km=query.distance_km
        )
        
        if df.empty:
            return []
        
        return [AccidentProximite(**row.to_dict()) for _, row in df.iterrows()]
    
    except Exception as e:
        logger.error(f"Error getting accidents near: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ANALYSES CUSTOM
# ============================================================================

@router.post("/analyze", response_model=ResultatAnalyse)
async def custom_analysis(
    query: AnalyseCustom,
    db: DatabaseManager = Depends(get_db)
):
    """
    Exécuter analyse custom
    
    **Types d'analyses supportées:**
    - `univariee`: Distribution univariée
    - `bivariee`: Crosstab + Chi-square
    - `temporelle`: Patterns temporels
    - `spatiale`: Analyses géographiques
    - `clustering`: K-means clustering
    
    **Example:**
    ```json
    {
      "type_analyse": "bivariee",
      "colonne_principale": "gravite_max",
      "filtre_annee": 2022
    }
    ```
    """
    try:
        # Importer analyses
        from src.analyses.comprehensive_analysis import AnalysesAccidents
        
        # Récupérer données
        df_acc = db.query_to_dataframe(
            "SELECT * FROM accidents_schema.accidents WHERE annee = %s",
            (query.filtre_annee or 2022,)
        )
        
        if df_acc.empty:
            raise HTTPException(status_code=404, detail="Aucune donnée pour l'année")
        
        # Exécuter analyse
        analyses = AnalysesAccidents(df_acc)
        
        resultats = {}
        if query.type_analyse == "univariee":
            resultats = analyses.analyse_univariee_accidents()
        elif query.type_analyse == "bivariee":
            resultats = analyses.analyse_bivariee_gravite_jour()
        elif query.type_analyse == "temporelle":
            resultats = analyses.get_stats_temporelles(query.filtre_annee)
        
        return ResultatAnalyse(
            type_analyse=query.type_analyse,
            resultats=resultats,
            statistiques={"rows": len(df_acc)},
            timestamp=datetime.now()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in custom analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# UTILITAIRES
# ============================================================================

@router.get("/report/quality", tags=["reports"])
async def quality_report(
    db: DatabaseManager = Depends(get_db)
):
    """
    Rapport qualité des données
    
    **Contenu:**
    - Counts par table
    - Doublons détectés
    - Données manquantes critiques
    """
    try:
        return db.validate_data_integrity()
    except Exception as e:
        logger.error(f"Error getting quality report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metadata", tags=["info"])
async def get_metadata():
    """
    Métadonnées du projet
    
    **Inclut:**
    - Version API
    - Données disponibles
    - Plages temporelles
    """
    return {
        "version": "1.0.0",
        "title": "Accidents Routiers API",
        "description": "API pour analyse accidents routiers corporels",
        "data_range": "2016-2024",
        "tables": [
            "accidents", "caracteristiques", "lieux", "usagers", "vehicules"
        ],
        "status": "production"
    }

