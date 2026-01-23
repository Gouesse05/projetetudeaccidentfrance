# 📊 Documentation des Endpoints d'Analyse Avancée

## Vue d'ensemble

Les endpoints d'analyse avancée permettent d'effectuer des analyses statistiques, de réduction dimensionnelle et de machine learning directement via l'API REST.

## Architecture

```
src/analyses/
├── data_cleaning.py              # Nettoyage et préparation des données
├── statistical_analysis.py        # Analyses statistiques (corrélations, tests)
├── dimensionality_reduction.py    # PCA, LDA, clustering, MCA, CA
└── machine_learning.py            # Random Forest, H2O GLM, feature selection

src/api/
└── analysis_endpoints.py          # Endpoints FastAPI pour les analyses
```

## Installation

1. **Installer les dépendances**:
```bash
pip install -r requirements.txt
```

Les packages principaux ajoutés:
- `statsmodels>=0.13.5` - Modèles statistiques
- `prince>=0.10.0` - MCA et CA
- `h2o>=3.42.0.1` - Machine Learning distribué

2. **Lancer l'API**:
```bash
cd /home/sdd/projetetudeapi
source venv/bin/activate
uvicorn src.api.main:app --reload --port 8000
```

3. **Accéder à la documentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Modules d'Analyse

### 1. Data Cleaning (`data_cleaning.py`)

Charge et nettoie les données d'accidents routiers.

**Fonctions principales**:

- `load_accident_data(data_path)` - Charge les 5 CSV
- `clean_lieux(df)` - Nettoie la table lieux
- `clean_usagers(df)` - Nettoie la table usagers
- `clean_vehicules(df)` - Nettoie la table véhicules
- `clean_all_data(data_path)` - Nettoyage complet
- `get_data_quality_report(data)` - Rapport de qualité
- `merge_datasets(data)` - Fusion des tables

**Exemple**:
```python
from src.analyses.data_cleaning import clean_all_data, get_data_quality_report

data = clean_all_data('/path/to/data')
quality = get_data_quality_report(data)
print(f"Données: {quality['lieux']['rows']} accidents")
```

### 2. Statistical Analysis (`statistical_analysis.py`)

Analyses statistiques et tests d'hypothèse.

**Fonctions principales**:

- `correlation_analysis(df)` - Matrice de corrélation
- `spearmans_correlation(df, col1, col2)` - Corrélation de Spearman
- `kendalls_correlation(df, col1, col2)` - Corrélation de Kendall
- `chi2_test(df, col1, col2)` - Test du chi-2 (indépendance)
- `ttest_samples(df, col1, col2, group_col)` - Test t (moyennes)
- `bartlett_test(df, col, group_col)` - Homogénéité des variances
- `linear_regression(df, dep_var, indep_vars)` - Régression OLS
- `logistic_regression(df, dep_var, indep_vars)` - Régression logistique
- `descriptive_statistics(df)` - Statistiques descriptives

**Exemple**:
```python
from src.analyses.statistical_analysis import correlation_analysis

corr = correlation_analysis(df)
# Retourne: matrice de corrélation Pearson
```

### 3. Dimensionality Reduction (`dimensionality_reduction.py`)

Réduction de dimensionnalité et clustering.

**Fonctions principales**:

#### PCA (Analyse en Composantes Principales)
```python
from src.analyses.dimensionality_reduction import pca_analysis

result = pca_analysis(df, n_components=2)
# result['explained_variance'] - Variance expliquée
# result['components'] - Vecteurs propres
# result['loadings'] - Loadings des variables
```

#### LDA (Analyse Discriminante Linéaire)
```python
from src.analyses.dimensionality_reduction import lda_analysis

result = lda_analysis(df, numerical_cols, target_col, n_components=2)
# result['explained_variance_ratio'] - Variance expliquée
# result['classes'] - Classes distinctes
```

#### K-Means Clustering
```python
from src.analyses.dimensionality_reduction import kmeans_clustering

result = kmeans_clustering(df, n_clusters=3)
# result['cluster_labels'] - Assignation des clusters
# result['inertia'] - Inertie (WSS)
# result['silhouette'] - Score de silhouette
```

#### Clustering Hiérarchique
```python
from src.analyses.dimensionality_reduction import hierarchical_clustering

result = hierarchical_clustering(df, method='ward', n_clusters=3)
# result['linkage_matrix'] - Matrice de liaison
# result['cluster_labels'] - Assignation des clusters
```

#### MCA (Analyse des Correspondances Multiples)
```python
from src.analyses.dimensionality_reduction import mca_analysis

result = mca_analysis(df, categorical_cols=['col1', 'col2'])
# Nécessite: pip install prince
```

#### Courbe du Coude
```python
from src.analyses.dimensionality_reduction import elbow_curve

result = elbow_curve(df, max_clusters=10)
# result['inertias'] - Inertie pour chaque k
# Aide à déterminer le nombre optimal de clusters
```

### 4. Machine Learning (`machine_learning.py`)

Modèles d'apprentissage automatique.

**Fonctions principales**:

#### Random Forest Classifier
```python
from src.analyses.machine_learning import train_random_forest_classifier

result = train_random_forest_classifier(
    df, 
    feature_cols=['var1', 'var2'],
    target_col='target',
    test_size=0.2,
    n_estimators=100
)
# result['metrics'] - accuracy, precision, recall, f1, roc_auc
# result['feature_importance'] - Importance de chaque feature
```

#### Random Forest Regressor
```python
from src.analyses.machine_learning import train_random_forest_regressor

result = train_random_forest_regressor(
    df,
    feature_cols=['var1', 'var2'],
    target_col='target',
    test_size=0.2,
    n_estimators=100
)
# result['metrics'] - MSE, RMSE, MAE, R²
```

#### Feature Selection
```python
from src.analyses.machine_learning import feature_selection

result = feature_selection(df, feature_cols, target_col)
# result['feature_importance'] - Dict trié par importance
# result['top_features'] - Top 10 features
```

#### Model Comparison
```python
from src.analyses.machine_learning import model_comparison

result = model_comparison(df, feature_cols, target_col)
# Compare Random Forest et H2O GLM
# result['Random Forest'] - Métriques RF
# result['H2O GLM'] - Métriques H2O
```

## Endpoints API

### Data Quality

**POST** `/api/v1/analyses/data-quality`

Upload un CSV et obtient un rapport de qualité.

**Réponse**:
```json
{
  "rows": 68432,
  "columns": 15,
  "missing_values": {"col1": 0, "col2": 5},
  "duplicates": 0,
  "memory_usage_mb": 45.2
}
```

### Statistics

#### Correlation Matrix
**POST** `/api/v1/analyses/correlation`

```bash
curl -F "file=@data.csv" http://localhost:8000/api/v1/analyses/correlation
```

#### Descriptive Statistics
**POST** `/api/v1/analyses/descriptive-statistics`

```bash
curl -F "file=@data.csv" http://localhost:8000/api/v1/analyses/descriptive-statistics
```

**Réponse**:
```json
{
  "statistics": {
    "age": {
      "count": 68432,
      "mean": 42.5,
      "std": 15.3,
      "min": 18,
      "max": 95,
      "skewness": 0.2
    }
  },
  "count_variables": 10
}
```

#### Chi-2 Test
**POST** `/api/v1/analyses/chi2-test?col1=genre&col2=type_accident`

Test d'indépendance entre deux variables catégoriques.

#### Linear Regression
**POST** `/api/v1/analyses/linear-regression?dependent_var=prix&independent_vars=age,kilom,puissance`

**Réponse**:
```json
{
  "r_squared": 0.75,
  "adjusted_r_squared": 0.74,
  "f_statistic": 125.3,
  "f_pvalue": 0.000001,
  "coefficients": {
    "age": 0.05,
    "kilom": -0.0001
  }
}
```

### Dimensionality Reduction

#### PCA
**POST** `/api/v1/analyses/pca?n_components=2`

```bash
curl -F "file=@data.csv" "http://localhost:8000/api/v1/analyses/pca?n_components=2"
```

**Réponse**:
```json
{
  "explained_variance": [0.35, 0.20],
  "cumulative_variance": [0.35, 0.55],
  "n_components": 2
}
```

#### PCA Détaillée
**POST** `/api/v1/analyses/pca-detailed?n_components=2`

Retourne aussi: components, loadings

#### LDA
**POST** `/api/v1/analyses/lda?target_col=classe&numerical_vars=var1,var2,var3&n_components=2`

#### K-Means
**POST** `/api/v1/analyses/kmeans?n_clusters=3`

**POST** `/api/v1/analyses/kmeans-detailed?n_clusters=3`

#### Hierarchical Clustering
**POST** `/api/v1/analyses/hierarchical-clustering?n_clusters=3&method=ward`

Méthodes: `ward`, `complete`, `average`, `single`

#### Elbow Curve
**POST** `/api/v1/analyses/elbow-curve?max_clusters=10`

Utile pour déterminer le nombre de clusters optimal.

#### MCA
**POST** `/api/v1/analyses/mca?categorical_vars=col1,col2,col3`

Nécessite: `prince` installé

### Machine Learning

#### Random Forest Classifier
**POST** `/api/v1/analyses/random-forest-classifier?target_col=outcome&feature_vars=var1,var2,var3&n_estimators=100&test_size=0.2`

**Réponse**:
```json
{
  "metrics": {
    "accuracy": 0.85,
    "precision": 0.83,
    "recall": 0.87,
    "f1": 0.85,
    "roc_auc": 0.91
  },
  "feature_importance": {
    "var1": 0.35,
    "var2": 0.28,
    "var3": 0.15
  },
  "cross_val_mean": 0.84,
  "cross_val_std": 0.02,
  "n_features": 3,
  "n_classes": 2
}
```

#### Random Forest Regressor
**POST** `/api/v1/analyses/random-forest-regressor?target_col=price&feature_vars=var1,var2`

#### Feature Selection
**POST** `/api/v1/analyses/feature-selection?target_col=target&feature_vars=var1,var2,var3,var4,var5`

**Réponse**:
```json
{
  "feature_importance": {
    "var1": 0.45,
    "var2": 0.30,
    "var3": 0.15
  },
  "top_features": ["var1", "var2", "var3"],
  "feature_count": 5
}
```

#### Model Comparison
**POST** `/api/v1/analyses/model-comparison?target_col=target&feature_vars=var1,var2,var3`

Compare Random Forest et H2O GLM.

## Exemple d'Utilisation Complète

```bash
# 1. Vérifier la qualité des données
curl -F "file=@accidents.csv" http://localhost:8000/api/v1/analyses/data-quality

# 2. Corrélations
curl -F "file=@accidents.csv" http://localhost:8000/api/v1/analyses/correlation

# 3. Statistiques descriptives
curl -F "file=@accidents.csv" http://localhost:8000/api/v1/analyses/descriptive-statistics

# 4. PCA
curl -F "file=@accidents.csv" "http://localhost:8000/api/v1/analyses/pca?n_components=3"

# 5. K-Means clustering
curl -F "file=@accidents.csv" "http://localhost:8000/api/v1/analyses/kmeans?n_clusters=4"

# 6. Courbe du coude
curl -F "file=@accidents.csv" "http://localhost:8000/api/v1/analyses/elbow-curve?max_clusters=10"

# 7. Feature selection
curl -F "file=@accidents.csv" "http://localhost:8000/api/v1/analyses/feature-selection?target_col=gravite&feature_vars=age,vitesse,jour,heure"

# 8. Random Forest Classification
curl -F "file=@accidents.csv" "http://localhost:8000/api/v1/analyses/random-forest-classifier?target_col=mortel&feature_vars=age,vitesse,jour&n_estimators=100"
```

## Airflow Integration

### DAG: `analysis_pipeline`

**Schedule**: Dimanche 5h du matin

**Tasks**:
1. `start_analysis_pipeline` - Début
2. `load_and_clean_data` - Chargement et nettoyage
3. `statistical_analysis` - Analyses statistiques (parallèle)
4. `pca_analysis` - PCA (parallèle)
5. `clustering_analysis` - K-Means (parallèle)
6. `ml_analysis` - Random Forest (parallèle)
7. `generate_summary_report` - Synthèse
8. `end_analysis_pipeline` - Fin

**Outputs**:
- Modèles sauvegardés dans `data/models/`
- Rapports dans `data/reports/`

**Lancer manuellement**:
```bash
# Une fois Airflow démarré
airflow dags trigger accidents_analysis_pipeline
airflow dags list
airflow tasks list accidents_analysis_pipeline
```

## Performance & Limitations

### Timeouts
- **PCA/LDA/Clustering**: <30s pour 50k lignes
- **Random Forest**: <2min pour 50k lignes, 10 features
- **H2O GLM**: <5min pour 50k lignes

### Limitations
- **MCA**: Nécessite `prince` (optionnel)
- **H2O**: Nécessite installation H2O complète
- **Fichiers**: Max 100MB par upload

### Optimisations
- Réduire n_components pour PCA/LDA
- Réduire n_estimators pour Random Forest
- Filtrer les données avant upload (sample)

## Troubleshooting

### "prince library not installed"
```bash
pip install prince
```

### "H2O not initialized"
```python
import h2o
h2o.init(strict_version_check=False)
```

### Out of Memory
- Réduire la taille du dataset
- Réduire n_estimators
- Réduire n_components

## Intégration avec Phase 5b (SDK)

Le SDK Phase 5b pourra exposer ces analyses directement:

```python
from accidents_sdk import AccidentsAnalysis

analysis = AccidentsAnalysis()
pca_result = analysis.pca(df, n_components=2)
rf_result = analysis.train_classifier(df, target='outcome')
```

## Prochaines Étapes

1. **Dashboard Interactif** (Phase 7)
   - Visualiser PCA/MCA
   - Heatmaps clustering
   - Feature importance plots

2. **Modèles Sauvegardés**
   - Versioning des modèles
   - Tracking Airflow
   - Registry MLflow

3. **Prédictions en Temps Réel**
   - Charger modèles entrainés
   - Endpoint de prédiction
   - Monitoring performance

4. **AutoML**
   - Auto-tuning hyperparameters
   - Sélection automatique du modèle
   - Validation croisée

## Ressources

- 📚 [Scikit-learn Documentation](https://scikit-learn.org)
- 📊 [Statsmodels Documentation](https://www.statsmodels.org)
- 🎯 [H2O ML Platform](https://h2o.ai)
- 👑 [Prince Library (MCA/CA)](https://github.com/MaxHalford/prince)
