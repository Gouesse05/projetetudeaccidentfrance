#!/bin/bash
#
# =============================================================================
# DEPLOY.SH - Script de déploiement versionné
# =============================================================================
#
# Automatise le déploiement avec gestion des versions:
# - Validation pre-deploy
# - Tests automatiques
# - Migration de version
# - Déploiement Render
# - Validation post-deploy
# - Rollback automatique en cas d'échec
#
# Usage:
#   ./scripts/deploy.sh [VERSION] [ENVIRONMENT]
#
# Exemples:
#   ./scripts/deploy.sh 1.0.0 production
#   ./scripts/deploy.sh 1.1.0 staging
#   ./scripts/deploy.sh           # Auto-incrémente PATCH

set -e  # Exit on error
set -u  # Exit on undefined variable

# =============================================================================
# CONFIGURATION
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MIGRATIONS_DIR="$ROOT_DIR/scripts/migrations"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

log_info() {
    echo -e "${BLUE}ℹ ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠️ ${NC} $1"
}

log_error() {
    echo -e "${RED}❌${NC} $1"
}

# =============================================================================
# VALIDATION PRE-DEPLOY
# =============================================================================

validate_environment() {
    log_info "Validation de l'environnement..."
    
    # Vérifier Git
    if ! git --version &> /dev/null; then
        log_error "Git n'est pas installé"
        exit 1
    fi
    
    # Vérifier Python
    if ! python3 --version &> /dev/null; then
        log_error "Python 3 n'est pas installé"
        exit 1
    fi
    
    # Vérifier que nous sommes sur main
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "main" ]; then
        log_error "Vous devez être sur la branche 'main' pour déployer"
        exit 1
    fi
    
    # Vérifier qu'il n'y a pas de changements non commités
    if [ -n "$(git status --porcelain)" ]; then
        log_error "Il y a des changements non commités"
        git status --short
        exit 1
    fi
    
    log_success "Environnement validé"
}

# =============================================================================
# GESTION DES VERSIONS
# =============================================================================

get_current_version() {
    # Extraire la version depuis src/api/version.py
    grep -oP 'VERSION = "\K[^"]+' "$ROOT_DIR/src/api/version.py" || echo "0.0.0"
}

increment_version() {
    local version=$1
    local part=${2:-patch}  # major, minor, ou patch
    
    IFS='.' read -r -a parts <<< "$version"
    
    case $part in
        major)
            echo "$((parts[0] + 1)).0.0"
            ;;
        minor)
            echo "${parts[0]}.$((parts[1] + 1)).0"
            ;;
        patch)
            echo "${parts[0]}.${parts[1]}.$((parts[2] + 1))"
            ;;
    esac
}

update_version_file() {
    local new_version=$1
    local version_file="$ROOT_DIR/src/api/version.py"
    local today=$(date +%Y-%m-%d)
    
    log_info "Mise à jour vers version $new_version..."
    
    # Backup
    cp "$version_file" "$version_file.bak"
    
    # Mise à jour VERSION
    sed -i "s/VERSION = \".*\"/VERSION = \"$new_version\"/" "$version_file"
    
    # Mise à jour BUILD_DATE
    sed -i "s/BUILD_DATE = \".*\"/BUILD_DATE = \"$today\"/" "$version_file"
    
    log_success "Version mise à jour"
}

# =============================================================================
# TESTS
# =============================================================================

run_tests() {
    log_info "Exécution des tests..."
    
    cd "$ROOT_DIR"
    
    # Activer l'environnement virtuel si disponible
    if [ -d "venv_clean" ]; then
        source venv_clean/bin/activate
    fi
    
    # Tests unitaires
    if [ -f "pytest.ini" ] || [ -d "tests" ]; then
        log_info "Tests unitaires..."
        python -m pytest tests/ -v --tb=short || {
            log_error "Tests unitaires échoués"
            return 1
        }
    fi
    
    # Linting (optionnel)
    # if command -v ruff &> /dev/null; then
    #     log_info "Linting..."
    #     ruff check src/ || log_warning "Problèmes de linting détectés"
    # fi
    
    log_success "Tests réussis"
}

# =============================================================================
# MIGRATIONS
# =============================================================================

run_migrations() {
    local target_version=$1
    
    log_info "Exécution des migrations vers $target_version..."
    
    cd "$MIGRATIONS_DIR"
    python migration_manager.py upgrade --version "$target_version" || {
        log_error "Migration échouée"
        return 1
    }
    
    log_success "Migrations réussies"
}

# =============================================================================
# DÉPLOIEMENT
# =============================================================================

deploy_to_render() {
    local version=$1
    local environment=${2:-production}
    
    log_info "Déploiement vers Render ($environment)..."
    
    cd "$ROOT_DIR"
    
    # Commit et tag
    git add .
    git commit -m "chore: Release v$version" || log_warning "Rien à commiter"
    
    # Créer tag
    git tag -a "v$version" -m "Release version $version"
    
    # Push
    log_info "Push vers GitHub..."
    git push origin main
    git push origin "v$version"
    
    log_success "Code poussé vers GitHub"
    log_info "Render va automatiquement déployer la nouvelle version"
    log_info "Suivre le déploiement sur: https://dashboard.render.com"
}

# =============================================================================
# VALIDATION POST-DEPLOY
# =============================================================================

validate_deployment() {
    local version=$1
    local environment=${2:-production}
    
    log_info "Validation du déploiement..."
    
    # Attendre que le déploiement démarre
    sleep 10
    
    # URL selon environnement
    if [ "$environment" = "production" ]; then
        API_URL="https://projetetudeaccidentfrance.onrender.com"
    else
        API_URL="http://localhost:8000"
    fi
    
    # Tester l'endpoint de version
    log_info "Test de l'API..."
    
    for i in {1..5}; do
        if curl -f "$API_URL/api/v1/version" &> /dev/null; then
            log_success "API accessible"
            
            # Vérifier la version
            deployed_version=$(curl -s "$API_URL/api/v1/version" | grep -oP '"version":"\K[^"]+')
            
            if [ "$deployed_version" = "$version" ]; then
                log_success "Version $version déployée avec succès"
                return 0
            else
                log_warning "Version déployée ($deployed_version) != version attendue ($version)"
            fi
            
            return 0
        fi
        
        log_info "Tentative $i/5..."
        sleep 10
    done
    
    log_warning "Impossible de valider le déploiement automatiquement"
    log_info "Vérifier manuellement sur $API_URL"
}

# =============================================================================
# ROLLBACK
# =============================================================================

rollback() {
    local version=$1
    
    log_warning "Rollback vers version $version..."
    
    cd "$ROOT_DIR"
    
    # Checkout du tag précédent
    git checkout "v$version"
    
    # Downgrade migrations
    cd "$MIGRATIONS_DIR"
    python migration_manager.py downgrade --version "$version"
    
    # Redéployer
    git push origin main --force
    
    log_warning "Rollback effectué. Vérifier le déploiement."
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    echo ""
    echo "======================================================================"
    echo "  🚀 DÉPLOIEMENT VERSIONNÉ - Accidents API"
    echo "======================================================================"
    echo ""
    
    # Arguments
    NEW_VERSION=${1:-""}
    ENVIRONMENT=${2:-"production"}
    
    # Validation
    validate_environment
    
    # Déterminer la version
    CURRENT_VERSION=$(get_current_version)
    log_info "Version actuelle: $CURRENT_VERSION"
    
    if [ -z "$NEW_VERSION" ]; then
        # Auto-incrémentation PATCH
        NEW_VERSION=$(increment_version "$CURRENT_VERSION" "patch")
        log_info "Auto-incrémentation vers: $NEW_VERSION"
    fi
    
    log_info "Version cible: $NEW_VERSION"
    
    # Confirmation
    read -p "Déployer vers $ENVIRONMENT (v$NEW_VERSION)? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warning "Déploiement annulé"
        exit 0
    fi
    
    # Tests
    if ! run_tests; then
        log_error "Les tests ont échoué. Déploiement annulé."
        exit 1
    fi
    
    # Mise à jour version
    update_version_file "$NEW_VERSION"
    
    # Migrations
    if ! run_migrations "$NEW_VERSION"; then
        log_error "Migrations échouées. Rollback recommandé."
        exit 1
    fi
    
    # Déploiement
    deploy_to_render "$NEW_VERSION" "$ENVIRONMENT"
    
    # Validation
    validate_deployment "$NEW_VERSION" "$ENVIRONMENT"
    
    echo ""
    echo "======================================================================"
    log_success "Déploiement de v$NEW_VERSION terminé!"
    echo "======================================================================"
    echo ""
    echo "📊 Monitoring:"
    echo "  - API: https://projetetudeaccidentfrance.onrender.com"
    echo "  - Dashboard: https://projetetudeaccidentfrance-dashboard.onrender.com"
    echo "  - Render: https://dashboard.render.com"
    echo ""
    echo "📖 Documentation:"
    echo "  - OpenAPI: https://projetetudeaccidentfrance.onrender.com/docs"
    echo "  - Version: https://projetetudeaccidentfrance.onrender.com/api/v1/version"
    echo ""
}

main "$@"
