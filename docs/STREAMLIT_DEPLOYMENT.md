# Guide de Déploiement Streamlit sur Render

## Configuration du Service Streamlit

### 1. Créer un Nouveau Web Service sur Render

1. Aller sur https://dashboard.render.com
2. Cliquer sur **"New +"** → **"Web Service"**
3. Connecter votre repository GitHub: `Gouesse05/projetetudeaccidentfrance`

### 2. Configuration du Service

**Paramètres de base:**
- **Name**: `accidents-dashboard-streamlit` (ou votre choix)
- **Region**: Choisir la région la plus proche
- **Branch**: `main`
- **Root Directory**: laisser vide ou `.`
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: 
  ```bash
  pip install -r requirements-streamlit.txt
  ```

- **Start Command**:
  ```bash
  streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
  ```

**Instance Type:**
- Free tier: OK pour démonstration
- Starter ($7/mois): Recommandé pour production

### 3. Variables d'Environnement (Optionnelles)

Si votre dashboard se connecte à l'API:

```
API_BASE_URL=https://projetetudeaccidentfrance.onrender.com
```

### 4. Déploiement

1. Cliquer sur **"Create Web Service"**
2. Render va:
   - Cloner le repo
   - Installer les dépendances
   - Lancer Streamlit
3. Attendre 5-10 minutes pour le premier build

### 5. Accès au Dashboard

Une fois déployé, votre dashboard sera accessible à:
```
https://accidents-dashboard-streamlit.onrender.com
```

## Commandes Utiles

### Test Local

```bash
# Installer les dépendances Streamlit
pip install -r requirements-streamlit.txt

# Lancer localement
streamlit run streamlit_app.py

# Accessible sur http://localhost:8501
```

### Logs de Déploiement

1. Dans le dashboard Render
2. Onglet **"Logs"**
3. Vérifier que Streamlit démarre sur le bon port

### Dépannage

**Port binding error:**
- Vérifier que la commande start utilise `$PORT`
- Render assigne dynamiquement le port

**Dépendances manquantes:**
- Vérifier `requirements-streamlit.txt`
- S'assurer que toutes les bibliothèques sont listées

**Memory exceeded:**
- Passer au plan Starter (512 MB → 2 GB RAM)
- Optimiser le chargement des données

## Auto-Deploy

Le dashboard se redéploiera automatiquement à chaque push sur la branche `main`.

Pour désactiver:
- Settings → Auto-Deploy → Off

## Architecture Recommandée

```
API Backend (FastAPI)     Dashboard (Streamlit)
↓                         ↓
projetetudeaccidentfrance → Consomme l'API
:8000                      :8501
```

Le dashboard Streamlit peut appeler l'API FastAPI pour obtenir des données réelles.

## URLs Finales

- **API**: https://projetetudeaccidentfrance.onrender.com
- **Dashboard**: https://accidents-dashboard-streamlit.onrender.com (à configurer)
- **Docs API**: https://projetetudeaccidentfrance.onrender.com/docs
