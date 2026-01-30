"""
=============================================================================
MODELS.PY - Schémas Pydantic pour l'API
=============================================================================

Définit les modèles de données pour validation et documentation Swagger
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import date, datetime


# ============================================================================
# MODÈLES DE RÉPONSE
# ============================================================================

class AccidentBase(BaseModel):
    """Modèle de base pour accidents"""
    num_acc: str = Field(..., description="Numéro unique d'accident")
    date_accident: date = Field(..., description="Date de l'accident")
    annee: int = Field(..., description="Année de l'accident")
    mois: int = Field(..., ge=1, le=12, description="Mois (1-12)")
    jour_semaine: int = Field(..., ge=1, le=7, description="Jour semaine (1=Lundi, 7=Dimanche)")
    heure: int = Field(..., ge=0, le=23, description="Heure (0-23)")
    

class AccidentEnrichi(AccidentBase):
    """Accident enrichi avec localisation et contexte"""
    id_accident: int
    nom_com: str = Field(..., description="Nom commune")
    code_com: str = Field(..., description="Code INSEE commune")
    code_dept: str = Field(..., description="Code département")
    nom_dept: str = Field(..., description="Nom département")
    region: str = Field(..., description="Région")
    population: Optional[int] = Field(None, description="Population commune")
    densite_hab_km2: Optional[float] = Field(None, description="Densité (hab/km²)")
    zone_urbaine: Optional[bool] = Field(None, description="TRUE si zone urbaine")
    nombre_vehicules: int = Field(..., description="Nombre véhicules impliqués")
    nombre_personnes: int = Field(..., description="Nombre personnes impliquées")
    gravite_max: int = Field(..., ge=1, le=4, description="1=Indemne, 2=Léger, 3=Hospitalisé, 4=Tué")
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")
    periode: str = Field(..., description="'Weekend' ou 'Semaine'")
    plage_horaire: str = Field(..., description="Plage horaire (heures pointe, nuit, etc.)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "num_acc": "201600001",
                "date_accident": "2016-01-01",
                "annee": 2016,
                "mois": 1,
                "jour_semaine": 5,
                "heure": 14,
                "nom_com": "Paris",
                "code_com": "75056",
                "gravite_max": 3,
                "nombre_personnes": 2
            }
        }
    )


class DangerScore(BaseModel):
    """Score de danger par commune"""
    id_com: int
    nom_com: str = Field(..., description="Nom commune")
    nom_dept: str = Field(..., description="Nom département")
    region: str = Field(..., description="Région")
    nombre_accidents: int = Field(..., description="Total accidents")
    nombre_personnes_impliquees: int = Field(..., description="Total personnes")
    nombre_personnes_tuees: int = Field(..., description="Total décès")
    gravite_moyenne: float = Field(..., description="Gravité moyenne (1-4)")
    score_danger: float = Field(..., ge=0, le=100, description="Score composite (0-100)")
    categorie_risque: str = Field(..., description="'TRÈS_ÉLEVÉ', 'ÉLEVÉ', 'MOYEN', 'FAIBLE'")
    population: Optional[int] = Field(None, description="Population commune")
    densite_hab_km2: Optional[float] = Field(None, description="Densité (hab/km²)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nom_com": "Paris",
                "score_danger": 85.5,
                "categorie_risque": "TRÈS_ÉLEVÉ",
                "nombre_accidents": 1200,
                "nombre_personnes_tuees": 45
            }
        }
    )


class StatistiquesTemporelles(BaseModel):
    """Statistiques par période temporelle"""
    annee: int
    mois: Optional[int]
    jour_semaine: Optional[int]
    heure: Optional[int]
    nombre_accidents: int = Field(..., description="Nombre accidents pour cette période")
    personnes_impliquees: int = Field(..., description="Total personnes")
    gravite_moyenne: float = Field(..., description="Gravité moyenne")
    nombre_deces: int = Field(..., description="Nombre de décédés")


class StatistiquesCommune(BaseModel):
    """Statistiques pour une commune"""
    nom_com: str
    code_com: str
    nom_dept: str
    code_dept: str
    population: Optional[int]
    densite_hab_km2: Optional[float]
    nombre_accidents: int
    personnes_impliquees: int
    nombre_deces: int
    gravite_moyenne: float
    accidents_pour_100k_hab: Optional[float] = Field(
        None, description="Accidents par 100k habitants (normalisé)"
    )


class StatistiquesUsager(BaseModel):
    """Statistiques usagers par âge et sexe"""
    age: int = Field(..., description="Âge (années)")
    sexe: str = Field(..., description="'1'=Masculin, '2'=Féminin")
    nombre_usagers: int
    nombre_deces: int
    gravite_moyenne: float
    pct_deces: float = Field(..., description="Pourcentage de décédés (%)")


class StatistiquesVehicule(BaseModel):
    """Statistiques par catégorie véhicule"""
    categorie_vehicule: str
    nombre_accidents: int
    nombre_accidents_distincts: int
    gravite_moyenne: float
    personnes_impliquees: int


class HeatmapPoint(BaseModel):
    """Point pour heatmap (géolocalisation)"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    annee: int
    heure: int
    gravite_max: int = Field(..., ge=1, le=4)
    weight: int = Field(..., ge=1, description="Nombre d'accidents au point")


class AccidentProximite(BaseModel):
    """Accident avec calcul de distance"""
    id_accident: int
    num_acc: str
    date_accident: date
    nom_com: str
    gravite_max: int
    latitude: Optional[float]
    longitude: Optional[float]
    distance_km: float = Field(..., description="Distance depuis point de référence (km)")


class Health(BaseModel):
    """Status de santé du service"""
    status: str = Field(..., description="'OK' ou 'ERROR'")
    database: str = Field(..., description="État de la base de données")
    timestamp: datetime = Field(default_factory=datetime.now)
    messages: List[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    """Réponse d'erreur standard"""
    error: str = Field(..., description="Message d'erreur")
    detail: Optional[str] = Field(None, description="Détails supplémentaires")
    status_code: int = Field(..., description="Code HTTP")


# ============================================================================
# MODÈLES DE REQUÊTE
# ============================================================================

class QueryAccidents(BaseModel):
    """Paramètres pour requête accidents"""
    annee: Optional[int] = Field(None, description="Filtrer par année")
    mois: Optional[int] = Field(None, ge=1, le=12, description="Filtrer par mois")
    dept: Optional[str] = Field(None, description="Code département")
    gravite_min: Optional[int] = Field(None, ge=1, le=4, description="Gravité minimale")
    limit: int = Field(100, ge=1, le=10000, description="Nombre de résultats max")


class QueryHeatmap(BaseModel):
    """Paramètres pour heatmap"""
    annee: Optional[int] = Field(None, description="Année")
    mois: Optional[int] = Field(None, ge=1, le=12, description="Mois")
    limit: int = Field(5000, ge=100, le=50000, description="Points max")


class QueryProximite(BaseModel):
    """Paramètres requête proximité"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    distance_km: float = Field(5.0, ge=0.1, le=100, description="Rayon de recherche (km)")


# ============================================================================
# MODÈLES ANALYTIQUES
# ============================================================================

class AnalyseCustom(BaseModel):
    """Requête analyse custom"""
    type_analyse: str = Field(
        ..., 
        description="'univariee', 'bivariee', 'temporelle', 'spatiale', 'clustering'"
    )
    colonne_principale: str = Field(..., description="Colonne à analyser")
    filtre_annee: Optional[int] = Field(None)
    filtre_dept: Optional[str] = Field(None)


class ResultatAnalyse(BaseModel):
    """Résultat d'analyse"""
    type_analyse: str
    resultats: Dict[str, Any] = Field(..., description="Résultats bruts")
    statistiques: Dict[str, Any] = Field(..., description="Statistiques descriptives")
    visualisation: Optional[str] = Field(None, description="URL ou data visualisation")
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================================
# PAGINATION
# ============================================================================

class PaginatedResponse(BaseModel):
    """Réponse paginée générique"""
    total: int = Field(..., description="Total enregistrements")
    limit: int = Field(..., description="Limite par page")
    offset: int = Field(..., description="Offset")
    items: List[Any] = Field(..., description="Éléments")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 1000,
                "limit": 100,
                "offset": 0,
                "items": []
            }
        }
    )

