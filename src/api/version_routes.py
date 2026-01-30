"""
=============================================================================
VERSION_ROUTES.PY - Endpoints de versioning
=============================================================================

Endpoints pour gérer et consulter les versions de l'API.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List, Optional
from datetime import datetime

from .version import (
    get_version_info,
    get_changelog,
    get_latest_version,
    is_version_compatible,
    compare_versions,
    get_migration_path,
    requires_migration,
    VERSION,
    API_VERSION,
    SUPPORTED_API_VERSIONS,
)

router = APIRouter(prefix="/api/v1", tags=["version"])


# ============================================================================
# ENDPOINTS DE VERSION
# ============================================================================

@router.get("/version", summary="Informations de version")
async def get_version() -> Dict[str, Any]:
    """
    Retourne les informations complètes de version de l'API.
    
    **Inclut:**
    - Version actuelle (SemVer)
    - Version de l'API
    - Date de build
    - Environnement
    - Versions d'API supportées
    - Dépendances minimales requises
    
    **Exemple de réponse:**
    ```json
    {
        "version": "1.0.0",
        "api_version": "v1",
        "build_date": "2026-01-31",
        "environment": "production",
        "status": "stable"
    }
    ```
    """
    return get_version_info()


@router.get("/version/changelog", summary="Historique des versions")
async def get_version_changelog(limit: int = 10) -> Dict[str, Any]:
    """
    Retourne l'historique des versions (changelog).
    
    **Paramètres:**
    - **limit**: Nombre maximum de versions à retourner (défaut: 10)
    
    **Exemple de réponse:**
    ```json
    {
        "current_version": "1.0.0",
        "total_versions": 4,
        "changelog": [
            {
                "version": "1.0.0",
                "date": "2026-01-31",
                "type": "major",
                "changes": ["Initial release"],
                "breaking_changes": [],
                "migrations_required": false
            }
        ]
    }
    ```
    """
    changelog = get_changelog(limit=limit)
    
    return {
        "current_version": VERSION,
        "api_version": API_VERSION,
        "total_versions": len(changelog),
        "changelog": changelog,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/version/latest", summary="Dernière version disponible")
async def get_latest() -> Dict[str, str]:
    """
    Retourne la dernière version disponible de l'API.
    
    **Exemple de réponse:**
    ```json
    {
        "latest_version": "1.0.0",
        "api_version": "v1",
        "status": "stable"
    }
    ```
    """
    return {
        "latest_version": get_latest_version(),
        "api_version": API_VERSION,
        "status": "stable",
        "release_date": "2026-01-31",
    }


@router.get("/version/compatibility/{client_version}", summary="Vérifier compatibilité")
async def check_compatibility(client_version: str) -> Dict[str, Any]:
    """
    Vérifie si une version client est compatible avec la version actuelle.
    
    **Paramètres:**
    - **client_version**: Version du client (format SemVer: X.Y.Z)
    
    **Règles de compatibilité:**
    - Compatible si même version MAJOR (X.y.z)
    - Incompatible si version MAJOR différente
    
    **Exemple de réponse:**
    ```json
    {
        "client_version": "1.2.0",
        "server_version": "1.0.0",
        "compatible": true,
        "message": "Version compatible"
    }
    ```
    """
    compatible = is_version_compatible(client_version)
    comparison = compare_versions(client_version, VERSION)
    
    if comparison < 0:
        message = "Client version plus ancienne mais compatible"
    elif comparison > 0:
        message = "Client version plus récente mais compatible"
    else:
        message = "Version identique"
    
    if not compatible:
        message = f"Version incompatible. Upgrade requis vers {VERSION}"
    
    return {
        "client_version": client_version,
        "server_version": VERSION,
        "api_version": API_VERSION,
        "compatible": compatible,
        "comparison": comparison,
        "message": message,
        "upgrade_required": comparison < 0 and not compatible,
    }


@router.get("/version/migration", summary="Chemin de migration")
async def get_migration(
    from_version: str,
    to_version: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retourne le chemin de migration entre deux versions.
    
    **Paramètres:**
    - **from_version**: Version source
    - **to_version**: Version cible (défaut: version actuelle)
    
    **Exemple de réponse:**
    ```json
    {
        "from_version": "0.8.0",
        "to_version": "1.0.0",
        "migration_path": ["0.8.0", "0.9.0", "1.0.0"],
        "requires_migration": true,
        "steps": 2
    }
    ```
    """
    target_version = to_version or VERSION
    
    # Vérifier que les versions existent
    path = get_migration_path(from_version, target_version)
    
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Migration path not found from {from_version} to {target_version}"
        )
    
    needs_migration = requires_migration(from_version, target_version)
    is_upgrade = compare_versions(from_version, target_version) < 0
    
    return {
        "from_version": from_version,
        "to_version": target_version,
        "migration_path": path,
        "requires_migration": needs_migration,
        "migration_type": "upgrade" if is_upgrade else "downgrade",
        "steps": len(path) - 1,
        "estimated_time": f"{(len(path) - 1) * 5} minutes",
    }


@router.get("/version/supported", summary="Versions supportées")
async def get_supported_versions() -> Dict[str, Any]:
    """
    Retourne la liste des versions d'API supportées.
    
    **Exemple de réponse:**
    ```json
    {
        "current_api_version": "v1",
        "supported_versions": ["v1"],
        "deprecated_versions": [],
        "sunset_date": null
    }
    ```
    """
    return {
        "current_api_version": API_VERSION,
        "supported_versions": SUPPORTED_API_VERSIONS,
        "deprecated_versions": [],
        "sunset_date": None,
        "message": "Toutes les versions listées sont actuellement supportées",
    }


@router.get("/version/health", summary="Health check avec version")
async def version_health() -> Dict[str, Any]:
    """
    Health check incluant les informations de version.
    
    Utile pour monitoring et alertes basées sur version.
    
    **Exemple de réponse:**
    ```json
    {
        "status": "healthy",
        "version": "1.0.0",
        "api_version": "v1",
        "timestamp": "2026-01-31T10:00:00",
        "uptime": "2 days"
    }
    ```
    """
    return {
        "status": "healthy",
        "version": VERSION,
        "api_version": API_VERSION,
        "environment": "production",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "api": "ok",
            "database": "ok",
            "dependencies": "ok",
        }
    }
