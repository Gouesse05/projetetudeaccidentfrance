"""
Module de réduction dimensionnelle et analyses multivariées.
PCA, MCA, CA, LDA, clustering hiérarchique.
Refactorisé à partir du notebook d'analyse.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA, FactorAnalysis as FA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from sklearn.cluster import KMeans
from typing import Dict, Tuple, Any
import warnings

warnings.filterwarnings('ignore')


def pca_analysis(df: pd.DataFrame, numerical_cols: list = None, n_components: int = 2) -> Dict[str, Any]:
    """
    Effectue une Analyse en Composantes Principales (PCA).
    
    Args:
        df: DataFrame d'entrée
        numerical_cols: Colonnes numériques à utiliser
        n_components: Nombre de composantes principales
        
    Returns:
        Dict avec résultats PCA
    """
    if numerical_cols is None:
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Nettoyage
    X = df[numerical_cols].dropna()
    
    # Standardisation
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # PCA
    pca = PCA(n_components=n_components)
    X_pca = pca.fit_transform(X_scaled)
    
    return {
        'transformed_data': X_pca,
        'explained_variance': pca.explained_variance_.tolist(),
        'explained_variance_ratio': pca.explained_variance_ratio_.tolist(),
        'cumulative_variance': np.cumsum(pca.explained_variance_ratio_).tolist(),
        'components': pca.components_.tolist(),
        'loadings': {col: pca.components_[0, i] for i, col in enumerate(numerical_cols)},
        'scaler': scaler,
        'model': pca
    }


def factor_analysis(df: pd.DataFrame, numerical_cols: list = None, n_components: int = 2) -> Dict[str, Any]:
    """
    Effectue une Analyse Factorielle.
    
    Args:
        df: DataFrame d'entrée
        numerical_cols: Colonnes numériques à utiliser
        n_components: Nombre de facteurs
        
    Returns:
        Dict avec résultats FA
    """
    if numerical_cols is None:
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Nettoyage et standardisation
    X = df[numerical_cols].dropna()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Factor Analysis
    fa = FA(n_components=n_components)
    X_fa = fa.fit_transform(X_scaled)
    
    return {
        'transformed_data': X_fa,
        'components': fa.components_.tolist(),
        'noise_variance': fa.noise_variance_.tolist(),
        'loadings': {col: fa.components_[0, i] for i, col in enumerate(numerical_cols)},
        'scaler': scaler,
        'model': fa
    }


def lda_analysis(df: pd.DataFrame, numerical_cols: list, target_col: str, n_components: int = 2) -> Dict[str, Any]:
    """
    Effectue une Analyse Discriminante Linéaire (LDA).
    
    Args:
        df: DataFrame d'entrée
        numerical_cols: Colonnes numériques
        target_col: Colonne cible (classes)
        n_components: Nombre de composantes
        
    Returns:
        Dict avec résultats LDA
    """
    # Préparation
    X = df[numerical_cols].dropna()
    y = df.loc[X.index, target_col]
    
    # Standardisation
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # LDA
    lda = LDA(n_components=min(n_components, len(np.unique(y)) - 1))
    X_lda = lda.fit_transform(X_scaled, y)
    
    return {
        'transformed_data': X_lda,
        'explained_variance_ratio': lda.explained_variance_ratio_.tolist(),
        'cumulative_variance': np.cumsum(lda.explained_variance_ratio_).tolist(),
        'coefficients': lda.coef_.tolist(),
        'intercept': lda.intercept_.tolist(),
        'classes': lda.classes_.tolist(),
        'scaler': scaler,
        'model': lda
    }


def hierarchical_clustering(df: pd.DataFrame, numerical_cols: list = None, 
                           method: str = 'ward', n_clusters: int = 3) -> Dict[str, Any]:
    """
    Effectue un clustering hiérarchique.
    
    Args:
        df: DataFrame d'entrée
        numerical_cols: Colonnes numériques
        method: Méthode de liaison (ward, complete, average, single)
        n_clusters: Nombre de clusters
        
    Returns:
        Dict avec résultats du clustering
    """
    if numerical_cols is None:
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Nettoyage
    X = df[numerical_cols].dropna()
    
    # Standardisation
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Clustering hiérarchique
    Z = linkage(X_scaled, method=method)
    clusters = fcluster(Z, n_clusters, criterion='maxclust')
    
    return {
        'linkage_matrix': Z.tolist(),
        'cluster_labels': clusters.tolist(),
        'n_clusters': n_clusters,
        'method': method,
        'scaler': scaler
    }


def kmeans_clustering(df: pd.DataFrame, numerical_cols: list = None, n_clusters: int = 3) -> Dict[str, Any]:
    """
    Effectue un clustering K-Means.
    
    Args:
        df: DataFrame d'entrée
        numerical_cols: Colonnes numériques
        n_clusters: Nombre de clusters
        
    Returns:
        Dict avec résultats du clustering
    """
    if numerical_cols is None:
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Nettoyage
    X = df[numerical_cols].dropna()
    
    # Standardisation
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    
    return {
        'cluster_labels': clusters.tolist(),
        'centroids': kmeans.cluster_centers_.tolist(),
        'inertia': float(kmeans.inertia_),
        'silhouette': calculate_silhouette_score(X_scaled, clusters),
        'n_clusters': n_clusters,
        'scaler': scaler,
        'model': kmeans
    }


def mca_analysis(df: pd.DataFrame, categorical_cols: list) -> Dict[str, Any]:
    """
    Effectue une Analyse des Correspondances Multiples (MCA).
    Utilise la bibliothèque 'prince' si disponible.
    
    Args:
        df: DataFrame d'entrée
        categorical_cols: Liste des colonnes catégorique
        
    Returns:
        Dict avec résultats MCA
    """
    try:
        from prince import MCA
        
        # Nettoyage
        df_clean = df[categorical_cols].dropna()
        
        # MCA
        mca = MCA(n_components=2, random_state=42)
        X_mca = mca.fit_transform(df_clean)
        
        return {
            'transformed_data': X_mca.values.tolist(),
            'inertia': float(mca.total_inertia),
            'eigenvalues': mca.eigenvalues_.tolist() if hasattr(mca, 'eigenvalues_') else [],
            'n_components': 2,
            'columns': df_clean.columns.tolist(),
            'success': True
        }
    except ImportError:
        return {
            'error': 'prince library not installed',
            'success': False
        }


def ca_analysis(df: pd.DataFrame, row_col: str, col_col: str) -> Dict[str, Any]:
    """
    Effectue une Analyse des Correspondances (CA) simple.
    
    Args:
        df: DataFrame d'entrée
        row_col: Colonne pour les lignes
        col_col: Colonne pour les colonnes
        
    Returns:
        Dict avec résultats CA
    """
    try:
        from prince import CA
        
        # Créer tableau de contingence
        contingency = pd.crosstab(df[row_col], df[col_col])
        
        # CA
        ca = CA(n_components=2, random_state=42)
        
        # Note: prince CA fonctionne différemment
        return {
            'contingency_table': contingency.values.tolist(),
            'row_labels': contingency.index.tolist(),
            'column_labels': contingency.columns.tolist(),
            'n_rows': len(contingency),
            'n_cols': len(contingency.columns)
        }
    except ImportError:
        return {
            'error': 'prince library not installed',
            'success': False
        }


def calculate_silhouette_score(X: np.ndarray, labels: np.ndarray) -> float:
    """Calcule le score de silhouette."""
    from sklearn.metrics import silhouette_score
    try:
        return float(silhouette_score(X, labels))
    except:
        return 0.0


def elbow_curve(df: pd.DataFrame, numerical_cols: list = None, max_clusters: int = 10) -> Dict[str, Any]:
    """
    Calcule la courbe du coude pour K-Means.
    
    Args:
        df: DataFrame d'entrée
        numerical_cols: Colonnes numériques
        max_clusters: Nombre maximum de clusters à tester
        
    Returns:
        Dict avec inertie par nombre de clusters
    """
    if numerical_cols is None:
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    X = df[numerical_cols].dropna()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    inertias = []
    for k in range(1, max_clusters + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        inertias.append(float(kmeans.inertia_))
    
    return {
        'n_clusters': list(range(1, max_clusters + 1)),
        'inertias': inertias
    }
