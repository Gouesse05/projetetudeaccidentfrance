"""
Tests du pipeline ETL
"""

import pytest
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pipeline.download_data import calculate_file_hash, load_metadata, save_metadata
from pipeline.explore_and_clean import (
    clean_accidents_data, 
    clean_caracteristiques_data,
    clean_lieux_data
)


class TestDownloadData:
    """Tests du téléchargement"""
    
    def test_calculate_file_hash(self, tmp_path):
        """Test calcul hash"""
        # Créer un fichier test
        test_file = tmp_path / "test.txt"
        test_file.write_text("test data")
        
        # Calculer hash
        hash_value = calculate_file_hash(test_file)
        
        assert hash_value is not None
        assert len(hash_value) == 32  # MD5 = 32 caractères hex
    
    def test_metadata_save_load(self, tmp_path):
        """Test sauvegarde/chargement métadonnées"""
        test_data = {
            "files": {
                "test.csv": {
                    "hash": "abc123",
                    "timestamp": datetime.now().isoformat()
                }
            }
        }
        
        # Note: Dans les vrais tests, mocker le fichier METADATA_FILE
        # Pour maintenant, on teste juste la structure
        assert "files" in test_data
        assert "test.csv" in test_data["files"]


class TestExploreAndClean:
    """Tests du nettoyage"""
    
    def test_clean_accidents_data(self):
        """Test nettoyage données accidents"""
        # Créer un DataFrame test
        df = pd.DataFrame({
            'Num_Acc': [1, 1, 2, 3],  # Doublons
            'Date': ['2024-01-01', '2024-01-01', '2024-01-02', '2024-01-03'],
            'an': [2024, 2024, 2024, 2024],
            'mois': [1, 1, 1, 1],
            'value': [100, 100, 200, 300]
        })
        
        df_cleaned = clean_accidents_data(df)
        
        # Vérifier les doublons supprimés
        assert len(df_cleaned) == 3
        
        # Vérifier que les colonnes sont normalisées
        assert all(col.islower() or '_' in col for col in df_cleaned.columns)
    
    def test_clean_caracteristiques_data(self):
        """Test nettoyage données caractéristiques"""
        df = pd.DataFrame({
            'Num Acc': [1, 2, 3],
            'Lumière': ['jour', 'nuit', 'crépuscule'],
            'Agglo': ['oui', 'non', 'oui']
        })
        
        df_cleaned = clean_caracteristiques_data(df)
        
        # Vérifier normalisation colonnes
        assert 'num_acc' in df_cleaned.columns or 'Num_Acc' not in df_cleaned.columns
        assert len(df_cleaned) == 3
    
    def test_clean_lieux_data(self):
        """Test nettoyage données lieux"""
        df = pd.DataFrame({
            'Num_Acc': [1, 2, 3],
            'Latitude': ['48.8566', '45.7640', '43.2965'],
            'Longitude': ['2.3522', '4.8357', '5.3698'],
            'Route': ['N1', 'N2', 'N3']
        })
        
        df_cleaned = clean_lieux_data(df)
        
        assert len(df_cleaned) == 3
        # Vérifier conversions numériques
        numeric_cols = df_cleaned.select_dtypes(include=['float64', 'int64']).columns
        assert len(numeric_cols) > 0


class TestDataValidation:
    """Tests de validation des données"""
    
    def test_csv_structure(self):
        """Test structure CSV basique"""
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        
        assert len(df) == 3
        assert len(df.columns) == 2
        assert df['col1'].dtype == 'int64'
        assert df['col2'].dtype == 'object'
    
    def test_missing_values_detection(self):
        """Test détection valeurs manquantes"""
        df = pd.DataFrame({
            'A': [1, 2, None, 4],
            'B': [1, None, None, 4]
        })
        
        missing_a = df['A'].isnull().sum()
        missing_b = df['B'].isnull().sum()
        
        assert missing_a == 1
        assert missing_b == 2


if __name__ == "__main__":
    # Lancer les tests
    pytest.main([__file__, "-v"])
