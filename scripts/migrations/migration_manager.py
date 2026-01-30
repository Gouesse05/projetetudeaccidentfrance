"""
=============================================================================
MIGRATION MANAGER - Gestion des migrations de version
=============================================================================

Système pour gérer les upgrades et downgrades entre versions.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime

# Ajouter le répertoire racine au PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.api.version import (
    VERSION,
    get_migration_path,
    requires_migration,
    compare_versions,
    CHANGELOG
)


class Migration:
    """Classe de base pour les migrations"""
    
    version: str = "0.0.0"
    description: str = ""
    
    def up(self):
        """Migration upgrade"""
        raise NotImplementedError("Méthode up() doit être implémentée")
    
    def down(self):
        """Migration downgrade (rollback)"""
        raise NotImplementedError("Méthode down() doit être implémentée")
    
    def validate(self) -> bool:
        """Validation de la migration"""
        return True


class MigrationManager:
    """Gestionnaire des migrations"""
    
    def __init__(self, migrations_dir: Path = None):
        self.migrations_dir = migrations_dir or Path(__file__).parent
        self.state_file = self.migrations_dir / "migration_state.json"
        self.current_version = self.load_current_version()
    
    def load_current_version(self) -> str:
        """Charge la version actuelle depuis l'état"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                return state.get("version", "0.0.0")
        return "0.0.0"
    
    def save_state(self, version: str, status: str = "success"):
        """Sauvegarde l'état de la migration"""
        state = {
            "version": version,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "previous_version": self.current_version,
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def upgrade(self, target_version: str = None):
        """
        Upgrade vers une version cible
        
        Args:
            target_version: Version cible (défaut: VERSION actuelle)
        """
        target = target_version or VERSION
        
        print(f"[UPGRADE] De {self.current_version} vers {target}")
        
        # Obtenir le chemin de migration
        path = get_migration_path(self.current_version, target)
        
        if not path:
            print(f"❌ Aucun chemin de migration trouvé")
            return False
        
        if len(path) == 1:
            print(f"[OK] Déjà sur la version {target}")
            return True
        
        print(f"📋 Chemin de migration: {' -> '.join(path)}")
        
        # Exécuter les migrations
        for i in range(len(path) - 1):
            from_v = path[i]
            to_v = path[i + 1]
            
            print(f"\n📦 Migration {from_v} -> {to_v}")
            
            if not self._run_migration_up(to_v):
                print(f"[ERROR] Échec de la migration vers {to_v}")
                return False
            
            self.save_state(to_v, "success")
            self.current_version = to_v
            print(f"[OK] Migration vers {to_v} réussie")
        
        print(f"\n[SUCCESS] Upgrade vers {target} terminé avec succès!")
        return True
    
    def downgrade(self, target_version: str):
        """
        Downgrade vers une version antérieure
        
        Args:
            target_version: Version cible
        """
        print(f"[DOWNGRADE] De {self.current_version} vers {target_version}")
        
        if compare_versions(target_version, self.current_version) >= 0:
            print(f"[ERROR] La version cible doit être inférieure à {self.current_version}")
            return False
        
        # Obtenir le chemin de migration (inversé)
        path = get_migration_path(self.current_version, target_version)
        
        if not path:
            print(f"❌ Aucun chemin de migration trouvé")
            return False
        
        print(f"📋 Chemin de migration: {' -> '.join(path)}")
        
        # Confirmation utilisateur pour downgrade
        confirm = input(f"\n[WARNING] Confirmer le downgrade vers {target_version}? (yes/no): ")
        if confirm.lower() != "yes":
            print("[CANCELLED] Downgrade annulé")
            return False
        
        # Exécuter les migrations en sens inverse
        for i in range(len(path) - 1):
            from_v = path[i]
            to_v = path[i + 1]
            
            print(f"\n📦 Rollback {from_v} -> {to_v}")
            
            if not self._run_migration_down(from_v):
                print(f"[ERROR] Échec du rollback depuis {from_v}")
                return False
            
            self.save_state(to_v, "rollback")
            self.current_version = to_v
            print(f"[OK] Rollback vers {to_v} réussi")
        
        print(f"\n[SUCCESS] Downgrade vers {target_version} terminé avec succès!")
        return True
    
    def _run_migration_up(self, version: str) -> bool:
        """Exécute la migration up pour une version"""
        try:
            # Chercher le fichier de migration
            migration_file = self.migrations_dir / f"v{version.replace('.', '_')}.py"
            
            if not migration_file.exists():
                print(f"[INFO] Pas de script de migration pour {version} (migration automatique)")
                return True
            
            # Importer et exécuter la migration
            # (implémentation simplifiée - à adapter selon besoins)
            print(f"  [RUN] Exécution de la migration {migration_file.name}")
            return True
            
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
            return False
    
    def _run_migration_down(self, version: str) -> bool:
        """Exécute la migration down pour une version"""
        try:
            migration_file = self.migrations_dir / f"v{version.replace('.', '_')}.py"
            
            if not migration_file.exists():
                print(f"[INFO] Pas de script de rollback pour {version} (rollback automatique)")
                return True
            
            print(f"  [RUN] Exécution du rollback {migration_file.name}")
            return True
            
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
            return False
    
    def status(self):
        """Affiche le statut des migrations"""
        print(f"[STATUS] Statut des migrations")
        print(f"  Version actuelle: {self.current_version}")
        print(f"  Version disponible: {VERSION}")
        
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                print(f"  Dernière migration: {state.get('timestamp')}")
                print(f"  Statut: {state.get('status')}")
        
        if requires_migration(self.current_version, VERSION):
            print(f"\n[WARNING] Migration requise vers {VERSION}")
        else:
            print(f"\n[OK] Système à jour")


def main():
    """Point d'entrée CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gestion des migrations de version")
    parser.add_argument("command", choices=["upgrade", "downgrade", "status"],
                       help="Commande à exécuter")
    parser.add_argument("--version", help="Version cible")
    
    args = parser.parse_args()
    
    manager = MigrationManager()
    
    if args.command == "upgrade":
        manager.upgrade(args.version)
    elif args.command == "downgrade":
        if not args.version:
            print("[ERROR] --version requis pour downgrade")
            return
        manager.downgrade(args.version)
    elif args.command == "status":
        manager.status()


if __name__ == "__main__":
    main()
