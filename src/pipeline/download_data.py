"""
Script de téléchargement automatique des données d'accidents
avec vérification de hash et gestion des mises à jour
"""

import os
import hashlib
import requests
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Optional
import logging

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Chemins
BASE_DIR = Path(__file__).parent.parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
METADATA_FILE = RAW_DATA_DIR / ".metadata.json"

# URLs des datasets (à adapter selon les sources réelles)
DATASETS = {
    "accidents": {
        "url": "https://www.data.gouv.fr/api/1/datasets/5f2e7ffa94a0c2558f5c25ea",
        "filename": "accidents.csv"
    },
    "caracteristiques": {
        "url": "https://www.data.gouv.fr/api/1/datasets/5f2e7ffa94a0c2558f5c25ea",
        "filename": "caracteristiques.csv"
    },
    "lieux": {
        "url": "https://www.data.gouv.fr/api/1/datasets/5f2e7ffa94a0c2558f5c25ea",
        "filename": "lieux.csv"
    },
    "usagers": {
        "url": "https://www.data.gouv.fr/api/1/datasets/5f2e7ffa94a0c2558f5c25ea",
        "filename": "usagers.csv"
    },
    "vehicules": {
        "url": "https://www.data.gouv.fr/api/1/datasets/5f2e7ffa94a0c2558f5c25ea",
        "filename": "vehicules.csv"
    }
}


def ensure_raw_data_dir():
    """Crée le répertoire des données brutes s'il n'existe pas"""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"✓ Répertoire données: {RAW_DATA_DIR}")


def calculate_file_hash(file_path: Path, algorithm: str = "md5") -> str:
    """
    Calcule le hash d'un fichier
    
    Args:
        file_path: Chemin du fichier
        algorithm: Algorithme de hash (md5, sha256)
    
    Returns:
        Hash en hexadécimal
    """
    hash_obj = hashlib.new(algorithm)
    
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def calculate_url_hash(url: str) -> str:
    """
    Calcule le hash du contenu d'une URL
    
    Args:
        url: URL du fichier
    
    Returns:
        Hash en hexadécimal
    """
    try:
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
        hash_obj = hashlib.md5()
        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    except Exception as e:
        logger.error(f"✗ Erreur calcul hash pour {url}: {e}")
        return None


def load_metadata() -> Dict:
    """Charge les métadonnées de téléchargement"""
    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"⚠ Erreur lecture metadata: {e}")
    return {}


def save_metadata(metadata: Dict):
    """Sauvegarde les métadonnées de téléchargement"""
    try:
        with open(METADATA_FILE, "w") as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"✓ Métadonnées sauvegardées")
    except Exception as e:
        logger.error(f"✗ Erreur sauvegarde metadata: {e}")


def download_file(url: str, file_path: Path, timeout: int = 30) -> Tuple[bool, str]:
    """
    Télécharge un fichier avec barre de progression
    
    Args:
        url: URL du fichier
        file_path: Chemin de destination
        timeout: Timeout en secondes
    
    Returns:
        Tuple (succès, message)
    """
    try:
        logger.info(f"📥 Téléchargement: {file_path.name}")
        
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\r  Progression: {progress:.1f}%", end="")
        
        print()  # Nouvelle ligne après la barre de progression
        logger.info(f"✓ Téléchargement réussi: {file_path.name}")
        
        return True, "Succès"
        
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ Erreur téléchargement: {e}")
        return False, str(e)
    except Exception as e:
        logger.error(f"✗ Erreur inattendue: {e}")
        return False, str(e)


def should_update(file_path: Path, remote_hash: str, metadata: Dict) -> bool:
    """
    Vérifie si le fichier doit être mis à jour
    
    Args:
        file_path: Chemin du fichier local
        remote_hash: Hash du fichier distant
        metadata: Métadonnées précédentes
    
    Returns:
        True si mise à jour nécessaire
    """
    filename = file_path.name
    
    # Si fichier n'existe pas
    if not file_path.exists():
        logger.info(f"  → Fichier n'existe pas, téléchargement nécessaire")
        return True
    
    # Si hash distant non disponible
    if not remote_hash:
        logger.warning(f"  → Hash distant indisponible, forcer téléchargement")
        return True
    
    # Si hash local existe dans metadata
    local_hash = metadata.get("files", {}).get(filename, {}).get("hash")
    
    if local_hash == remote_hash:
        logger.info(f"  → Hash identique, pas de mise à jour")
        return False
    else:
        logger.info(f"  → Hash différent, mise à jour nécessaire")
        return True


def process_dataset_resources(dataset_name: str, dataset_url: str) -> Dict[str, str]:
    """
    Récupère les ressources (fichiers CSV) d'un dataset
    
    Args:
        dataset_name: Nom du dataset
        dataset_url: URL de l'API dataset
    
    Returns:
        Dict {filename: download_url}
    """
    resources = {}
    
    try:
        response = requests.get(dataset_url, timeout=10)
        response.raise_for_status()
        
        dataset = response.json()
        
        for resource in dataset.get("resources", []):
            # Filtrer les fichiers CSV
            if resource.get("format", "").upper() == "CSV":
                filename = resource.get("title", resource.get("name", "unknown.csv"))
                if not filename.endswith(".csv"):
                    filename += ".csv"
                
                url = resource.get("url")
                if url:
                    resources[filename] = url
                    logger.info(f"  Ressource trouvée: {filename}")
        
        logger.info(f"✓ {len(resources)} ressources trouvées pour {dataset_name}")
        
    except Exception as e:
        logger.error(f"✗ Erreur lors de la récupération des ressources: {e}")
    
    return resources


def download_all_datasets(force: bool = False) -> Dict[str, Dict]:
    """
    Télécharge tous les datasets d'accidents
    
    Args:
        force: Force le téléchargement même si fichier existe
    
    Returns:
        Dict des résultats de téléchargement
    """
    ensure_raw_data_dir()
    
    metadata = load_metadata()
    if "files" not in metadata:
        metadata["files"] = {}
    
    results = {}
    
    logger.info("\n" + "=" * 80)
    logger.info("📥 TÉLÉCHARGEMENT DONNÉES ACCIDENTS ROUTIERS")
    logger.info("=" * 80 + "\n")
    
    # Traiter chaque dataset
    for dataset_name, dataset_config in DATASETS.items():
        logger.info(f"\n🔍 Dataset: {dataset_name}")
        logger.info("-" * 40)
        
        dataset_url = dataset_config["url"]
        filename = dataset_config["filename"]
        file_path = RAW_DATA_DIR / filename
        
        # Récupérer les ressources
        resources = process_dataset_resources(dataset_name, dataset_url)
        
        if not resources:
            logger.warning(f"⚠ Aucune ressource trouvée pour {dataset_name}")
            results[dataset_name] = {
                "success": False,
                "message": "Aucune ressource trouvée"
            }
            continue
        
        # Prendre la première ressource CSV (adapter si besoin)
        download_url = list(resources.values())[0]
        
        # Vérifier hash distant
        logger.info(f"🔐 Calcul du hash distant...")
        remote_hash = calculate_url_hash(download_url)
        
        # Vérifier si mise à jour nécessaire
        if force or should_update(file_path, remote_hash, metadata):
            success, message = download_file(download_url, file_path)
            
            if success:
                # Calculer hash local
                local_hash = calculate_file_hash(file_path)
                
                # Mettre à jour métadonnées
                metadata["files"][filename] = {
                    "hash": local_hash,
                    "remote_hash": remote_hash,
                    "download_url": download_url,
                    "downloaded_at": datetime.now().isoformat(),
                    "size": file_path.stat().st_size
                }
                
                results[dataset_name] = {
                    "success": True,
                    "message": f"Téléchargé avec succès",
                    "size": file_path.stat().st_size,
                    "hash": local_hash
                }
            else:
                results[dataset_name] = {
                    "success": False,
                    "message": message
                }
        else:
            logger.info(f"✓ Fichier à jour, pas de téléchargement")
            results[dataset_name] = {
                "success": True,
                "message": "Fichier déjà à jour"
            }
    
    # Sauvegarder métadonnées
    save_metadata(metadata)
    
    # Afficher résumé
    logger.info("\n" + "=" * 80)
    logger.info("📊 RÉSUMÉ TÉLÉCHARGEMENT")
    logger.info("=" * 80)
    
    for dataset, result in results.items():
        status = "✓" if result.get("success") else "✗"
        logger.info(f"{status} {dataset}: {result.get('message')}")
    
    return results


if __name__ == "__main__":
    import sys
    
    # Permettre le forçage du téléchargement avec --force
    force_download = "--force" in sys.argv
    
    results = download_all_datasets(force=force_download)
    
    # Code de sortie
    all_success = all(r.get("success") for r in results.values())
    exit(0 if all_success else 1)
