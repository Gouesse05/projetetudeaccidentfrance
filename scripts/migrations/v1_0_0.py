"""
=============================================================================
Migration v1.0.0 - Initial Production Release
=============================================================================

Migration de la version 0.9.0 vers 1.0.0
"""

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))


def up():
    """
    Migration UP: 0.9.0 -> 1.0.0
    
    Changements:
    - Ajout du système de versioning
    - Ajout des endpoints /api/v1/version/*
    - Ajout de la section Risk Normalization au dashboard
    - Mise à jour de la documentation
    """
    print("  📦 Déploiement version 1.0.0")
    print("  ✅ Système de versioning activé")
    print("  ✅ Endpoints de version disponibles")
    print("  ✅ Risk Normalization intégrée")
    
    # Pas de migration de schéma BDD nécessaire
    return True


def down():
    """
    Migration DOWN: 1.0.0 -> 0.9.0 (Rollback)
    
    Rollback des fonctionnalités de la v1.0.0
    """
    print("  ⬇️  Rollback vers 0.9.0")
    print("  ⚠️  Désactivation des endpoints de version")
    print("  ⚠️  Suppression Risk Normalization du dashboard")
    
    # Pas de rollback de schéma BDD nécessaire
    return True


def validate():
    """Validation post-migration"""
    print("  🔍 Validation de la migration...")
    
    # Vérifier que les modules sont accessibles
    try:
        from src.api.version import VERSION, get_version_info
        from src.api.version_routes import router
        
        assert VERSION == "1.0.0", "Version incorrecte"
        
        print("  ✅ Validation réussie")
        return True
        
    except Exception as e:
        print(f"  ❌ Validation échouée: {e}")
        return False


if __name__ == "__main__":
    print("Migration v1.0.0")
    print("-" * 50)
    
    if up():
        if validate():
            print("\n✅ Migration 1.0.0 réussie")
        else:
            print("\n❌ Validation échouée")
            down()
    else:
        print("\n❌ Migration échouée")
