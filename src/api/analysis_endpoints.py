"""
Endpoints API pour les analyses avancées.
Expose les modèles PCA, MCA, clustering, statistiques, ML.
"""

from fastapi import APIRouter, HTTPException, File, UploadFile, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
import io

# Imports des modules d'analyse
from src.analyses.data_cleaning import (
    load_accident_data, clean_all_data, get_data_quality_report, merge_datasets
)
from src.analyses.statistical_analysis import (
    correlation_analysis, descriptive_statistics, chi2_test,
    linear_regression, logistic_regression
)
from src.analyses.dimensionality_reduction import (
    pca_analysis, lda_analysis, kmeans_clustering, 
    hierarchical_clustering, mca_analysis, elbow_curve
)
from src.analyses.machine_learning import (
    train_random_forest_classifier, train_random_forest_regressor,
    feature_selection, model_comparison
)

# Créer le routeur
router = APIRouter(prefix="/api/v1/analyses", tags=["analyses"])


# ==================== Modèles Pydantic ====================

class DataQualityResponse(BaseModel):
    """Réponse de qualité des données"""
    lieux: Dict[str, Any] = Field(...)
    usagers: Dict[str, Any] = Field(...)
    vehicules: Dict[str, Any] = Field(...)
    charge: Dict[str, Any] = Field(...)
    caracteristiques: Dict[str, Any] = Field(...)


class PCAResponse(BaseModel):
    """Réponse de l'analyse PCA"""
    explained_variance: List[float]
    cumulative_variance: List[float]
    n_components: int


class ClusteringResponse(BaseModel):
    """Réponse du clustering"""
    n_clusters: int
    method: str
    silhouette_score: Optional[float] = None


class DescriptiveStatsResponse(BaseModel):
    """Statistiques descriptives"""
    statistics: Dict[str, Dict[str, float]]
    count_variables: int


class CorrelationResponse(BaseModel):
    """Matrice de corrélation"""
    correlation_matrix: Dict[str, Dict[str, float]]


# ==================== Endpoints Data Cleaning ====================

@router.post("/data-quality")
async def check_data_quality(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Vérifie la qualité des données uploadées.
    
    Accepte un fichier CSV et retourne un rapport de qualité.
    """
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')), delimiter=";")
        
        return {
            'rows': len(df),
            'columns': len(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicates': int(df.duplicated().sum()),
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
            'column_dtypes': df.dtypes.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Endpoints Statistics ====================

@router.post("/correlation")
async def get_correlation(file: UploadFile = File(...)) -> CorrelationResponse:
    """
    Calcule la matrice de corrélation des variables numériques.
    """
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')), delimiter=";")
        
        corr_matrix = correlation_analysis(df)
        
        return CorrelationResponse(
            correlation_matrix=corr_matrix.to_dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/descriptive-statistics")
async def get_descriptive_stats(file: UploadFile = File(...)) -> DescriptiveStatsResponse:
    """
    Calcule les statistiques descriptives.
    """
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')), delimiter=";")
        
        stats = descriptive_statistics(df)
        
        return DescriptiveStatsResponse(
            statistics=stats,
            count_variables=len(stats)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/chi2-test")
async def perform_chi2_test(
    file: UploadFile = File(...),
    col1: str = Query(...),
    col2: str = Query(...)
) -> Dict[str, Any]:
    """
    Effectue un test du chi-2 d'indépendance entre deux variables catégoriques.
    """
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')), delimiter=";")
        
        result = chi2_test(df, col1, col2)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/linear-regression")
async def perform_linear_regression(
    file: UploadFile = File(...),
    dependent_var: str = Query(...),
    independent_vars: str = Query(...)  # CSV séparé par virgule
) -> Dict[str, Any]:
    """
    Effectue une régression linéaire OLS.
    
    independent_vars: Variables indépendantes séparées par virgule (ex: "var1,var2,var3")
    """
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')), delimiter=";")
        
        ind_vars = [v.strip() for v in independent_vars.split(",")]
        result = linear_regression(df, dependent_var, ind_vars)
        
        # Retourner seulement les résultats sérialisables
        return {
            'r_squared': result['r_squared'],
            'adjusted_r_squared': result['adjusted_r_squared'],
            'f_statistic': result['f_statistic'],
            'f_pvalue': result['f_pvalue'],
            'aic': result['aic'],
            'bic': result['bic'],
            'coefficients': result['coefficients'],
            'pvalues': result['pvalues']
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Endpoints Dimensionality Reduction ====================

@router.post("/pca", response_model=PCAResponse)
async def perform_pca(
    file: UploadFile = File(...),
    n_components: int = Query(2)
) -> PCAResponse:
    """
    Effectue une Analyse en Composantes Principales (PCA).
    
    n_components: Nombre de composantes principales (défaut: 2)
    """
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')), delimiter=";")
        
        result = pca_analysis(df, n_components=n_components)
        
        return PCAResponse(
            explained_variance=result['explained_variance'],
            cumulative_variance=result['cumulative_variance'],
            n_components=n_components
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pca-detailed")
async def perform_pca_detailed(
    file: UploadFile = File(...),
    n_components: int = Query(2)
) -> Dict[str, Any]:
    """
    Effectue PCA et retourne tous les détails (composantes, loadings, etc.)
    """
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')), delimiter=";")
        
        result = pca_analysis(df, n_components=n_components)
        
        # Convertir array en liste pour sérialisation JSON
        return {
            'explained_variance': result['explained_variance'],
            'explained_variance_ratio': result['explained_variance_ratio'],
            'cumulative_variance': result['cumulative_variance'],
            'components': result['components'],
            'loadings': result['loadings'],
            'n_components': n_components
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/lda")
async def perform_lda(
    file: UploadFile = File(...),
    target_col: str = Query(...),
    numerical_vars: str = Query(...),  # CSV séparé par virgule
    n_components: int = Query(2)
) -> Dict[str, Any]:
    """
    Effectue une Analyse Discriminante Linéaire (LDA).
    
    numerical_vars: Variables numériques séparées par virgule
    """
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')), delimiter=";")
        
        num_vars = [v.strip() for v in numerical_vars.split(",")]
        result = lda_analysis(df, num_vars, target_col, n_components)
        
        return {
            'explained_variance_ratio': result['explained_variance_ratio'],
            'cumulative_variance': result['cumulative_variance'],
            'n_components': min(n_components, len(result['classes']) - 1),
            'n_classes': len(result['classes']),
            'classes': [str(c) for c in result['classes']]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/kmeans")
async def perform_kmeans(
    file: UploadFile = File(...),
    n_clusters: int = Query(3)
) -> ClusteringResponse:
    """
    Effectue un clustering K-Means.
    
    n_clusters: Nombre de clusters (défaut: 3)
    """
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')), delimiter=";")
        
        result = kmeans_clustering(df, n_clusters=n_clusters)
        
        return ClusteringResponse(
            n_clusters=n_clusters,
            method='kmeans',
            silhouette_score=result.get('silhouette')
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/kmeans-detailed")
async def perform_kmeans_detailed(
    file: UploadFile = File(...),
    n_clusters: int = Query(3)
) -> Dict[str, Any]:
    """
    Effectue K-Means avec tous les détails (inertia, centroids, etc.)
    """
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')), delimiter=";")
        
        result = kmeans_clustering(df, n_clusters=n_clusters)
        
        return {
            'n_clusters': n_clusters,
            'inertia': result['inertia'],
            'silhouette_score': result['silhouette'],
            'centroids': result['centroids']
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/hierarchical-clustering")
async def perform_hierarchical_clustering(
    file: UploadFile = File(...),
    n_clusters: int = Query(3),
    method: str = Query("ward")
) -> ClusteringResponse:
    """
    Effectue un clustering hiérarchique.
    
    n_clusters: Nombre de clusters
    method: Méthode de liaison (ward, complete, average, single)
    """
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')), delimiter=";")
        
        result = hierarchical_clustering(df, method=method, n_clusters=n_clusters)
        
        return ClusteringResponse(
            n_clusters=n_clusters,
            method=method
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/elbow-curve")
async def get_elbow_curve(
    file: UploadFile = File(...),
    max_clusters: int = Query(10)
) -> Dict[str, Any]:
    """
    Calcule la courbe du coude pour K-Means.
    Utile pour déterminer le nombre optimal de clusters.
    """
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')), delimiter=";")
        
        result = elbow_curve(df, max_clusters=max_clusters)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/mca")
async def perform_mca(
    file: UploadFile = File(...),
    categorical_vars: str = Query(...)  # CSV séparé par virgule
) -> Dict[str, Any]:
    """
    Effectue une Analyse des Correspondances Multiples (MCA).
    
    categorical_vars: Variables catégoriques séparées par virgule
    """
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')), delimiter=";")
        
        cat_vars = [v.strip() for v in categorical_vars.split(",")]
        result = mca_analysis(df, cat_vars)
        
        if result.get('success', False):
            return {
                'inertia': result['inertia'],
                'n_components': result['n_components'],
                'columns_analyzed': result['columns']
            }
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'MCA failed'))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Endpoints Machine Learning ====================

@router.post("/random-forest-classifier")
async def train_rf_classifier(
    file: UploadFile = File(...),
    target_col: str = Query(...),
    feature_vars: str = Query(...),  # CSV séparé par virgule
    n_estimators: int = Query(100),
    test_size: float = Query(0.2)
) -> Dict[str, Any]:
    """
    Entraîne un Random Forest Classifier.
    
    feature_vars: Variables de feature séparées par virgule
    n_estimators: Nombre d'arbres
    test_size: Proportion du test set (0-1)
    """
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')), delimiter=";")
        
        feat_vars = [v.strip() for v in feature_vars.split(",")]
        result = train_random_forest_classifier(df, feat_vars, target_col, 
                                               test_size, n_estimators)
        
        return {
            'metrics': result['metrics'],
            'feature_importance': result['feature_importance'],
            'cross_val_mean': result['cross_val_mean'],
            'cross_val_std': result['cross_val_std'],
            'n_features': result['n_features'],
            'n_classes': result['n_classes']
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/random-forest-regressor")
async def train_rf_regressor(
    file: UploadFile = File(...),
    target_col: str = Query(...),
    feature_vars: str = Query(...),
    n_estimators: int = Query(100),
    test_size: float = Query(0.2)
) -> Dict[str, Any]:
    """
    Entraîne un Random Forest Regressor.
    """
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')), delimiter=";")
        
        feat_vars = [v.strip() for v in feature_vars.split(",")]
        result = train_random_forest_regressor(df, feat_vars, target_col,
                                              test_size, n_estimators)
        
        return {
            'metrics': result['metrics'],
            'feature_importance': result['feature_importance'],
            'cross_val_mean': result['cross_val_mean'],
            'cross_val_std': result['cross_val_std'],
            'n_features': result['n_features']
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/feature-selection")
async def select_features(
    file: UploadFile = File(...),
    target_col: str = Query(...),
    feature_vars: str = Query(...)  # CSV séparé par virgule
) -> Dict[str, Any]:
    """
    Sélectionne les features les plus importantes.
    """
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')), delimiter=";")
        
        feat_vars = [v.strip() for v in feature_vars.split(",")]
        result = feature_selection(df, feat_vars, target_col)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/model-comparison")
async def compare_models(
    file: UploadFile = File(...),
    target_col: str = Query(...),
    feature_vars: str = Query(...)  # CSV séparé par virgule
) -> Dict[str, Any]:
    """
    Compare les performances de plusieurs modèles (Random Forest, H2O GLM).
    """
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')), delimiter=";")
        
        feat_vars = [v.strip() for v in feature_vars.split(",")]
        result = model_comparison(df, feat_vars, target_col)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Health Check ====================

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Vérifie la santé du module d'analyse.
    """
    return {
        'status': 'healthy',
        'modules': [
            'data_cleaning',
            'statistical_analysis',
            'dimensionality_reduction',
            'machine_learning'
        ]
    }
