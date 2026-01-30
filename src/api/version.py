"""
=============================================================================
VERSION.PY - Gestion des versions de l'API
=============================================================================

Système de versioning pour gérer les upgrades et downgrades en production.
Suit la spécification Semantic Versioning 2.0.0 (https://semver.org/)

Format: MAJOR.MINOR.PATCH
- MAJOR: Changements incompatibles (breaking changes)
- MINOR: Nouvelles fonctionnalités compatibles
- PATCH: Corrections de bugs compatibles
"""

from datetime import datetime
from typing import Dict, List, Any

# ============================================================================
# VERSION ACTUELLE
# ============================================================================

VERSION = "1.0.0"
API_VERSION = "v1"
BUILD_DATE = "2026-01-31"
PYTHON_VERSION = "3.13.4"

# ============================================================================
# MÉTADONNÉES DE LA VERSION
# ============================================================================

VERSION_INFO = {
    "version": VERSION,
    "api_version": API_VERSION,
    "build_date": BUILD_DATE,
    "python_version": PYTHON_VERSION,
    "environment": "production",  # production | staging | development
    "status": "stable",  # stable | beta | alpha
}

# ============================================================================
# HISTORIQUE DES VERSIONS
# ============================================================================

CHANGELOG: List[Dict[str, Any]] = [
    {
        "version": "1.0.0",
        "date": "2026-01-31",
        "type": "major",
        "changes": [
            "🚀 Initial production release",
            "✅ API FastAPI avec endpoints statistiques accidents",
            "✅ Dashboard Streamlit avec visualisations interactives",
            "✅ Analyse de normalisation des risques (INSEE/ONISR)",
            "✅ Déploiement Render avec auto-deploy",
            "✅ Documentation OpenAPI complète",
            "✅ Tests unitaires et coverage >80%",
        ],
        "breaking_changes": [],
        "migrations_required": False,
    },
    {
        "version": "0.9.0",
        "date": "2026-01-30",
        "type": "minor",
        "changes": [
            "🔧 Fix deprecation warnings Streamlit",
            "🔧 Fix compatibility Python 3.13.4",
            "📝 Update documentation README",
        ],
        "breaking_changes": [],
        "migrations_required": False,
    },
    {
        "version": "0.8.0",
        "date": "2026-01-29",
        "changes": [
            "🎨 Dashboard Streamlit initial",
            "📊 Visualisations plotly",
            "🔗 Intégration API REST",
        ],
        "breaking_changes": [],
        "migrations_required": False,
    },
    {
        "version": "0.7.0",
        "date": "2026-01-28",
        "changes": [
            "⚡ API FastAPI endpoints",
            "📊 Endpoints statistiques",
            "🔍 Endpoints recherche",
        ],
        "breaking_changes": [],
        "migrations_required": False,
    },
]

# ============================================================================
# VERSIONS COMPATIBLES
# ============================================================================

# Versions de l'API supportées (pour backward compatibility)
SUPPORTED_API_VERSIONS = ["v1"]

# Versions minimales des dépendances critiques
MIN_DEPENDENCIES = {
    "fastapi": "0.104.0",
    "streamlit": "1.28.0",
    "pandas": "2.0.0",
    "numpy": "1.24.0",
    "plotly": "5.17.0",
    "psycopg2-binary": "2.9.9",
}

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_version_info() -> Dict[str, Any]:
    """Retourne les informations complètes de version"""
    return {
        **VERSION_INFO,
        "supported_api_versions": SUPPORTED_API_VERSIONS,
        "min_dependencies": MIN_DEPENDENCIES,
    }


def get_changelog(limit: int = 5) -> List[Dict[str, Any]]:
    """Retourne l'historique des versions (limité)"""
    return CHANGELOG[:limit]


def get_latest_version() -> str:
    """Retourne la dernière version"""
    return VERSION


def is_version_compatible(client_version: str) -> bool:
    """Vérifie si une version client est compatible"""
    try:
        client_major = int(client_version.split(".")[0])
        current_major = int(VERSION.split(".")[0])
        # Compatible si même MAJOR version
        return client_major == current_major
    except (ValueError, IndexError):
        return False


def compare_versions(v1: str, v2: str) -> int:
    """
    Compare deux versions (SemVer)
    
    Returns:
        -1 si v1 < v2
         0 si v1 == v2
         1 si v1 > v2
    """
    def parse_version(v: str) -> tuple:
        return tuple(int(x) for x in v.split("."))
    
    try:
        parts1 = parse_version(v1)
        parts2 = parse_version(v2)
        
        if parts1 < parts2:
            return -1
        elif parts1 > parts2:
            return 1
        else:
            return 0
    except (ValueError, IndexError):
        return 0


def get_migration_path(from_version: str, to_version: str) -> List[str]:
    """
    Retourne le chemin de migration entre deux versions
    
    Args:
        from_version: Version source
        to_version: Version cible
        
    Returns:
        Liste des versions intermédiaires pour migration
    """
    versions = [entry["version"] for entry in CHANGELOG]
    
    try:
        from_idx = versions.index(from_version)
        to_idx = versions.index(to_version)
        
        if from_idx < to_idx:
            # Upgrade
            return versions[from_idx:to_idx + 1]
        else:
            # Downgrade
            return list(reversed(versions[to_idx:from_idx + 1]))
    except ValueError:
        return []


def requires_migration(from_version: str, to_version: str) -> bool:
    """Vérifie si une migration est nécessaire entre deux versions"""
    path = get_migration_path(from_version, to_version)
    
    for version in path:
        entry = next((e for e in CHANGELOG if e["version"] == version), None)
        if entry and entry.get("migrations_required", False):
            return True
    
    return False


# ============================================================================
# METADATA POUR OPENAPI
# ============================================================================

OPENAPI_TAGS_METADATA = [
    {
        "name": "health",
        "description": "Endpoints de santé et version de l'API",
    },
    {
        "name": "statistics",
        "description": "Endpoints statistiques sur les accidents",
    },
    {
        "name": "search",
        "description": "Endpoints de recherche et filtrage",
    },
    {
        "name": "analysis",
        "description": "Endpoints d'analyse avancée",
    },
]
