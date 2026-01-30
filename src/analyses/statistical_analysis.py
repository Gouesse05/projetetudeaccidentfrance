"""
Module d'analyse statistique et tests statistiques.
Refactorisé à partir du notebook d'analyse.
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import kendalltau, spearmanr, chi2_contingency, ttest_ind, bartlett
import statsmodels.api as sm
from typing import Dict, Tuple, Any


def correlation_analysis(df: pd.DataFrame, numerical_cols: list = None) -> pd.DataFrame:
    """
    Calcule les corrélations entre variables numériques.
    
    Args:
        df: DataFrame d'entrée
        numerical_cols: Liste des colonnes numériques (auto-détecté si None)
        
    Returns:
        Matrice de corrélation
    """
    if numerical_cols is None:
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    return df[numerical_cols].corr()


def spearmans_correlation(df: pd.DataFrame, col1: str, col2: str) -> Tuple[float, float]:
    """
    Calcule la corrélation de Spearman entre deux variables.
    
    Args:
        df: DataFrame d'entrée
        col1: Première colonne
        col2: Deuxième colonne
        
    Returns:
        Tuple (corrélation, p-value)
    """
    return spearmanr(df[col1].dropna(), df[col2].dropna())


def kendalls_correlation(df: pd.DataFrame, col1: str, col2: str) -> Tuple[float, float]:
    """
    Calcule la corrélation de Kendall entre deux variables.
    
    Args:
        df: DataFrame d'entrée
        col1: Première colonne
        col2: Deuxième colonne
        
    Returns:
        Tuple (corrélation, p-value)
    """
    return kendalltau(df[col1].dropna(), df[col2].dropna())


def chi2_test(df: pd.DataFrame, col1: str, col2: str) -> Dict[str, Any]:
    """
    Effectue un test du chi-2 d'indépendance.
    
    Args:
        df: DataFrame d'entrée
        col1: Première colonne (catégorique)
        col2: Deuxième colonne (catégorique)
        
    Returns:
        Dict avec statistiques du test
    """
    contingency_table = pd.crosstab(df[col1], df[col2])
    chi2, pval, dof, expected = chi2_contingency(contingency_table)
    
    return {
        'chi2_statistic': chi2,
        'p_value': pval,
        'degrees_of_freedom': dof,
        'significant': pval < 0.05
    }


def ttest_samples(df: pd.DataFrame, col1: str, col2: str, group_col: str) -> Dict[str, Any]:
    """
    Effectue un test t de comparaison de moyennes entre deux groupes.
    
    Args:
        df: DataFrame d'entrée
        col1: Colonne numérique à comparer
        col2: Valeur de groupe 1
        group_col: Colonne de groupage
        
    Returns:
        Dict avec résultats du test
    """
    group1 = df[df[group_col] == col1][col1].dropna()
    group2 = df[df[group_col] != col1][col1].dropna()
    
    tstat, pval = ttest_ind(group1, group2)
    
    return {
        't_statistic': tstat,
        'p_value': pval,
        'significant': pval < 0.05,
        'mean_group1': group1.mean(),
        'mean_group2': group2.mean()
    }


def bartlett_test(df: pd.DataFrame, col: str, group_col: str) -> Dict[str, Any]:
    """
    Effectue le test de Bartlett pour l'homogénéité des variances.
    
    Args:
        df: DataFrame d'entrée
        col: Colonne numérique
        group_col: Colonne de groupage
        
    Returns:
        Dict avec résultats du test
    """
    groups = [group[col].dropna().values for name, group in df.groupby(group_col)]
    stat, pval = bartlett(*groups)
    
    return {
        'statistic': stat,
        'p_value': pval,
        'homogeneity': pval > 0.05,
        'interpretation': "Variances homogènes" if pval > 0.05 else "Variances hétérogènes"
    }


def linear_regression(df: pd.DataFrame, dependent_var: str, independent_vars: list) -> Dict[str, Any]:
    """
    Effectue une régression linéaire OLS.
    
    Args:
        df: DataFrame d'entrée
        dependent_var: Variable dépendante
        independent_vars: Liste des variables indépendantes
        
    Returns:
        Dict avec résultats du modèle
    """
    # Préparation des données
    X = df[independent_vars].dropna()
    y = df.loc[X.index, dependent_var]
    
    # Ajout de la constante
    X = sm.add_constant(X)
    
    # Ajustement du modèle
    model = sm.OLS(y, X).fit()
    
    return {
        'summary': model.summary().as_text(),
        'r_squared': model.rsquared,
        'adjusted_r_squared': model.rsquared_adj,
        'f_statistic': model.fvalue,
        'f_pvalue': model.f_pvalue,
        'aic': model.aic,
        'bic': model.bic,
        'coefficients': model.params.to_dict(),
        'pvalues': model.pvalues.to_dict()
    }


def logistic_regression(df: pd.DataFrame, dependent_var: str, independent_vars: list) -> Dict[str, Any]:
    """
    Effectue une régression logistique.
    
    Args:
        df: DataFrame d'entrée
        dependent_var: Variable dépendante binaire
        independent_vars: Liste des variables indépendantes
        
    Returns:
        Dict avec résultats du modèle
    """
    # Préparation des données
    X = df[independent_vars].dropna()
    y = df.loc[X.index, dependent_var]
    
    # Ajout de la constante
    X = sm.add_constant(X)
    
    # Ajustement du modèle
    model = sm.Logit(y, X).fit()
    
    return {
        'summary': model.summary().as_text(),
        'log_likelihood': model.llf,
        'aic': model.aic,
        'bic': model.bic,
        'coefficients': model.params.to_dict(),
        'odds_ratios': np.exp(model.params).to_dict(),
        'pvalues': model.pvalues.to_dict()
    }


def descriptive_statistics(df: pd.DataFrame, numerical_cols: list = None) -> Dict[str, Dict]:
    """
    Calcule les statistiques descriptives.
    
    Args:
        df: DataFrame d'entrée
        numerical_cols: Liste des colonnes numériques
        
    Returns:
        Dict avec statistiques par colonne
    """
    if numerical_cols is None:
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    stats_dict = {}
    for col in numerical_cols:
        if col in df.columns:
            stats_dict[col] = {
                'count': int(df[col].count()),
                'mean': float(df[col].mean()),
                'std': float(df[col].std()),
                'min': float(df[col].min()),
                '25%': float(df[col].quantile(0.25)),
                '50%': float(df[col].quantile(0.50)),
                '75%': float(df[col].quantile(0.75)),
                'max': float(df[col].max()),
                'skewness': float(df[col].skew()),
                'kurtosis': float(df[col].kurtosis())
            }
    
    return stats_dict

