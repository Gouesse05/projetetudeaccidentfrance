"""
=============================================================================
LOAD_POSTGRESQL.PY
Chargement des données nettoyées dans PostgreSQL
=============================================================================

Description:
    Charge les CSV nettoyés dans la base PostgreSQL avec:
    - Transformation des données selon le schéma
    - Validation des contraintes
    - Gestion des doublons
    - Rapports de qualité

Usage:
    python src/database/load_postgresql.py [--force] [--skip-communes]

Options:
    --force: Tronquer les tables avant chargement
    --skip-communes: Ignorer l'import des communes (garder données existantes)
"""

import os
import logging
import pandas as pd
import psycopg2
from psycopg2 import sql, Error, extras
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv
import sys

# ============================================================================
# CONFIGURATION
# ============================================================================

# Charger variables d'environnement
load_dotenv()

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/postgresql_load.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Chemins
PROJECT_ROOT = Path(__file__).parent.parent.parent
CLEAN_DATA_DIR = PROJECT_ROOT / 'data' / 'cleaned'

# Base de données
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'accidents_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
}

BATCH_SIZE = 1000

# =============================================================================
# CLASSES
# =============================================================================

class PostgreSQLLoader:
    """Gestionnaire de chargement PostgreSQL"""
    
    def __init__(self, config: Dict):
        """Initialiser connexion PostgreSQL"""
        self.config = config
        self.conn = None
        self.cursor = None
        self.stats = {
            'departements_inserted': 0,
            'communes_inserted': 0,
            'accidents_inserted': 0,
            'caracteristiques_inserted': 0,
            'lieux_inserted': 0,
            'usagers_inserted': 0,
            'vehicules_inserted': 0,
            'errors': []
        }
    
    def connect(self) -> bool:
        """Établir connexion PostgreSQL"""
        try:
            self.conn = psycopg2.connect(**self.config)
            self.cursor = self.conn.cursor(cursor_factory=extras.RealDictCursor)
            logger.info(f"✓ Connexion PostgreSQL établie ({self.config['host']}:{self.config['port']})")
            return True
        except Error as e:
            logger.error(f"✗ Erreur connexion PostgreSQL: {e}")
            return False
    
    def disconnect(self):
        """Fermer connexion"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Connexion PostgreSQL fermée")
    
    def execute_query(self, query: str, params: Tuple = None) -> bool:
        """Exécuter requête SQL"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return True
        except Error as e:
            logger.error(f"Erreur SQL: {e}")
            self.conn.rollback()
            return False
    
    def truncate_tables(self, force: bool = False):
        """Tronquer tables (si force=True)"""
        if not force:
            return
        
        tables = [
            'score_danger_commune',
            'usagers',
            'vehicules',
            'lieux',
            'caracteristiques',
            'accidents',
            'communes',
            'departements'
        ]
        
        logger.info("Troncature des tables...")
        try:
            for table in tables:
                self.execute_query(
                    f"TRUNCATE TABLE accidents_schema.{table} CASCADE"
                )
            logger.info("✓ Tables tronquées")
        except Exception as e:
            logger.error(f"Erreur troncature: {e}")
    
    def create_schema(self):
        """Créer schéma s'il n'existe pas"""
        schema_file = Path(__file__).parent / 'schema.sql'
        
        if not schema_file.exists():
            logger.error(f"Fichier schéma non trouvé: {schema_file}")
            return False
        
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Exécuter le schéma
            self.cursor.execute(schema_sql)
            self.conn.commit()
            logger.info("✓ Schéma PostgreSQL créé/vérifié")
            return True
        except Error as e:
            logger.error(f"Erreur création schéma: {e}")
            return False
    
    # =========================================================================
    # CHARGEMENT TABLES
    # =========================================================================
    
    def load_communes(self, skip: bool = False):
        """Charger communes depuis CSV"""
        if skip:
            logger.info("⊘ Import communes ignoré (--skip-communes)")
            return
        
        csv_file = CLEAN_DATA_DIR / 'lieux_cleaned.csv'
        if not csv_file.exists():
            logger.warning(f"Fichier communes non trouvé: {csv_file}")
            return
        
        logger.info("Chargement communes...")
        
        try:
            df = pd.read_csv(csv_file, dtype={'dep': str, 'com': str})
            
            # Extraire communes uniques
            communes = df[['dep', 'com']].drop_duplicates().reset_index(drop=True)
            
            for idx, row in communes.iterrows():
                try:
                    self.cursor.execute(
                        sql.SQL(
                            """
                            INSERT INTO accidents_schema.communes 
                            (code_com, nom_com, id_dept, population, zone_urbaine)
                            SELECT %s, CONCAT('COM-', %s), 
                                   (SELECT id_dept FROM accidents_schema.departements 
                                    WHERE code_dept = %s),
                                   0, FALSE
                            WHERE NOT EXISTS (
                                SELECT 1 FROM accidents_schema.communes 
                                WHERE code_com = %s
                            )
                            """
                        ),
                        (f"{row['dep']}{row['com']}", f"{row['com']}", 
                         row['dep'], f"{row['dep']}{row['com']}")
                    )
                    self.stats['communes_inserted'] += 1
                except Error as e:
                    self.stats['errors'].append(f"Commune {row['com']}: {str(e)}")
                    continue
            
            self.conn.commit()
            logger.info(f"✓ {self.stats['communes_inserted']} communes chargées")
        except Exception as e:
            logger.error(f"Erreur chargement communes: {e}")
            self.conn.rollback()
    
    def load_accidents(self):
        """Charger accidents depuis CSV"""
        csv_file = CLEAN_DATA_DIR / 'accidents_cleaned.csv'
        if not csv_file.exists():
            logger.error(f"Fichier accidents non trouvé: {csv_file}")
            return
        
        logger.info("Chargement accidents...")
        
        try:
            df = pd.read_csv(csv_file)
            
            # Transformer colonnes
            df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
            df['annee'] = df['date'].dt.year
            df['mois'] = df['date'].dt.month
            df['jour_mois'] = df['date'].dt.day
            df['jour_semaine'] = df['date'].dt.dayofweek + 1
            
            # Mapper gravité (1=Indemne, 2=Blessé léger, 3=Hospitalisé, 4=Tué)
            gravite_map = {'1': 1, '2': 2, '3': 3, '4': 4}
            df['grav'] = df['grav'].astype(str).map(gravite_map).fillna(1)
            
            records = df.to_dict('records')
            
            for idx, record in enumerate(records):
                try:
                    # Récupérer id_com
                    com_code = f"{record.get('dep', '')}{record.get('com', '')}"
                    self.cursor.execute(
                        "SELECT id_com FROM accidents_schema.communes WHERE code_com = %s",
                        (com_code,)
                    )
                    com_result = self.cursor.fetchone()
                    id_com = com_result['id_com'] if com_result else 1
                    
                    # Insérer accident
                    self.cursor.execute(
                        sql.SQL(
                            """
                            INSERT INTO accidents_schema.accidents 
                            (num_acc, date_accident, annee, mois, jour_mois, jour_semaine, 
                             heure, minute, id_com, nombre_vehicules, nombre_personnes, 
                             gravite_max, hash_md5)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (num_acc) DO NOTHING
                            """
                        ),
                        (
                            str(record.get('Num_Acc', f"ACC_{idx}")),
                            record.get('date'),
                            int(record.get('annee', 0)),
                            int(record.get('mois', 0)),
                            int(record.get('jour_mois', 0)),
                            int(record.get('jour_semaine', 0)),
                            int(record.get('heure', 0)) if pd.notna(record.get('heure')) else 0,
                            int(record.get('minute', 0)) if pd.notna(record.get('minute')) else 0,
                            id_com,
                            int(record.get('nb_vehicules', 0)) if pd.notna(record.get('nb_vehicules')) else 0,
                            int(record.get('nb_usagers', 0)) if pd.notna(record.get('nb_usagers')) else 0,
                            int(record.get('grav', 1)),
                            record.get('hash', None)
                        )
                    )
                    self.stats['accidents_inserted'] += 1
                except Error as e:
                    self.stats['errors'].append(f"Accident {idx}: {str(e)}")
                    continue
                
                # Commit par batch
                if (idx + 1) % BATCH_SIZE == 0:
                    self.conn.commit()
                    logger.info(f"  {idx + 1}/{len(records)} accidents traités")
            
            self.conn.commit()
            logger.info(f"✓ {self.stats['accidents_inserted']} accidents chargés")
        except Exception as e:
            logger.error(f"Erreur chargement accidents: {e}")
            self.conn.rollback()
    
    def load_caracteristiques(self):
        """Charger caractéristiques"""
        csv_file = CLEAN_DATA_DIR / 'caracteristiques_cleaned.csv'
        if not csv_file.exists():
            logger.warning(f"Fichier caractéristiques non trouvé: {csv_file}")
            return
        
        logger.info("Chargement caractéristiques...")
        
        try:
            df = pd.read_csv(csv_file)
            
            for idx, record in df.iterrows():
                try:
                    # Récupérer id_accident
                    self.cursor.execute(
                        "SELECT id_accident FROM accidents_schema.accidents WHERE num_acc = %s",
                        (str(record.get('Num_Acc', '')),)
                    )
                    acc_result = self.cursor.fetchone()
                    if not acc_result:
                        continue
                    
                    id_accident = acc_result['id_accident']
                    
                    # Insérer caractéristiques
                    self.cursor.execute(
                        sql.SQL(
                            """
                            INSERT INTO accidents_schema.caracteristiques 
                            (id_accident, agglomeration)
                            VALUES (%s, %s)
                            """
                        ),
                        (id_accident, record.get('agg', False))
                    )
                    self.stats['caracteristiques_inserted'] += 1
                except Error as e:
                    self.stats['errors'].append(f"Caractéristique {idx}: {str(e)}")
                    continue
                
                if (idx + 1) % BATCH_SIZE == 0:
                    self.conn.commit()
            
            self.conn.commit()
            logger.info(f"✓ {self.stats['caracteristiques_inserted']} caractéristiques chargées")
        except Exception as e:
            logger.error(f"Erreur chargement caractéristiques: {e}")
            self.conn.rollback()
    
    def load_lieux(self):
        """Charger lieux"""
        csv_file = CLEAN_DATA_DIR / 'lieux_cleaned.csv'
        if not csv_file.exists():
            logger.warning(f"Fichier lieux non trouvé: {csv_file}")
            return
        
        logger.info("Chargement lieux...")
        
        try:
            df = pd.read_csv(csv_file)
            
            for idx, record in df.iterrows():
                try:
                    # Récupérer id_accident
                    self.cursor.execute(
                        "SELECT id_accident FROM accidents_schema.accidents WHERE num_acc = %s",
                        (str(record.get('Num_Acc', '')),)
                    )
                    acc_result = self.cursor.fetchone()
                    if not acc_result:
                        continue
                    
                    id_accident = acc_result['id_accident']
                    
                    # Insérer lieu
                    self.cursor.execute(
                        sql.SQL(
                            """
                            INSERT INTO accidents_schema.lieux 
                            (id_accident, latitude, longitude)
                            VALUES (%s, %s, %s)
                            """
                        ),
                        (
                            id_accident,
                            float(record.get('lat', 0)) if pd.notna(record.get('lat')) else 0,
                            float(record.get('long', 0)) if pd.notna(record.get('long')) else 0
                        )
                    )
                    self.stats['lieux_inserted'] += 1
                except Error as e:
                    self.stats['errors'].append(f"Lieu {idx}: {str(e)}")
                    continue
                
                if (idx + 1) % BATCH_SIZE == 0:
                    self.conn.commit()
            
            self.conn.commit()
            logger.info(f"✓ {self.stats['lieux_inserted']} lieux chargés")
        except Exception as e:
            logger.error(f"Erreur chargement lieux: {e}")
            self.conn.rollback()
    
    def load_usagers(self):
        """Charger usagers"""
        csv_file = CLEAN_DATA_DIR / 'usagers_cleaned.csv'
        if not csv_file.exists():
            logger.warning(f"Fichier usagers non trouvé: {csv_file}")
            return
        
        logger.info("Chargement usagers...")
        
        try:
            df = pd.read_csv(csv_file)
            
            for idx, record in df.iterrows():
                try:
                    # Récupérer id_accident
                    self.cursor.execute(
                        "SELECT id_accident FROM accidents_schema.accidents WHERE num_acc = %s",
                        (str(record.get('Num_Acc', '')),)
                    )
                    acc_result = self.cursor.fetchone()
                    if not acc_result:
                        continue
                    
                    id_accident = acc_result['id_accident']
                    
                    # Insérer usager
                    self.cursor.execute(
                        sql.SQL(
                            """
                            INSERT INTO accidents_schema.usagers 
                            (id_accident, num_vehicule, num_occupant, age, sexe, gravite)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """
                        ),
                        (
                            id_accident,
                            int(record.get('Num_Veh', 0)) if pd.notna(record.get('Num_Veh')) else 0,
                            int(record.get('num_occupant', 0)) if pd.notna(record.get('num_occupant')) else 0,
                            int(record.get('an_nais', 0)) if pd.notna(record.get('an_nais')) else 0,
                            str(record.get('sexe', '1'))[:1],
                            int(record.get('grav', 1))
                        )
                    )
                    self.stats['usagers_inserted'] += 1
                except Error as e:
                    self.stats['errors'].append(f"Usager {idx}: {str(e)}")
                    continue
                
                if (idx + 1) % BATCH_SIZE == 0:
                    self.conn.commit()
            
            self.conn.commit()
            logger.info(f"✓ {self.stats['usagers_inserted']} usagers chargés")
        except Exception as e:
            logger.error(f"Erreur chargement usagers: {e}")
            self.conn.rollback()
    
    def load_vehicules(self):
        """Charger véhicules"""
        csv_file = CLEAN_DATA_DIR / 'vehicules_cleaned.csv'
        if not csv_file.exists():
            logger.warning(f"Fichier véhicules non trouvé: {csv_file}")
            return
        
        logger.info("Chargement véhicules...")
        
        try:
            df = pd.read_csv(csv_file)
            
            for idx, record in df.iterrows():
                try:
                    # Récupérer id_accident
                    self.cursor.execute(
                        "SELECT id_accident FROM accidents_schema.accidents WHERE num_acc = %s",
                        (str(record.get('Num_Acc', '')),)
                    )
                    acc_result = self.cursor.fetchone()
                    if not acc_result:
                        continue
                    
                    id_accident = acc_result['id_accident']
                    
                    # Insérer véhicule
                    self.cursor.execute(
                        sql.SQL(
                            """
                            INSERT INTO accidents_schema.vehicules 
                            (id_accident, num_vehicule, categorie_vehicule, nombre_occupants)
                            VALUES (%s, %s, %s, %s)
                            """
                        ),
                        (
                            id_accident,
                            int(record.get('Num_Veh', 0)) if pd.notna(record.get('Num_Veh')) else 0,
                            str(record.get('catv', 'UNKNOWN')),
                            int(record.get('occup', 0)) if pd.notna(record.get('occup')) else 0
                        )
                    )
                    self.stats['vehicules_inserted'] += 1
                except Error as e:
                    self.stats['errors'].append(f"Véhicule {idx}: {str(e)}")
                    continue
                
                if (idx + 1) % BATCH_SIZE == 0:
                    self.conn.commit()
            
            self.conn.commit()
            logger.info(f"✓ {self.stats['vehicules_inserted']} véhicules chargés")
        except Exception as e:
            logger.error(f"Erreur chargement véhicules: {e}")
            self.conn.rollback()
    
    def calculate_danger_scores(self):
        """Calculer scores de danger par commune"""
        logger.info("Calcul scores de danger...")
        
        try:
            # Exécuter fonction stockée
            self.cursor.execute("SELECT * FROM accidents_schema.calculer_scores_danger()")
            result = self.cursor.fetchone()
            count = result[0] if result else 0
            
            logger.info(f"✓ {count} scores de danger calculés")
        except Error as e:
            logger.error(f"Erreur calcul scores: {e}")
    
    def generate_report(self):
        """Générer rapport de chargement"""
        report = [
            "\n" + "="*80,
            "RAPPORT CHARGEMENT POSTGRESQL",
            "="*80,
            f"Timestamp: {datetime.now().isoformat()}",
            "",
            "STATISTIQUES CHARGEMENT:",
            f"  • Départements: {self.stats['departements_inserted']}",
            f"  • Communes: {self.stats['communes_inserted']}",
            f"  • Accidents: {self.stats['accidents_inserted']}",
            f"  • Caractéristiques: {self.stats['caracteristiques_inserted']}",
            f"  • Lieux: {self.stats['lieux_inserted']}",
            f"  • Usagers: {self.stats['usagers_inserted']}",
            f"  • Véhicules: {self.stats['vehicules_inserted']}",
            "",
        ]
        
        if self.stats['errors']:
            report.append(f"ERREURS ({len(self.stats['errors'])}):")
            for error in self.stats['errors'][:10]:  # Afficher max 10
                report.append(f"  • {error}")
            if len(self.stats['errors']) > 10:
                report.append(f"  ... et {len(self.stats['errors']) - 10} autres")
        else:
            report.append("✓ Aucune erreur")
        
        report.append("="*80 + "\n")
        
        return "\n".join(report)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Orchestrer chargement complet"""
    import argparse
    
    # Arguments
    parser = argparse.ArgumentParser(description='Charger données dans PostgreSQL')
    parser.add_argument('--force', action='store_true', help='Tronquer tables avant chargement')
    parser.add_argument('--skip-communes', action='store_true', help='Ignorer import communes')
    args = parser.parse_args()
    
    logger.info("="*80)
    logger.info("DÉMARRAGE CHARGEMENT POSTGRESQL")
    logger.info("="*80)
    
    # Créer loader
    loader = PostgreSQLLoader(DB_CONFIG)
    
    # Connexion
    if not loader.connect():
        logger.error("Connexion échouée")
        sys.exit(1)
    
    try:
        # Créer schéma
        loader.create_schema()
        
        # Tronquer tables si demandé
        loader.truncate_tables(force=args.force)
        
        # Charger données
        loader.load_accidents()
        loader.load_communes(skip=args.skip_communes)
        loader.load_caracteristiques()
        loader.load_lieux()
        loader.load_usagers()
        loader.load_vehicules()
        
        # Calculer scores
        loader.calculate_danger_scores()
        
        # Rapport
        report = loader.generate_report()
        logger.info(report)
        
    finally:
        loader.disconnect()
    
    logger.info("✓ Chargement terminé")


if __name__ == '__main__':
    main()
