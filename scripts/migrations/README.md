# Scripts de Migration

Ce répertoire contient les scripts de migration pour gérer les upgrades et downgrades entre versions.

## Structure

- `migration_manager.py` - Gestionnaire principal des migrations
- `v{MAJOR}_{MINOR}_{PATCH}.py` - Scripts de migration par version
- `migration_state.json` - État actuel des migrations

## Utilisation

### Upgrade vers la dernière version
```bash
python scripts/migrations/migration_manager.py upgrade
```

### Upgrade vers une version spécifique
```bash
python scripts/migrations/migration_manager.py upgrade --version 1.2.0
```

### Downgrade vers une version antérieure
```bash
python scripts/migrations/migration_manager.py downgrade --version 0.9.0
```

### Vérifier le statut
```bash
python scripts/migrations/migration_manager.py status
```

## Créer une nouvelle migration

Créer un fichier `v{VERSION}.py` avec la structure suivante:

```python
def up():
    """Migration upgrade"""
    # Code pour upgrade
    return True

def down():
    """Migration downgrade (rollback)"""
    # Code pour rollback
    return True

def validate():
    """Validation post-migration"""
    # Code de validation
    return True
```

## Exemples de migrations

### Migration avec schéma BDD
```python
def up():
    """Ajout d'une colonne"""
    from src.database.connection import get_db
    
    with get_db() as db:
        db.execute("""
            ALTER TABLE accidents 
            ADD COLUMN risk_score FLOAT
        """)
    return True

def down():
    """Suppression de la colonne"""
    from src.database.connection import get_db
    
    with get_db() as db:
        db.execute("""
            ALTER TABLE accidents 
            DROP COLUMN risk_score
        """)
    return True
```

### Migration avec données
```python
def up():
    """Migration de données"""
    import pandas as pd
    
    # Charger anciennes données
    df = pd.read_csv("old_data.csv")
    
    # Transformer
    df["new_field"] = df["old_field"].apply(transform)
    
    # Sauvegarder
    df.to_csv("new_data.csv", index=False)
    
    return True
```

## Bonnes pratiques

1. **Toujours tester les migrations** en dev avant prod
2. **Backup la BDD** avant toute migration en prod
3. **Écrire des rollbacks** pour chaque migration
4. **Documenter les changements** dans le script
5. **Valider les migrations** avec des tests
6. **Versionner atomiquement** (1 changement = 1 version)

## Ordre des migrations

Les migrations sont exécutées dans l'ordre des versions (SemVer):
- 0.8.0 → 0.9.0 → 1.0.0 → 1.0.1 → 1.1.0 → 2.0.0

Pour un downgrade, l'ordre est inversé.
