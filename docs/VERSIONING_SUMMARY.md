# 🚀 Système de Versioning Installé

## ✅ Composants Créés

### 1. Module de Versioning (`src/api/version.py`)
- Constantes: `VERSION`, `API_VERSION`, `BUILD_DATE`
- Métadonnées complètes de version
- Historique complet (CHANGELOG)
- Fonctions utilitaires:
  - `get_version_info()` - Informations complètes
  - `get_changelog()` - Historique des versions
  - `is_version_compatible()` - Vérification compatibilité
  - `compare_versions()` - Comparaison SemVer
  - `get_migration_path()` - Chemin de migration
  - `requires_migration()` - Vérification migration nécessaire

### 2. Endpoints API (`src/api/version_routes.py`)
- `GET /api/v1/version` - Version actuelle
- `GET /api/v1/version/changelog` - Historique
- `GET /api/v1/version/latest` - Dernière version
- `GET /api/v1/version/compatibility/{version}` - Compatibilité
- `GET /api/v1/version/migration` - Chemins de migration
- `GET /api/v1/version/supported` - Versions supportées
- `GET /api/v1/version/health` - Health check avec version

### 3. Système de Migration (`scripts/migrations/`)
- `migration_manager.py` - Gestionnaire principal
  - Commandes: upgrade, downgrade, status
  - Gestion de l'état dans `migration_state.json`
  - Validation des migrations
- `v1_0_0.py` - Migration v1.0.0
- `README.md` - Guide complet des migrations

### 4. Script de Déploiement (`scripts/deploy.sh`)
Automatise le workflow complet:
- ✅ Validation environnement (git, python, branche main)
- ✅ Exécution tests (pytest)
- ✅ Gestion de version (auto-increment ou manuel)
- ✅ Exécution migrations
- ✅ Commit + Tag Git
- ✅ Push GitHub (auto-deploy Render)
- ✅ Validation post-deploy
- ✅ Support rollback

### 5. Documentation (`docs/VERSIONING.md`)
Guide complet SemVer 2.0.0:
- Stratégie de versioning
- Workflow de release
- Procédures de migration
- Guide de déploiement
- Stratégies de rollback
- API versioning
- Bonnes pratiques

### 6. Intégrations
- **main.py**: VERSION dynamique dans FastAPI
- **streamlit_app.py**: Version dans sidebar
- **pyproject.toml**: Version centralisée

## 📖 Utilisation

### Consulter la Version API
```bash
curl https://projetetudeaccidentfrance.onrender.com/api/v1/version
```

### Déployer une Nouvelle Version
```bash
# Auto-increment PATCH (1.0.0 → 1.0.1)
./scripts/deploy.sh

# Version spécifique
./scripts/deploy.sh 1.1.0 production
```

### Gérer les Migrations
```bash
# Status
python scripts/migrations/migration_manager.py status

# Upgrade
python scripts/migrations/migration_manager.py upgrade --version 1.1.0

# Downgrade
python scripts/migrations/migration_manager.py downgrade --version 1.0.0
```

### Rollback d'Urgence
```bash
# Revenir à la version précédente
git checkout v1.0.0
python scripts/migrations/migration_manager.py downgrade --version 1.0.0
git push origin main --force
```

## 🎯 Avantages

1. **Traçabilité**: Chaque version est documentée dans CHANGELOG
2. **Automatisation**: Script deploy.sh gère tout le workflow
3. **Sécurité**: Validations pré/post-deploy
4. **Rollback**: Downgrade rapide en cas de problème
5. **API Monitoring**: Endpoints pour surveiller versions
6. **Compatibilité**: Vérification automatique des versions client
7. **Documentation**: Guide complet des procédures

## 📊 Endpoints de Version

Tous disponibles sur:
- **Production**: https://projetetudeaccidentfrance.onrender.com
- **Local**: http://localhost:8000

```bash
# Version actuelle
GET /api/v1/version

# Changelog
GET /api/v1/version/changelog

# Compatibilité
GET /api/v1/version/compatibility/1.0.0

# Migration path
GET /api/v1/version/migration?from_version=0.9.0&to_version=1.0.0
```

## 🚦 Prochaines Étapes

1. Tester les endpoints de version en production
2. Créer une release v1.0.0 officielle avec tag Git
3. Documenter les procédures d'upgrade pour l'équipe
4. Configurer monitoring des versions (alertes)
5. Planifier v1.1.0 avec nouvelles features

## 📚 Références

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Guide Complet](docs/VERSIONING.md)
- [README Migrations](scripts/migrations/README.md)
