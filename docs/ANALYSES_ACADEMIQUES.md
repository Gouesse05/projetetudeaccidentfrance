# 📊 Guide Analyses Académiques - Accidents Routiers

## Contexte Projet

**Rôle**: Data Analyst au sein d'une société d'assurance  
**Objectif**: Analyser les bases de données Open Data des accidents corporels pour gérer le risque de responsabilité civile  
**Évaluation**: Projets "Traitement de Données", "Machine Learning", "Econométrie"

---

## 📋 Consignes Académiques

### Fond (Contenu)

✅ **Utiliser packages Python** (vus ou non) pour exploiter les données  
✅ **Analyses pertinentes** avec sens et intérêt (pas juste du code)  
✅ **Interpréter résultats** : déduire relations, tendances, patterns  
✅ **Expliciter chaque analyse** : objectif → mise en place → résultats  
✅ **Variables externes** :
   - Région (data.gouv.fr)
   - Densité/population (INSEE)
   - Analyse géographique pour zonier

### Forme (Présentation)

✅ **Notebook propre** : clair, précis, structuré, concis  
✅ **Commentaires et titres** de parties  
✅ **Conclusions et interprétations**  
✅ **Note PDF** en plus du notebook  
✅ **Code commenté** avec documentation

---

## 📊 Processus Classique d'Analyse Statistique

```
1. Nettoyage de données
   ├─ Compréhension format
   ├─ Analyse complétude
   ├─ Contrôles cohérence
   └─ Gestion anomalies

2. Jointure et enrichissement
   ├─ Variables externes (région, densité)
   ├─ Rapprochement données
   └─ Gestion doublons

3. Analyse descriptive
   ├─ Univariée (distributions)
   ├─ Bivariée (crosstab, corrélations)
   └─ Multivariée (clustering, ACP)

4. Modélisation
   ├─ Approche paramétrique (GLM)
   └─ Approche non-paramétrique (ML)

5. Résultats et interprétation
   ├─ Analyse coefficients
   ├─ Tests statistiques
   └─ Implications pratiques

6. Applications
   ├─ Prévisions
   ├─ Tarification
   └─ Gestion des risques
```

---

## 🎯 12 Sections du Notebook

### 1️⃣ **Chargement et Exploration**
- Charger datasets (5 fichiers accidents)
- Structure et dimensions
- Statistiques basiques

**Objectif**: Comprendre les données  
**Code**: `pd.read_csv()`, `.info()`, `.describe()`, `.head()`

---

### 2️⃣ **Nettoyage et Prétraitement**
- Analyse complétude (% valeurs manquantes)
- Doublons (identification et suppression)
- Incohérences (inter-variables)
- Corrections univariées/multivariées

**Métrique**: 
```
Avant nettoyage: X lignes, Y % manquant
Après nettoyage: X' lignes, Y'% manquant
```

---

### 3️⃣ **Intégration Variables Externes**
Ajouter:
- **Régions**: joindre communes → régions
- **Démographie**: population, densité (INSEE)
- **Géographie**: latitude/longitude (lieux)

**Validation**: Afficher % rapprochement réussi

---

### 4️⃣ **Analyse Univariée**
Pour chaque variable clé:
- Histogramme/distribution
- Statistiques (mean, median, std, quantiles)
- Cas particuliers (0, négatifs, outliers)

**Variables**: accidents/an, gravité, véhicules, personnes, heure, jour

---

### 5️⃣ **Analyse Bivariée et Multivariée**
- Crosstabs (jour × gravité, etc.)
- **Tests Chi-2** pour variables catégoriques
- **Correlations** (Pearson/Spearman) numériques
- **Visualisations** (heatmaps, scatter, boxplots)

**Exemple**:
```python
# Gravité par jour (test significativité)
crosstab = pd.crosstab(df['jour'], df['grav'])
chi2, p_val = stats.chi2_contingency(crosstab)
```

---

### 6️⃣ **Analyse Spatiale et Heatmaps**
- Top 20 communes dangereuses (par accidents)
- **Heatmap géographique**: latitude × longitude × accidents
- Densité zones urbaines vs rurales
- Clustering spatial (si coordonnées disponibles)

**Visualisation**:
```python
plt.hexbin(df['lat'], df['lon'], gridsize=30, cmap='YlOrRd')
```

---

### 7️⃣ **Clustering (Classification Non-Supervisée)**
- **K-Means**: grouper accidents par caractéristiques
  - Features: nombre véhicules, personnes, heure, etc.
  - Déterminer k optimal (elbow method)
- **Hierarchical clustering**: dendrogramme

**Interprétation**: Profil de chaque cluster

---

### 8️⃣ **Score de Danger par Commune**
Créer score composite (0-100):
```
Score = 50% × (accidents normalisés) 
       + 30% × (gravité moyenne)
       + 20% × (nombre personnes)
```

**Output**: Ranking communes (plus dangereuses d'abord)

---

### 9️⃣ **Analyse des Facteurs de Risque**
Corrélations avec accidents/gravité:
- ⏰ **Heure du jour** (pics matinaux, soir?)
- 📅 **Jour de semaine** (WE vs semaine?)
- 🌤️ **Météo** (si disponible)
- 🛣️ **Infrastructure** (type route)
- 🏙️ **Densité** (urbain vs rural)

**Test**: ANOVA ou Kruskal-Wallis selon distribution

---

### 🔟 **Modélisation: Approche Paramétrique (GLM)**
Prédire: Accident grave (gravité ≥ 3)?

```python
from sklearn.linear_model import LogisticRegression

y = (df['grav'] >= 3).astype(int)  # Variable cible
X = df[['nbv', 'nbp', 'mois', 'jour']]

model = LogisticRegression()
model.fit(X, y)
```

**Résultats**:
- Accuracy/AUC
- Coefficients (interprétation: impact variables)
- P-values (significativité)

---

### 1️⃣1️⃣ **Modélisation: Approche Non-Paramétrique (ML)**
Comparer modèles:
- **Random Forest** (importance variables)
- **Gradient Boosting** (meilleure performance?)
- **Neural Networks** (si données + complexes)

**Comparaison**:
```
Modèle           | Accuracy | AUC   | F1-Score
─────────────────┼──────────┼───────┼─────────
Logistic         |   0.78   | 0.82  |  0.65
Random Forest    |   0.85   | 0.89  |  0.74
Gradient Boost   |   0.87   | 0.91  |  0.76
```

---

### 1️⃣2️⃣ **Résultats, Interprétation et Recommandations**

**Synthèse des findings:**
1. Tendances temporelles (accidents augmentent? où?)
2. Zones critiques (communes/régions à surveiller)
3. Facteurs clés (heure, jour, infrastructure)
4. Patterns identifiés (qui cause les accidents graves?)

**Recommandations pour assurance:**
- 🎯 Zones de surprime (score danger > X)
- ⏰ Tarification horaire/jour
- 🚗 Surprime multi-véhicules
- 📍 Zonier géographique
- 📊 Score creditant (ajustement primes)

---

## 📈 Exemple: Analyse Complète d'une Variable

### Cas: Accidents par Heure

**1. Objectif**
Identifier les heures critiques pour prévention et tarification

**2. Méthodologie**
```python
# Extraire heure
df['heure'] = df['hrmn'].str[:2].astype(int)

# Agrégation
risque_heure = df.groupby('heure').agg({
    'Num_Acc': 'count',
    'grav': 'mean',
    'nbp': 'sum'
}).rename(columns={...})

# Visualisation
plt.figure(figsize=(12, 5))
plt.plot(risque_heure.index, risque_heure['Num_Acc'], marker='o')
plt.xlabel('Heure du jour')
plt.ylabel('Nombre d\'accidents')
plt.title('Profil horaire des accidents')
plt.grid(True)
```

**3. Résultats**
- Heures critiques: 8h (trajet travail), 17-19h (retour)
- Gravité: pics différents (24h en campagne?)
- Pattern: week-end ≠ semaine

**4. Interprétation**
- Surcharge réseau certaines heures
- Fatigue/vigilance à 23h?
- Conditions météo variables?

**5. Implication**
- Primes réduites heures creuses
- Campagnes prévention aux heures critiques
- Incitation trajets hors-pics

---

## 🛠️ Stack Technique Recommandée

```python
# Data
import pandas as pd
import numpy as np

# Visualisation
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Analyse
from scipy import stats
from scipy.spatial.distance import pdist, squareform

# ML
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

# Autres
import warnings
warnings.filterwarnings('ignore')
```

---

## 📝 Checklist Notebook

- [ ] Introduction et contexte
- [ ] Chargement données
- [ ] Exploration (dimensions, types)
- [ ] Nettoyage (complétude, doublons, outliers)
- [ ] Variables externes intégrées
- [ ] Analyses univariées (distributions, stats)
- [ ] Analyses bivariées (crosstabs, corrélations)
- [ ] Analyses multivariées (clustering, ACP?)
- [ ] Analyse spatiale (heatmaps, communes)
- [ ] Score de danger calculé et rankingé
- [ ] Modèle GLM (logistic regression)
- [ ] Modèles ML (Random Forest, XGBoost)
- [ ] Comparaison modèles
- [ ] Résultats interprétés
- [ ] Recommandations pour assurance
- [ ] Conclusions
- [ ] Code commenté et documenté

---

## 📄 Structure Note PDF

```
1. Résumé exécutif (1 page)
   - Question posée
   - Données utilisées
   - Findings principaux
   - Recommandations

2. Méthodologie (1-2 pages)
   - Sources données
   - Processus nettoyage
   - Variables externes
   - Approches analytiques

3. Résultats (5-10 pages)
   - Graphiques avec captions
   - Analyses statistiques
   - Interprétations
   - Tableaux clés

4. Recommandations (1-2 pages)
   - Pour la tarification
   - Pour la prévention
   - Pour la gestion des risques
   - Limitations et perspectives

5. Annexe technique
   - Détails nettoyage
   - Formules modèles
   - Références
```

---

## 💡 Conseils de Rédaction

✅ **Clarté**: Chaque figure doit être explicite (titre, axes, légende)  
✅ **Concision**: Aller à l'essentiel, pas de redondance  
✅ **Interprétation**: Toujours expliquer le "pourquoi"  
✅ **Critique**: Souligner limitations et hypothèses  
✅ **Rigueur**: Tests stats, p-values, intervalle confiance  
✅ **Actionnable**: Recommandations concrètes pour business

---

## 🎓 Évaluation (ce que les profs regardent)

| Critère | Points | Détails |
|---------|--------|---------|
| Fond | 60% | Analyses pertinentes, interprétations, rigueur |
| Forme | 20% | Clarté, organisation, présentation |
| Technique | 15% | Python, modèles, visualisations |
| Innovation | 5% | Approches créatives, insights originales |

---

## 📚 Ressources

- [scikit-learn documentation](https://scikit-learn.org)
- [Pandas for data analysis](https://pandas.pydata.org)
- [Seaborn visualization](https://seaborn.pydata.org)
- [Statistical tests with SciPy](https://docs.scipy.org/doc/scipy/)
- [INSEE données](https://www.insee.fr)
- [data.gouv.fr open data](https://www.data.gouv.fr)

---

**Bonne chance! Faites du code propre et des analyses pertinentes.** 🚀
