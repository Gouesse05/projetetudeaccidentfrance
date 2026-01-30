"""
Module de machine learning avancé.
Modèles H2O, Random Forest, Logistic Regression, etc.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, roc_curve, auc,
    mean_squared_error, r2_score, mean_absolute_error
)
from typing import Dict, Tuple, Any
import warnings

warnings.filterwarnings('ignore')


def train_random_forest_classifier(df: pd.DataFrame, feature_cols: list, target_col: str,
                                  test_size: float = 0.2, n_estimators: int = 100) -> Dict[str, Any]:
    """
    Entraîne un Random Forest Classifier.
    
    Args:
        df: DataFrame d'entrée
        feature_cols: Colonnes de features
        target_col: Colonne cible
        test_size: Proportion de l'ensemble de test
        n_estimators: Nombre d'arbres
        
    Returns:
        Dict avec modèle et métriques
    """
    # Préparation
    X = df[feature_cols].fillna(df[feature_cols].mean())
    y = df[target_col]
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    
    # Entraînement
    model = RandomForestClassifier(n_estimators=n_estimators, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # Prédictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    # Métriques
    metrics = {
        'accuracy': float(accuracy_score(y_test, y_pred)),
        'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
        'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
        'f1': float(f1_score(y_test, y_pred, average='weighted', zero_division=0)),
    }
    
    # ROC-AUC si binaire
    if len(np.unique(y)) == 2:
        metrics['roc_auc'] = float(roc_auc_score(y_test, y_pred_proba[:, 1]))
    
    # Feature importance
    feature_importance = {col: float(imp) for col, imp in 
                         zip(feature_cols, model.feature_importances_)}
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train, y_train, cv=5)
    
    return {
        'model': model,
        'metrics': metrics,
        'feature_importance': feature_importance,
        'cross_val_mean': float(cv_scores.mean()),
        'cross_val_std': float(cv_scores.std()),
        'n_features': len(feature_cols),
        'n_classes': len(np.unique(y)),
        'test_size': test_size
    }


def train_random_forest_regressor(df: pd.DataFrame, feature_cols: list, target_col: str,
                                 test_size: float = 0.2, n_estimators: int = 100) -> Dict[str, Any]:
    """
    Entraîne un Random Forest Regressor.
    
    Args:
        df: DataFrame d'entrée
        feature_cols: Colonnes de features
        target_col: Colonne cible
        test_size: Proportion de l'ensemble de test
        n_estimators: Nombre d'arbres
        
    Returns:
        Dict avec modèle et métriques
    """
    # Préparation
    X = df[feature_cols].fillna(df[feature_cols].mean())
    y = df[target_col].fillna(df[target_col].mean())
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    
    # Entraînement
    model = RandomForestRegressor(n_estimators=n_estimators, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # Prédictions
    y_pred = model.predict(X_test)
    
    # Métriques
    metrics = {
        'mse': float(mean_squared_error(y_test, y_pred)),
        'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
        'mae': float(mean_absolute_error(y_test, y_pred)),
        'r2': float(r2_score(y_test, y_pred))
    }
    
    # Feature importance
    feature_importance = {col: float(imp) for col, imp in 
                         zip(feature_cols, model.feature_importances_)}
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
    
    return {
        'model': model,
        'metrics': metrics,
        'feature_importance': feature_importance,
        'cross_val_mean': float(cv_scores.mean()),
        'cross_val_std': float(cv_scores.std()),
        'n_features': len(feature_cols),
        'test_size': test_size
    }


def h2o_glm_model(df: pd.DataFrame, feature_cols: list, target_col: str, 
                  family: str = "binomial") -> Dict[str, Any]:
    """
    Entraîne un modèle H2O GLM.
    
    Args:
        df: DataFrame d'entrée
        feature_cols: Colonnes de features
        target_col: Colonne cible
        family: Famille de distribution (binomial, gaussian, etc.)
        
    Returns:
        Dict avec résultats du modèle
    """
    try:
        import h2o
        from h2o.estimators.glm import H2OGeneralizedLinearEstimator as GLMH2O
        
        # Initialisation H2O
        if not h2o.cluster():
            h2o.init(strict_version_check=False)
        
        # Conversion en H2OFrame
        h2o_df = h2o.H2OFrame(df[[*feature_cols, target_col]])
        
        # Split
        train, test = h2o_df.split_frame([0.8], seed=42)
        
        # Modèle
        glm = GLMH2O(family=family, alpha=0.5)
        glm.train(feature_cols, target_col, training_frame=train)
        
        # Performance
        perf = glm.model_performance(test)
        
        return {
            'model_id': glm.model_id,
            'auc': float(perf.auc()) if hasattr(perf, 'auc') else None,
            'rmse': float(perf.rmse()) if hasattr(perf, 'rmse') else None,
            'r2': float(perf.r2()) if hasattr(perf, 'r2') else None,
            'family': family,
            'coefficients': glm.coef(),
            'success': True
        }
    except ImportError:
        return {
            'error': 'H2O library not installed',
            'success': False
        }


def model_comparison(df: pd.DataFrame, feature_cols: list, target_col: str) -> Dict[str, Any]:
    """
    Compare plusieurs modèles sur le même dataset.
    
    Args:
        df: DataFrame d'entrée
        feature_cols: Colonnes de features
        target_col: Colonne cible
        
    Returns:
        Dict avec comparaison des performances
    """
    # Préparation
    X = df[feature_cols].fillna(df[feature_cols].mean())
    y = df[target_col]
    
    # Check si binaire ou multiclass
    is_binary = len(np.unique(y)) == 2
    
    results = {}
    
    # Random Forest
    try:
        if is_binary:
            rf_result = train_random_forest_classifier(df, feature_cols, target_col)
            results['Random Forest'] = {
                'accuracy': rf_result['metrics']['accuracy'],
                'f1': rf_result['metrics']['f1'],
                'cross_val_mean': rf_result['cross_val_mean']
            }
        else:
            rf_result = train_random_forest_regressor(df, feature_cols, target_col)
            results['Random Forest'] = {
                'r2': rf_result['metrics']['r2'],
                'rmse': rf_result['metrics']['rmse'],
                'cross_val_mean': rf_result['cross_val_mean']
            }
    except Exception as e:
        results['Random Forest'] = {'error': str(e)}
    
    # H2O GLM
    try:
        glm_result = h2o_glm_model(df, feature_cols, target_col, 
                                   family="binomial" if is_binary else "gaussian")
        if glm_result['success']:
            results['H2O GLM'] = {
                'auc': glm_result.get('auc'),
                'rmse': glm_result.get('rmse'),
                'r2': glm_result.get('r2')
            }
        else:
            results['H2O GLM'] = glm_result
    except Exception as e:
        results['H2O GLM'] = {'error': str(e)}
    
    return results


def feature_selection(df: pd.DataFrame, feature_cols: list, target_col: str) -> Dict[str, Any]:
    """
    Sélectionne les features les plus importantes.
    
    Args:
        df: DataFrame d'entrée
        feature_cols: Colonnes de features
        target_col: Colonne cible
        
    Returns:
        Dict avec features importances triées
    """
    X = df[feature_cols].fillna(df[feature_cols].mean())
    y = df[target_col]
    
    # Déterminer le type de target
    is_classification = y.dtype == 'object' or len(np.unique(y)) < 20
    
    if is_classification:
        model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    else:
        model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    
    model.fit(X, y)
    
    # Trier par importance
    importances = sorted(
        zip(feature_cols, model.feature_importances_),
        key=lambda x: x[1],
        reverse=True
    )
    
    return {
        'feature_importance': {col: float(imp) for col, imp in importances},
        'top_features': [col for col, _ in importances[:10]],
        'feature_count': len(feature_cols)
    }

