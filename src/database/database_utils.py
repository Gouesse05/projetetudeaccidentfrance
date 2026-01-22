"""
=============================================================================
DATABASE_UTILS.PY
Utilitaires de base de données et requêtes courantes
=============================================================================

Description:
    - Connection pooling PostgreSQL
    - Requêtes d'analyse pré-compilées
    - Validation intégrité données
    - Utility functions pour API/SDK

Usage:
    from src.database.database_utils import DatabaseManager
    
    db = DatabaseManager()
    df_accidents = db.query_accidents(annee=2022, limit=1000)
    db.get_commune_danger_score(code_com='75056')
"""

import os
import logging
import pandas as pd
import psycopg2
from psycopg2 import sql, Error
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from typing import Dict, List, Optional, Tuple, Any
from dotenv import load_dotenv
from datetime import datetime, date
from functools import lru_cache

# Configuration
load_dotenv()

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'accidents_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
}

POOL_SIZE = 5
SCHEMA = 'accidents_schema'

# ============================================================================
# CLASSES
# ============================================================================

class DatabaseManager:
    """Gestionnaire de connexions et requêtes PostgreSQL"""
    
    def __init__(self, config: Dict = DB_CONFIG, pool_size: int = POOL_SIZE):
        """Initialiser pool de connexions"""
        self.config = config
        self.pool_size = pool_size
        self.pool = None
        self.connect_pool()
    
    def connect_pool(self):
        """Créer pool de connexions"""
        try:
            self.pool = SimpleConnectionPool(
                1, self.pool_size,
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )
            logger.info(f"✓ Pool PostgreSQL créé (size={self.pool_size})")
        except Error as e:
            logger.error(f"Erreur création pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager pour connexion du pool"""
        conn = self.pool.getconn()
        try:
            yield conn
        finally:
            self.pool.putconn(conn)
    
    def close_pool(self):
        """Fermer pool"""
        if self.pool:
            self.pool.closeall()
            logger.info("Pool PostgreSQL fermé")
    
    # =========================================================================
    # REQUÊTES SIMPLES
    # =========================================================================
    
    def query_to_dataframe(self, query: str, params: Tuple = None) -> pd.DataFrame:
        """Exécuter requête et retourner DataFrame"""
        try:
            with self.get_connection() as conn:
                return pd.read_sql(query, conn, params=params)
        except Error as e:
            logger.error(f"Erreur requête: {e}")
            return pd.DataFrame()
    
    def execute_query(self, query: str, params: Tuple = None) -> bool:
        """Exécuter requête sans retour"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return True
        except Error as e:
            logger.error(f"Erreur exécution: {e}")
            return False
    
    def fetch_one(self, query: str, params: Tuple = None) -> Dict:
        """Retourner une ligne"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result if result else {}
        except Error as e:
            logger.error(f"Erreur fetch: {e}")
            return {}
    
    # =========================================================================
    # REQUÊTES MÉTIER - ACCIDENTS
    # =========================================================================
    
    def query_accidents(
        self, 
        annee: Optional[int] = None,
        mois: Optional[int] = None,
        dep: Optional[str] = None,
        gravite_min: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """Requête accidents avec filtres"""
        query = f"""
            SELECT * FROM {SCHEMA}.v_accidents_enrichis
            WHERE 1=1
        """
        params = []
        
        if annee:
            query += " AND annee = %s"
            params.append(annee)
        if mois:
            query += " AND mois = %s"
            params.append(mois)
        if dep:
            query += " AND code_dept = %s"
            params.append(dep)
        if gravite_min:
            query += " AND gravite_max >= %s"
            params.append(gravite_min)
        
        query += f" LIMIT {limit}"
        
        return self.query_to_dataframe(query, tuple(params) if params else None)
    
    def get_accidents_by_commune(self, code_com: str, limit: int = 100) -> pd.DataFrame:
        """Accidents par commune"""
        query = f"""
            SELECT * FROM {SCHEMA}.v_accidents_enrichis
            WHERE code_com = %s
            ORDER BY date_accident DESC
            LIMIT %s
        """
        return self.query_to_dataframe(query, (code_com, limit))
    
    def get_accidents_by_region(self, region: str, annee: Optional[int] = None) -> pd.DataFrame:
        """Accidents par région"""
        query = f"""
            SELECT * FROM {SCHEMA}.v_accidents_enrichis
            WHERE region = %s
        """
        params = [region]
        
        if annee:
            query += " AND annee = %s"
            params.append(annee)
        
        query += " ORDER BY date_accident DESC"
        
        return self.query_to_dataframe(query, tuple(params))
    
    # =========================================================================
    # REQUÊTES MÉTIER - ANALYSES
    # =========================================================================
    
    def get_stats_temporelles(self, annee: Optional[int] = None) -> pd.DataFrame:
        """Statistiques par jour/heure"""
        query = f"""
            SELECT 
                annee, mois, jour_semaine, heure,
                COUNT(*) as nombre_accidents,
                SUM(nombre_personnes) as personnes_impliquees,
                AVG(gravite_max) as gravite_moyenne,
                COUNT(CASE WHEN gravite_max = 4 THEN 1 END) as nombre_deces
            FROM {SCHEMA}.accidents
            WHERE 1=1
        """
        params = []
        
        if annee:
            query += " AND annee = %s"
            params.append(annee)
        
        query += """
            GROUP BY annee, mois, jour_semaine, heure
            ORDER BY annee DESC, mois, jour_semaine, heure
        """
        
        return self.query_to_dataframe(query, tuple(params) if params else None)
    
    def get_stats_communes(self, limit: int = 100) -> pd.DataFrame:
        """Communes les plus dangereuses"""
        query = f"""
            SELECT 
                c.nom_com, 
                d.nom_dept,
                COUNT(DISTINCT a.id_accident) as nombre_accidents,
                SUM(a.nombre_personnes) as personnes_impliquees,
                COUNT(CASE WHEN a.gravite_max = 4 THEN 1 END) as nombre_deces,
                AVG(a.gravite_max) as gravite_moyenne,
                c.population,
                ROUND(COUNT(DISTINCT a.id_accident) * 100000.0 / NULLIF(c.population, 0), 2) as accidents_pour_100k_hab
            FROM {SCHEMA}.accidents a
            LEFT JOIN {SCHEMA}.communes c ON a.id_com = c.id_com
            LEFT JOIN {SCHEMA}.departements d ON c.id_dept = d.id_dept
            GROUP BY c.id_com, c.nom_com, d.nom_dept, c.population
            ORDER BY nombre_accidents DESC
            LIMIT %s
        """
        return self.query_to_dataframe(query, (limit,))
    
    def get_stats_departements(self, limit: int = 50) -> pd.DataFrame:
        """Départements les plus impactés"""
        query = f"""
            SELECT 
                d.code_dept,
                d.nom_dept,
                d.region,
                COUNT(DISTINCT a.id_accident) as nombre_accidents,
                SUM(a.nombre_personnes) as personnes_impliquees,
                COUNT(CASE WHEN a.gravite_max = 4 THEN 1 END) as nombre_deces,
                AVG(a.gravite_max) as gravite_moyenne,
                d.population,
                ROUND(COUNT(DISTINCT a.id_accident) * 100000.0 / NULLIF(d.population, 0), 2) as accidents_pour_100k_hab
            FROM {SCHEMA}.accidents a
            LEFT JOIN {SCHEMA}.communes c ON a.id_com = c.id_com
            LEFT JOIN {SCHEMA}.departements d ON c.id_dept = d.id_dept
            GROUP BY d.id_dept, d.code_dept, d.nom_dept, d.region, d.population
            ORDER BY nombre_accidents DESC
            LIMIT %s
        """
        return self.query_to_dataframe(query, (limit,))
    
    def get_danger_scores(self, limit: int = 50) -> pd.DataFrame:
        """Scores de danger par commune"""
        query = f"""
            SELECT 
                c.nom_com,
                d.nom_dept,
                sdc.nombre_accidents,
                sdc.nombre_personnes_impliquees,
                sdc.nombre_personnes_tuees,
                sdc.gravite_moyenne,
                sdc.score_danger,
                sdc.categorie_risque,
                c.densite_hab_km2,
                c.population
            FROM {SCHEMA}.score_danger_commune sdc
            LEFT JOIN {SCHEMA}.communes c ON sdc.id_com = c.id_com
            LEFT JOIN {SCHEMA}.departements d ON c.id_dept = d.id_dept
            ORDER BY sdc.score_danger DESC
            LIMIT %s
        """
        return self.query_to_dataframe(query, (limit,))
    
    def get_commune_danger_score(self, code_com: str) -> Dict:
        """Score danger d'une commune spécifique"""
        query = f"""
            SELECT 
                sdc.*,
                c.nom_com,
                d.nom_dept,
                d.region
            FROM {SCHEMA}.score_danger_commune sdc
            LEFT JOIN {SCHEMA}.communes c ON sdc.id_com = c.id_com
            LEFT JOIN {SCHEMA}.departements d ON c.id_dept = d.id_dept
            WHERE c.code_com = %s
            ORDER BY sdc.date_calcul DESC
            LIMIT 1
        """
        return self.fetch_one(query, (code_com,))
    
    def get_stats_usagers(self, limit: int = 50) -> pd.DataFrame:
        """Statistiques usagers (âge, sexe, etc.)"""
        query = f"""
            SELECT 
                age,
                sexe,
                COUNT(*) as nombre_usagers,
                COUNT(CASE WHEN gravite = 4 THEN 1 END) as nombre_deces,
                AVG(gravite) as gravite_moyenne,
                ROUND(COUNT(CASE WHEN gravite = 4 THEN 1 END) * 100.0 / COUNT(*), 2) as pct_deces
            FROM {SCHEMA}.usagers
            WHERE age > 0
            GROUP BY age, sexe
            ORDER BY nombre_usagers DESC
            LIMIT %s
        """
        return self.query_to_dataframe(query, (limit,))
    
    def get_stats_vehicules(self) -> pd.DataFrame:
        """Statistiques par catégorie véhicule"""
        query = f"""
            SELECT 
                v.categorie_vehicule,
                COUNT(*) as nombre_accidents,
                COUNT(DISTINCT a.id_accident) as nombre_accidents_distincts,
                AVG(a.gravite_max) as gravite_moyenne,
                SUM(a.nombre_personnes) as personnes_impliquees
            FROM {SCHEMA}.vehicules v
            LEFT JOIN {SCHEMA}.accidents a ON v.id_accident = a.id_accident
            WHERE v.categorie_vehicule IS NOT NULL AND v.categorie_vehicule != 'UNKNOWN'
            GROUP BY v.categorie_vehicule
            ORDER BY nombre_accidents DESC
        """
        return self.query_to_dataframe(query)
    
    # =========================================================================
    # REQUÊTES MÉTIER - PATTERNS
    # =========================================================================
    
    def get_heatmap_data(self, annee: Optional[int] = None, limit: int = 10000) -> pd.DataFrame:
        """Données géographiques pour heatmap (lat/lon)"""
        query = f"""
            SELECT 
                l.latitude,
                l.longitude,
                a.annee,
                a.heure,
                a.gravite_max,
                COUNT(*) as weight
            FROM {SCHEMA}.lieux l
            LEFT JOIN {SCHEMA}.accidents a ON l.id_accident = a.id_accident
            WHERE l.latitude IS NOT NULL AND l.longitude IS NOT NULL
        """
        params = []
        
        if annee:
            query += " AND a.annee = %s"
            params.append(annee)
        
        query += """
            GROUP BY l.latitude, l.longitude, a.annee, a.heure, a.gravite_max
            LIMIT %s
        """
        params.append(limit)
        
        return self.query_to_dataframe(query, tuple(params))
    
    def get_accidents_near(self, latitude: float, longitude: float, distance_km: float = 5) -> pd.DataFrame:
        """Accidents proches d'une location (calcul simple distance)"""
        query = f"""
            SELECT 
                a.*,
                l.latitude,
                l.longitude,
                c.nom_com,
                ROUND(
                    SQRT(
                        POW((l.latitude - %s) * 111.32, 2) +
                        POW((l.longitude - %s) * 111.32 * COS(RADIANS(l.latitude)), 2)
                    )::numeric, 2
                ) as distance_km
            FROM {SCHEMA}.accidents a
            LEFT JOIN {SCHEMA}.lieux l ON a.id_accident = l.id_accident
            LEFT JOIN {SCHEMA}.communes c ON a.id_com = c.id_com
            WHERE SQRT(
                POW((l.latitude - %s) * 111.32, 2) +
                POW((l.longitude - %s) * 111.32 * COS(RADIANS(l.latitude)), 2)
            ) <= %s
            ORDER BY distance_km
        """
        return self.query_to_dataframe(
            query, 
            (latitude, longitude, latitude, longitude, distance_km)
        )
    
    # =========================================================================
    # VALIDATION
    # =========================================================================
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """Valider intégrité des données"""
        results = {}
        
        try:
            # Compter enregistrements
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                tables = ['accidents', 'caracteristiques', 'lieux', 'usagers', 'vehicules']
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{table}")
                    count = cursor.fetchone()[0]
                    results[table] = count
                
                # Accidents sans lieux
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.accidents a
                    LEFT JOIN {SCHEMA}.lieux l ON a.id_accident = l.id_accident
                    WHERE l.id_lieu IS NULL
                """)
                results['accidents_sans_lieu'] = cursor.fetchone()[0]
                
                # Doublons détectés
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.accidents
                    WHERE est_doublon = TRUE
                """)
                results['doublons'] = cursor.fetchone()[0]
                
                # Données manquantes critiques
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.accidents
                    WHERE id_com IS NULL
                """)
                results['accidents_sans_commune'] = cursor.fetchone()[0]
                
        except Error as e:
            logger.error(f"Erreur validation: {e}")
            results['erreur'] = str(e)
        
        return results
    
    def generate_data_report(self) -> str:
        """Générer rapport qualité données"""
        stats = self.validate_data_integrity()
        
        report = [
            "\n" + "="*60,
            "RAPPORT QUALITÉ DONNÉES POSTGRESQL",
            "="*60,
            f"Timestamp: {datetime.now().isoformat()}",
            "",
            "COMPTEURS:",
        ]
        
        for key, value in stats.items():
            if key != 'erreur':
                report.append(f"  • {key}: {value}")
        
        report.append("\n" + "="*60)
        
        return "\n".join(report)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_db_manager() -> DatabaseManager:
    """Factory function pour créer DatabaseManager"""
    return DatabaseManager()


def quick_query(sql: str) -> pd.DataFrame:
    """Requête rapide (crée connexion temporaire)"""
    db = DatabaseManager()
    result = db.query_to_dataframe(sql)
    db.close_pool()
    return result


# ============================================================================
# CLI
# ============================================================================

if __name__ == '__main__':
    import sys
    
    # Initialiser manager
    db = DatabaseManager()
    
    # Afficher rapport
    print(db.generate_data_report())
    
    # Afficher communes les plus dangereuses
    print("\n📍 TOP 10 COMMUNES LES PLUS DANGEREUSES:")
    print(db.get_stats_communes(limit=10).to_string())
    
    # Afficher scores danger
    print("\n⚠️ TOP 10 SCORES DE DANGER:")
    print(db.get_danger_scores(limit=10).to_string())
    
    db.close_pool()
