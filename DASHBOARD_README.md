# 📊 Streamlit Dashboard - Accidents Routiers

Interactive visualization dashboard for accident data analysis.

---

## 🚀 Démarrage rapide

### Option 1: Script bash
```bash
./run_dashboard.sh
```

### Option 2: Commande directe
```bash
source venv_clean/bin/activate
streamlit run streamlit_app.py
```

### Accès
**URL**: http://localhost:8501

---

## 📄 Pages du Dashboard

### 1. 🏠 Accueil
- Vue d'ensemble du projet
- Métriques clés
- Architecture
- Instructions démarrage

### 2. 📊 Données
- Exploration des données
- Aperçu et statistiques
- Distributions des variables
- Histogrammes interactifs

### 3. 📈 Statistiques
- Matrice de corrélation heatmap
- Corrélations entre variables
- Statistiques par catégorie
- Analyse descriptive

### 4. 🤖 Machine Learning
- Feature importance
- Résultats Random Forest
- Métriques de performance:
  - Accuracy
  - Precision
  - Recall
  - F1 Score

### 5. 🔍 Dimensionalité
- Analyse PCA
- Variance expliquée
- K-Means clustering
- Silhouette score

---

## 🛠 Fonctionnalités

✅ **Responsive Design** - S'adapte à tous les écrans  
✅ **Interactive Charts** - Plotly pour les graphiques interactifs  
✅ **Cached Data** - Performance optimisée  
✅ **Real-time Updates** - Rafraîchissement instant  
✅ **Sidebar Navigation** - Navigation facile  

---

## 📦 Dépendances

```
streamlit>=1.28.0
plotly>=5.17.0
pandas>=1.5.0
numpy>=1.26.0
scikit-learn>=1.5.0
```

Installation automatique via:
```bash
pip install streamlit plotly
```

---

## 🎨 Customization

### Changer les couleurs
Éditer le CSS custom au début de `streamlit_app.py`:
```python
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;  # Modifier ici
        ...
    }
</style>
""", unsafe_allow_html=True)
```

### Ajouter des pages
1. Ajouter un nouveau `elif` dans la section navigation
2. Créer le contenu avec st.* widgets
3. Mettre à jour le radio button

---

## 🔗 Intégration avec API

Le dashboard peut être connecté à l'API FastAPI:

```python
import requests

response = requests.get('http://localhost:8000/api/correlation')
data = response.json()
```

---

## 📊 Données de Test

Le dashboard utilise actuellement des données aléatoires pour démonstration.

Pour utiliser des vraies données:

```python
from analyses.data_cleaning import load_accident_data
df = load_accident_data('data/raw')
```

---

## 🚀 Déploiement

### Streamlit Cloud
```bash
git push origin main
```
Connecter le repo à Streamlit Cloud

### Render
```bash
# Créer un nouveau web service
# Repository: projetetudeaccidentfrance
# Build command: pip install -r requirements.txt
# Start command: streamlit run streamlit_app.py --server.port=$PORT
```

### Local
```bash
./run_dashboard.sh
```

---

## 🐛 Troubleshooting

### Port déjà utilisé
```bash
lsof -i :8501
kill -9 <PID>
```

### Cache issues
```bash
streamlit cache clear
```

### Import errors
```bash
source venv_clean/bin/activate
pip install -r requirements.txt
```

---

## 📝 Notes

- Données actuellement aléatoires (pour démo)
- À connecter avec données réelles du pipeline
- Peut être déployé indépendamment de l'API
- Utilise caching pour performance

---

**Status**: ✅ Phase 5 - Production Ready
