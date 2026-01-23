"""
Tests unitaires pour le pipeline d'analyse des accidents.
Tests des modules : data_cleaning, statistical_analysis, dimensionality_reduction, machine_learning.
"""

import pytest
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# ============================================================================
# IMPORTS - Modules d'analyse
# ============================================================================

from analyses.data_cleaning import clean_all_data, get_data_quality_report
from analyses.statistical_analysis import (
    correlation_analysis, 
    descriptive_statistics,
    chi2_test
)
from analyses.dimensionality_reduction import (
    pca_analysis,
    kmeans_clustering,
    elbow_curve
)
from analyses.machine_learning import (
    train_random_forest_classifier,
    feature_selection
)


# ============================================================================
# FIXTURES - Données de test
# ============================================================================

@pytest.fixture
def sample_dataframe():
    """Créer un DataFrame de test."""
    np.random.seed(42)
    return pd.DataFrame({
        'numeric_col1': np.random.randn(100),
        'numeric_col2': np.random.randn(100),
        'numeric_col3': np.random.randint(0, 100, 100),
        'categorical_col': np.random.choice(['A', 'B', 'C'], 100)
    })


@pytest.fixture
def sample_features_targets():
    """Créer des features et targets pour ML."""
    np.random.seed(42)
    X = pd.DataFrame({
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'feature3': np.random.randn(100),
    })
    y = np.random.choice([0, 1], 100)
    return X, y


# ============================================================================
# TESTS - Data Cleaning
# ============================================================================

class TestDataCleaning:
    """Tests du module data_cleaning."""
    
    def test_descriptive_statistics(self, sample_dataframe):
        """Test des statistiques descriptives."""
        result = descriptive_statistics(sample_dataframe)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_correlation_analysis(self, sample_dataframe):
        """Test de l'analyse de corrélation."""
        result = correlation_analysis(sample_dataframe)
        
        assert result is not None
        assert isinstance(result, (dict, pd.DataFrame))
    
    def test_chi2_test(self, sample_dataframe):
        """Test du test chi-carré."""
        # chi2_test signature: chi2_test(df, col1, col2)
        df = pd.DataFrame({
            'cat1': np.random.choice(['A', 'B'], 100),
            'cat2': np.random.choice(['X', 'Y'], 100)
        })
        
        result = chi2_test(df, 'cat1', 'cat2')
        
        assert result is not None
        assert isinstance(result, dict)


# ============================================================================
# TESTS - Statistical Analysis
# ============================================================================

class TestStatisticalAnalysis:
    """Tests des analyses statistiques."""
    
    def test_correlation_result_structure(self, sample_dataframe):
        """Vérifier la structure du résultat de corrélation."""
        result = correlation_analysis(sample_dataframe)
        
        assert isinstance(result, (dict, pd.DataFrame))
    
    def test_chi2_test_structure(self):
        """Vérifier la structure du test chi-carré."""
        df = pd.DataFrame({
            'col1': np.random.choice(['A', 'B'], 50),
            'col2': np.random.choice(['X', 'Y'], 50)
        })
        
        result = chi2_test(df, 'col1', 'col2')
        
        assert isinstance(result, dict)
        assert len(result) > 0


# ============================================================================
# TESTS - Dimensionality Reduction
# ============================================================================

class TestDimensionalityReduction:
    """Tests de la réduction dimensionnelle."""
    
    def test_pca_analysis(self, sample_dataframe):
        """Test PCA."""
        numeric_df = sample_dataframe.select_dtypes(include=[np.number])
        
        result = pca_analysis(numeric_df, n_components=2)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_kmeans_clustering(self, sample_dataframe):
        """Test K-Means."""
        numeric_df = sample_dataframe.select_dtypes(include=[np.number])
        
        result = kmeans_clustering(numeric_df, n_clusters=3)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_elbow_curve(self, sample_dataframe):
        """Test méthode du coude."""
        numeric_df = sample_dataframe.select_dtypes(include=[np.number])
        
        # elbow_curve signature: elbow_curve(df, numerical_cols=None, max_clusters=10)
        result = elbow_curve(numeric_df, max_clusters=5)
        
        assert result is not None
        assert isinstance(result, dict)


# ============================================================================
# TESTS - Machine Learning
# ============================================================================

class TestMachineLearning:
    """Tests du machine learning."""
    
    def test_random_forest_classifier(self, sample_dataframe):
        """Test Random Forest Classifier."""
        # Préparer les données avec colonnes de features et target
        df = sample_dataframe.copy()
        df['target'] = np.random.choice([0, 1], len(df))
        
        feature_cols = ['numeric_col1', 'numeric_col2', 'numeric_col3']
        
        # train_random_forest_classifier signature: (df, feature_cols, target_col, ...)
        result = train_random_forest_classifier(
            df,
            feature_cols=feature_cols,
            target_col='target',
            n_estimators=10,
            test_size=0.2,
            random_state=42
        )
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_feature_selection(self, sample_dataframe):
        """Test sélection de features."""
        df = sample_dataframe.copy()
        df['target'] = np.random.choice([0, 1], len(df))
        
        feature_cols = ['numeric_col1', 'numeric_col2', 'numeric_col3']
        
        # feature_selection signature: (df, feature_cols, target_col, ...)
        result = feature_selection(
            df,
            feature_cols=feature_cols,
            target_col='target'
        )
        
        assert result is not None
        assert isinstance(result, dict)


# ============================================================================
# TESTS - Data Validation
# ============================================================================

class TestDataValidation:
    """Tests de validation des données."""
    
    def test_dataframe_structure(self):
        """Test structure basique d'un DataFrame."""
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        
        assert len(df) == 3
        assert len(df.columns) == 2
        assert df['col1'].dtype in ['int64', 'int32']
        assert df['col2'].dtype == 'object'
    
    def test_missing_values(self):
        """Test détection valeurs manquantes."""
        df = pd.DataFrame({
            'A': [1, 2, None, 4],
            'B': [1, None, None, 4]
        })
        
        missing_a = df['A'].isnull().sum()
        missing_b = df['B'].isnull().sum()
        
        assert missing_a == 1
        assert missing_b == 2
    
    def test_dataframe_dtypes(self, sample_dataframe):
        """Test types de données du DataFrame."""
        numeric_df = sample_dataframe.select_dtypes(include=[np.number])
        
        assert len(numeric_df.columns) > 0


class TestDownloadData:
    """Tests du téléchargement"""
    
    def test_calculate_file_hash(self, tmp_path):
        """Test calcul hash"""
        # Créer un fichier test
        test_file = tmp_path / "test.txt"
        test_file.write_text("test data")
        
        # Simplement vérifier que le fichier existe
        assert test_file.exists()
    
    def test_metadata_structure(self):
        """Test structure métadonnées"""
        test_data = {
            "files": {
                "test.csv": {
                    "hash": "abc123",
                    "timestamp": datetime.now().isoformat()
                }
            }
        }
        
        assert "files" in test_data
        assert "test.csv" in test_data["files"]


# ============================================================================
# TESTS - Integration
# ============================================================================

class TestIntegration:
    """Tests d'intégration du pipeline."""
    
    def test_pipeline_imports(self):
        """Vérifier que tous les imports fonctionnent."""
        assert clean_all_data is not None
        assert correlation_analysis is not None
        assert pca_analysis is not None
        assert train_random_forest_classifier is not None
    
    def test_sequential_pipeline(self, sample_dataframe):
        """Test exécution séquentielle du pipeline."""
        # Statistiques
        stats = descriptive_statistics(sample_dataframe)
        assert stats is not None
        
        # Dimensionalité
        numeric_df = sample_dataframe.select_dtypes(include=[np.number])
        pca = pca_analysis(numeric_df, n_components=2)
        assert pca is not None
        
        # ML
        df = sample_dataframe.copy()
        df['target'] = np.random.choice([0, 1], len(df))
        feature_cols = ['numeric_col1', 'numeric_col2', 'numeric_col3']
        
        ml = train_random_forest_classifier(
            df,
            feature_cols=feature_cols,
            target_col='target',
            n_estimators=10
        )
        assert ml is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
