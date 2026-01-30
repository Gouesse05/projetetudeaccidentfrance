"""
=============================================================================
DATABASE MODULE
=============================================================================

Module pour gestion PostgreSQL:
- Connection pooling
- Schéma DDL
- Chargement de données
- Requêtes analytiques

Utilisation:
    from src.database import DatabaseManager
    db = DatabaseManager()
    df = db.query_accidents(annee=2022)
"""

from src.database.database_utils import (
    DatabaseManager,
    create_db_manager,
    quick_query
)

__all__ = [
    'DatabaseManager',
    'create_db_manager',
    'quick_query',
]

__version__ = '1.0.0'

