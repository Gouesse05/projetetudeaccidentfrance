# Guide de Versioning

Ce document décrit la stratégie de versioning et les procédures de gestion des versions pour le projet Accidents API.

## 📋 Table des matières

- [Stratégie de Versioning](#stratégie-de-versioning)
- [Semantic Versioning (SemVer)](#semantic-versioning-semver)
- [Workflow de Release](#workflow-de-release)
- [Migrations](#migrations)
- [Déploiement](#déploiement)
- [Rollback](#rollback)
- [API Versioning](#api-versioning)
- [Bonnes Pratiques](#bonnes-pratiques)

## Stratégie de Versioning

Le projet suit la spécification **Semantic Versioning 2.0.0** (https://semver.org/).

### Format de version

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: Changements incompatibles (breaking changes)
- **MINOR**: Nouvelles fonctionnalités compatibles
- **PATCH**: Corrections de bugs compatibles

### Exemples

- `1.0.0` → `1.0.1` : Fix de bug
- `1.0.1` → `1.1.0` : Nouvelle fonctionnalité
- `1.1.0` → `2.0.0` : Breaking change

## Semantic Versioning (SemVer)

### Quand incrémenter MAJOR (X.y.z)

Changements incompatibles avec les versions précédentes:

- ❌ Suppression d'endpoints API
- ❌ Modification du format de réponse existant
- ❌ Changement de schéma BDD incompatible
- ❌ Modification de signatures de fonctions publiques
- ❌ Suppression de paramètres obligatoires

**Exemple:**
```python
# v1.0.0
GET /api/v1/accidents
Response: {"accidents": [...]}

# v2.0.0 - BREAKING CHANGE
GET /api/v2/accidents  # Nouveau endpoint
Response: {"data": [...], "meta": {...}}  # Nouveau format
```

### Quand incrémenter MINOR (x.Y.z)

Nouvelles fonctionnalités compatibles:

- ✅ Ajout de nouveaux endpoints
- ✅ Ajout de paramètres optionnels
- ✅ Nouvelles fonctionnalités dans le dashboard
- ✅ Amélioration des performances
- ✅ Ajout de champs optionnels dans les réponses

**Exemple:**
```python
# v1.0.0
GET /api/v1/accidents

# v1.1.0 - Nouvelle fonctionnalité
GET /api/v1/accidents/risk-analysis  # Nouveau endpoint
GET /api/v1/accidents?include_weather=true  # Nouveau paramètre optionnel
```

### Quand incrémenter PATCH (x.y.Z)

Corrections de bugs compatibles:

- 🔧 Fix de bugs
- 🔧 Corrections de sécurité
- 🔧 Amélioration de la documentation
- 🔧 Refactoring interne
- 🔧 Optimisation de performances sans changement de comportement

**Exemple:**
```python
# v1.0.0
def calculate_risk(age):
    return age / 0  # Bug!

# v1.0.1 - Bug fix
def calculate_risk(age):
    return age / 100 if age > 0 else 0  # Fixed
```

## Workflow de Release

### 1. Planification

```bash
# Déterminer le type de changement
- Breaking change? → MAJOR
- Nouvelle fonctionnalité? → MINOR
- Bug fix? → PATCH
```

### 2. Développement

```bash
# Créer une branche feature
git checkout -b feature/new-feature

# Développer
# ...

# Tests
pytest tests/

# Commit
git commit -m "feat: Add new feature"
```

### 3. Préparation de la release

```bash
# Mettre à jour CHANGELOG
# Mettre à jour version dans src/api/version.py
# Créer migration si nécessaire

# Commit
git commit -m "chore: Prepare release v1.1.0"
```

### 4. Release

```bash
# Utiliser le script de déploiement automatique
./scripts/deploy.sh 1.1.0 production

# OU manuellement:
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin main
git push origin v1.1.0
```

## Migrations

### Structure des migrations

```
scripts/migrations/
├── migration_manager.py       # Gestionnaire
├── migration_state.json       # État actuel
├── v1_0_0.py                 # Migration v1.0.0
├── v1_1_0.py                 # Migration v1.1.0
└── README.md                 # Documentation
```

### Créer une migration

```python
# scripts/migrations/v1_1_0.py

def up():
    """Migration upgrade: 1.0.0 -> 1.1.0"""
    # Code pour upgrade
    return True

def down():
    """Migration downgrade: 1.1.0 -> 1.0.0"""
    # Code pour rollback
    return True

def validate():
    """Validation post-migration"""
    # Tests de validation
    return True
```

### Exécuter les migrations

```bash
# Upgrade vers la dernière version
python scripts/migrations/migration_manager.py upgrade

# Upgrade vers version spécifique
python scripts/migrations/migration_manager.py upgrade --version 1.1.0

# Downgrade
python scripts/migrations/migration_manager.py downgrade --version 1.0.0

# Status
python scripts/migrations/migration_manager.py status
```

## Déploiement

### Déploiement automatique avec script

```bash
# Déploiement avec auto-incrémentation PATCH
./scripts/deploy.sh

# Déploiement vers version spécifique
./scripts/deploy.sh 1.1.0 production

# Déploiement staging
./scripts/deploy.sh 1.1.0 staging
```

### Étapes du déploiement

1. ✅ Validation de l'environnement
2. ✅ Exécution des tests
3. ✅ Mise à jour de la version
4. ✅ Exécution des migrations
5. ✅ Commit et tag
6. ✅ Push vers GitHub
7. ✅ Auto-déploiement Render
8. ✅ Validation post-deploy

### Déploiement manuel

```bash
# 1. Tests
pytest tests/

# 2. Mise à jour version
vim src/api/version.py

# 3. Migrations
python scripts/migrations/migration_manager.py upgrade

# 4. Commit
git add .
git commit -m "chore: Release v1.1.0"

# 5. Tag
git tag -a v1.1.0 -m "Release v1.1.0"

# 6. Push
git push origin main
git push origin v1.1.0

# 7. Render déploie automatiquement
```

## Rollback

### Rollback rapide

```bash
# Rollback vers version précédente
git checkout v1.0.0
python scripts/migrations/migration_manager.py downgrade --version 1.0.0
git push origin main --force
```

### Rollback avec script

```bash
# Le script gère automatiquement:
# - Checkout du tag
# - Downgrade des migrations
# - Push forcé
./scripts/rollback.sh 1.0.0
```

### Procédure de rollback complète

1. **Identifier la version stable**
   ```bash
   git tag -l
   ```

2. **Backup de la BDD** (si migrations de schéma)
   ```bash
   # Sur Render
   pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
   ```

3. **Rollback code**
   ```bash
   git checkout v1.0.0
   ```

4. **Rollback migrations**
   ```bash
   python scripts/migrations/migration_manager.py downgrade --version 1.0.0
   ```

5. **Redéployer**
   ```bash
   git push origin main --force
   ```

6. **Valider**
   ```bash
   curl https://projetetudeaccidentfrance.onrender.com/api/v1/version
   ```

## API Versioning

### Versioning d'URL

L'API utilise le versioning dans l'URL:

```
/api/v1/accidents
/api/v2/accidents  # Future version
```

### Maintien des versions

- **v1**: Supportée, maintenance active
- **v2**: En développement (quand nécessaire)

### Deprecation

Quand une version d'API est dépréciée:

1. Annoncer 6 mois à l'avance
2. Ajouter header `Deprecation: true`
3. Fournir guide de migration
4. Maintenir pendant période de transition
5. Sunset après deadline

```python
# Exemple de deprecation
@app.get("/api/v1/old-endpoint")
async def old_endpoint(response: Response):
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "2026-12-31"
    response.headers["Link"] = "</api/v2/new-endpoint>; rel='successor-version'"
    return {"message": "This endpoint is deprecated"}
```

## Bonnes Pratiques

### ✅ À FAIRE

1. **Versionner atomiquement**: 1 changement = 1 version
2. **Tester avant deploy**: Tests unitaires + intégration
3. **Documenter les changements**: CHANGELOG détaillé
4. **Backward compatibility**: Éviter les breaking changes
5. **Migrations réversibles**: Toujours écrire `down()`
6. **Backup avant migration**: Surtout pour schéma BDD
7. **Valider après deploy**: Tests automatiques
8. **Tags Git**: Toujours tagguer les releases

### ❌ À ÉVITER

1. ❌ Modifier du code sans bump de version
2. ❌ Breaking changes sans MAJOR bump
3. ❌ Déployer sans tests
4. ❌ Migrations sans rollback
5. ❌ Sauter des versions (1.0.0 → 1.2.0)
6. ❌ Déployer directement en prod sans staging
7. ❌ Modifier l'historique Git après release

### Checklist de Release

```markdown
## Pre-Release
- [ ] Tous les tests passent
- [ ] Documentation à jour
- [ ] CHANGELOG mis à jour
- [ ] Migrations créées si nécessaire
- [ ] Code review effectué
- [ ] Branche mergée dans main

## Release
- [ ] Version bumped dans src/api/version.py
- [ ] Tag Git créé
- [ ] Push vers GitHub
- [ ] Déploiement Render réussi

## Post-Release
- [ ] Validation API accessible
- [ ] Version correcte déployée
- [ ] Dashboard fonctionnel
- [ ] Monitoring actif
- [ ] Annonce de release (si MAJOR/MINOR)
```

## Endpoints de Version

L'API expose plusieurs endpoints pour gérer les versions:

```bash
# Informations de version
GET /api/v1/version

# Changelog
GET /api/v1/version/changelog

# Dernière version
GET /api/v1/version/latest

# Compatibilité client
GET /api/v1/version/compatibility/{client_version}

# Chemin de migration
GET /api/v1/version/migration?from_version=1.0.0&to_version=1.1.0

# Versions supportées
GET /api/v1/version/supported

# Health check avec version
GET /api/v1/version/health
```

## Monitoring des Versions

### Render Dashboard

- https://dashboard.render.com
- Monitoring des déploiements
- Logs en temps réel
- Rollback rapide

### API Monitoring

```bash
# Version déployée
curl https://projetetudeaccidentfrance.onrender.com/api/v1/version

# Health check
curl https://projetetudeaccidentfrance.onrender.com/api/v1/version/health
```

## Références

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [API Versioning Best Practices](https://restfulapi.net/versioning/)

## Contact

Pour questions sur le versioning:
- GitHub Issues: https://github.com/Gouesse05/projetetudeaccidentfrance/issues
- Documentation: https://projetetudeaccidentfrance.onrender.com/docs
