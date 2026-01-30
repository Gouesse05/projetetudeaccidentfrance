"""
Exploration des sources de données accidents routiers sur data.gouv.fr
"""

import requests
import json
from typing import List, Dict

def explore_datasets():
    """Explore les datasets accidents routiers sur data.gouv.fr"""
    
    print(" Exploration des datasets accidents routiers...\n")
    
    # API data.gouv.fr
    api_url = "https://www.data.gouv.fr/api/1/datasets"
    
    # Recherche datasets avec "accidents" ou "securite routiere"
    params = {
        "q": "accidents routiers",
        "page_size": 20
    }
    
    try:
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        datasets = data.get("data", [])
        
        print(f" {len(datasets)} datasets trouvés\n")
        print("=" * 80)
        
        for i, dataset in enumerate(datasets, 1):
            print(f"\n{i}. {dataset.get('title', 'N/A')}")
            print(f"   ID: {dataset.get('id')}")
            print(f"   Slug: {dataset.get('slug')}")
            print(f"   Description: {dataset.get('description', 'N/A')[:100]}...")
            print(f"   Ressources: {len(dataset.get('resources', []))}")
            
            # Afficher les ressources (fichiers)
            for res in dataset.get('resources', [])[:3]:
                print(f"     - {res.get('title', 'N/A')} ({res.get('format', 'N/A')})")
                if res.get('last_modified'):
                    print(f"       Dernière mise à jour: {res.get('last_modified')}")
                if res.get('url'):
                    print(f"       URL: {res.get('url')[:80]}...")
            
            print()
        
        return datasets
        
    except Exception as e:
        print(f" Erreur lors de l'exploration: {e}")
        return []


def get_securite_routiere_datasets():
    """Récupère spécifiquement les datasets de la Sécurité Routière"""
    
    print("\n Recherche datasets Sécurité Routière...\n")
    
    # Utiliser l'organisation "Securite-Routiere"
    api_url = "https://www.data.gouv.fr/api/1/organizations/securite-routiere/datasets"
    
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        datasets = data.get("data", [])
        
        print(f" {len(datasets)} datasets trouvés de Sécurité Routière\n")
        
        for dataset in datasets:
            print(f" {dataset.get('title')}")
            print(f"   ID: {dataset.get('id')}")
            print(f"   Slug: {dataset.get('slug')}")
            print(f"   Resources: {len(dataset.get('resources', []))}")
            
            for res in dataset.get('resources', []):
                print(f"     - {res.get('title')} ({res.get('format')})")
                if res.get('url'):
                    print(f"       {res.get('url')}")
            print()
        
        return datasets
        
    except Exception as e:
        print(f" Erreur: {e}")
        return []


def get_accidents_data_urls():
    """Récupère les URLs des données d'accidents"""
    
    print("\n Récupération des URLs de données d'accidents...\n")
    
    # URLs connues des données d'accidents (à mettre à jour)
    urls = {
        "accidents": "https://www.data.gouv.fr/api/1/datasets/5f2e7ffa94a0c2558f5c25ea/resources",
        "caracteristiques": "https://www.data.gouv.fr/api/1/datasets/5f2e7ffa94a0c2558f5c25ea/resources",
    }
    
    try:
        # Essayer de récupérer les ressources du dataset principal
        response = requests.get(urls["accidents"], timeout=10)
        response.raise_for_status()
        
        resources = response.json().get("data", [])
        
        print(f" {len(resources)} ressources trouvées\n")
        
        for res in resources:
            print(f" {res.get('title')}")
            print(f"   Format: {res.get('format')}")
            print(f"   Taille: {res.get('filesize', 'N/A')} bytes")
            print(f"   Mise à jour: {res.get('last_modified')}")
            print(f"   URL: {res.get('url')}\n")
        
        return resources
        
    except Exception as e:
        print(f" Erreur: {e}")
        return []


if __name__ == "__main__":
    print("=" * 80)
    print(" EXPLORATION SOURCES DE DONNÉES - ACCIDENTS ROUTIERS")
    print("=" * 80)
    
    # 1. Exploration générale
    explore_datasets()
    
    # 2. Datasets Sécurité Routière
    get_securite_routiere_datasets()
    
    # 3. URLs spécifiques
    get_accidents_data_urls()
    
    print("\n" + "=" * 80)
    print(" Exploration terminée")
    print("=" * 80)

