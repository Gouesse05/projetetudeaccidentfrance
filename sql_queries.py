"""
Raw SQL Queries for Direct PostgreSQL Access
This module provides functions for executing raw SQL queries directly on the accidents database.
"""

import psycopg2
import pandas as pd
from typing import Dict, List, Optional
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


class DatabaseConnection:
    """Handle PostgreSQL database connections and queries"""
    
    def __init__(self):
        """Initialize database connection from environment variables"""
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.database = os.getenv('DB_NAME', 'accidents_db')
        self.user = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD')
        self.conn = None
        self.cursor = None
    
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.conn.cursor()
            print(f"Connected to {self.user}@{self.host}:{self.port}/{self.database}")
            return True
        except psycopg2.Error as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Database connection closed")
    
    def execute_query(self, query: str, params: tuple = None) -> pd.DataFrame:
        """Execute SELECT query and return results as DataFrame"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            columns = [desc[0] for desc in self.cursor.description]
            data = self.cursor.fetchall()
            
            return pd.DataFrame(data, columns=columns)
        except psycopg2.Error as e:
            print(f"Query error: {e}")
            return pd.DataFrame()
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute INSERT/UPDATE/DELETE query"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            self.conn.commit()
            return self.cursor.rowcount
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Update error: {e}")
            return 0


# Initialize global connection
db = DatabaseConnection()


# ============================================================================
# SCHEMA QUERIES
# ============================================================================

def get_tables() -> pd.DataFrame:
    """List all tables in the database"""
    query = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name;
    """
    return db.execute_query(query)


def get_table_schema(table_name: str) -> pd.DataFrame:
    """Get schema/columns for a specific table"""
    query = """
    SELECT 
        column_name,
        data_type,
        is_nullable,
        column_default
    FROM information_schema.columns
    WHERE table_name = %s
    ORDER BY ordinal_position;
    """
    return db.execute_query(query, (table_name,))


def get_table_info(table_name: str) -> Dict:
    """Get detailed information about a table"""
    query = f"""
    SELECT COUNT(*) as row_count,
           pg_size_pretty(pg_total_relation_size('{table_name}')) as size
    FROM {table_name};
    """
    df = db.execute_query(query)
    if not df.empty:
        return df.iloc[0].to_dict()
    return {}


# ============================================================================
# BASIC QUERIES
# ============================================================================

def count_accidents() -> int:
    """Get total number of accidents"""
    query = "SELECT COUNT(*) as total FROM accidents;"
    df = db.execute_query(query)
    if not df.empty:
        return df.iloc[0]['total']
    return 0


def get_sample_data(table: str = 'accidents', limit: int = 10) -> pd.DataFrame:
    """Get sample data from a table"""
    query = f"SELECT * FROM {table} LIMIT %s;"
    return db.execute_query(query, (limit,))


def get_years() -> pd.DataFrame:
    """Get distinct years in database"""
    query = """
    SELECT DISTINCT EXTRACT(YEAR FROM date_accident) as annee
    FROM accidents
    ORDER BY annee DESC;
    """
    return db.execute_query(query)


# ============================================================================
# AGGREGATION QUERIES
# ============================================================================

def accidents_by_year() -> pd.DataFrame:
    """Get accident count by year"""
    query = """
    SELECT 
        EXTRACT(YEAR FROM date_accident)::int as annee,
        COUNT(*) as nombre_accidents,
        SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) as nombre_deces,
        ROUND(AVG(gravite_max)::numeric, 2) as gravite_moyenne
    FROM accidents
    GROUP BY EXTRACT(YEAR FROM date_accident)
    ORDER BY annee DESC;
    """
    return db.execute_query(query)


def accidents_by_month(year: int = None) -> pd.DataFrame:
    """Get accident count by month"""
    if year:
        query = """
        SELECT 
            EXTRACT(MONTH FROM date_accident)::int as mois,
            COUNT(*) as nombre,
            SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) as deces
        FROM accidents
        WHERE EXTRACT(YEAR FROM date_accident) = %s
        GROUP BY EXTRACT(MONTH FROM date_accident)
        ORDER BY mois;
        """
        return db.execute_query(query, (year,))
    else:
        query = """
        SELECT 
            EXTRACT(MONTH FROM date_accident)::int as mois,
            COUNT(*) as nombre,
            SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) as deces
        FROM accidents
        GROUP BY EXTRACT(MONTH FROM date_accident)
        ORDER BY mois;
        """
        return db.execute_query(query)


def accidents_by_day_of_week() -> pd.DataFrame:
    """Get accident count by day of week"""
    query = """
    SELECT 
        jour_semaine,
        COUNT(*) as nombre,
        ROUND(AVG(gravite_max)::numeric, 2) as gravite_moyenne,
        SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) as deces
    FROM accidents
    GROUP BY jour_semaine
    ORDER BY jour_semaine;
    """
    return db.execute_query(query)


def accidents_by_hour() -> pd.DataFrame:
    """Get accident count by hour of day"""
    query = """
    SELECT 
        EXTRACT(HOUR FROM heure)::int as heure,
        COUNT(*) as nombre,
        ROUND(AVG(gravite_max)::numeric, 2) as gravite_moyenne,
        ROUND(100.0 * SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) / COUNT(*)::numeric, 2) as taux_fatal_percent
    FROM accidents
    WHERE heure IS NOT NULL
    GROUP BY EXTRACT(HOUR FROM heure)
    ORDER BY heure;
    """
    return db.execute_query(query)


# ============================================================================
# GEOGRAPHICAL QUERIES
# ============================================================================

def top_communes(limit: int = 10) -> pd.DataFrame:
    """Get top most dangerous communes"""
    query = """
    SELECT 
        a.code_com,
        com.nom,
        COUNT(*) as nombre_accidents,
        SUM(CASE WHEN a.gravite_max = 4 THEN 1 ELSE 0 END) as nombres_deces,
        ROUND(AVG(a.gravite_max)::numeric, 2) as gravite_moyenne,
        com.population,
        ROUND(com.densite_hab_km2::numeric, 1) as densite
    FROM accidents a
    JOIN communes com ON a.code_com = com.code_com
    GROUP BY a.code_com, com.nom, com.population, com.densite_hab_km2
    ORDER BY nombre_accidents DESC
    LIMIT %s;
    """
    return db.execute_query(query, (limit,))


def top_departments(limit: int = 10) -> pd.DataFrame:
    """Get top most dangerous departments"""
    query = """
    SELECT 
        code_dept,
        COUNT(*) as nombre_accidents,
        SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) as nombres_deces,
        ROUND(AVG(gravite_max)::numeric, 2) as gravite_moyenne
    FROM accidents
    GROUP BY code_dept
    ORDER BY nombre_accidents DESC
    LIMIT %s;
    """
    return db.execute_query(query, (limit,))


def accidents_by_commune(code_com: str, year: int = None) -> pd.DataFrame:
    """Get accidents for a specific commune"""
    if year:
        query = """
        SELECT 
            date_accident,
            heure,
            gravite_max,
            nombre_personnes,
            nombre_deces,
            conditions_meteo,
            type_route
        FROM accidents
        WHERE code_com = %s AND EXTRACT(YEAR FROM date_accident) = %s
        ORDER BY date_accident DESC;
        """
        return db.execute_query(query, (code_com, year))
    else:
        query = """
        SELECT 
            date_accident,
            heure,
            gravite_max,
            nombre_personnes,
            nombre_deces,
            conditions_meteo,
            type_route
        FROM accidents
        WHERE code_com = %s
        ORDER BY date_accident DESC;
        """
        return db.execute_query(query, (code_com,))


# ============================================================================
# SEVERITY ANALYSIS
# ============================================================================

def severity_by_conditions() -> pd.DataFrame:
    """Analyze severity by weather and light conditions"""
    query = """
    SELECT 
        conditions_meteo,
        luminosite,
        COUNT(*) as nombre,
        ROUND(AVG(gravite_max)::numeric, 2) as gravite_moyenne,
        ROUND(100.0 * SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) / COUNT(*)::numeric, 2) as taux_fatal_percent
    FROM accidents
    WHERE conditions_meteo IS NOT NULL AND luminosite IS NOT NULL
    GROUP BY conditions_meteo, luminosite
    ORDER BY nombre DESC;
    """
    return db.execute_query(query)


def severity_by_road_type() -> pd.DataFrame:
    """Analyze severity by road type"""
    query = """
    SELECT 
        type_route,
        COUNT(*) as nombre_accidents,
        ROUND(AVG(gravite_max)::numeric, 2) as gravite_moyenne,
        SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) as nombres_deces,
        ROUND(100.0 * SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) / COUNT(*)::numeric, 2) as taux_fatal_percent
    FROM accidents
    WHERE type_route IS NOT NULL
    GROUP BY type_route
    ORDER BY nombre_accidents DESC;
    """
    return db.execute_query(query)


def severity_by_weather() -> pd.DataFrame:
    """Analyze severity by weather conditions"""
    query = """
    SELECT 
        conditions_meteo,
        COUNT(*) as nombre,
        ROUND(AVG(gravite_max)::numeric, 2) as gravite_moyenne,
        SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) as deces,
        ROUND(100.0 * SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) / COUNT(*)::numeric, 2) as taux_fatal_percent
    FROM accidents
    WHERE conditions_meteo IS NOT NULL
    GROUP BY conditions_meteo
    ORDER BY nombre DESC;
    """
    return db.execute_query(query)


# ============================================================================
# CUSTOM QUERIES
# ============================================================================

def custom_query(query: str, params: tuple = None) -> pd.DataFrame:
    """Execute a custom SQL query"""
    return db.execute_query(query, params)


def custom_update(query: str, params: tuple = None) -> int:
    """Execute a custom UPDATE/INSERT/DELETE query"""
    return db.execute_update(query, params)


# ============================================================================
# DATA EXPORT
# ============================================================================

def export_query_to_csv(query: str, filename: str, params: tuple = None):
    """Export query results to CSV"""
    df = db.execute_query(query, params)
    df.to_csv(filename, index=False)
    print(f"Exported {len(df)} rows to {filename}")
    return df


def export_query_to_json(query: str, filename: str, params: tuple = None):
    """Export query results to JSON"""
    df = db.execute_query(query, params)
    df.to_json(filename, orient='records', indent=2)
    print(f"Exported {len(df)} rows to {filename}")
    return df


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Connect to database
    if db.connect():
        
        # Example 1: Get tables
        print("\n=== Database Tables ===")
        tables = get_tables()
        print(tables)
        
        # Example 2: Get sample data
        print("\n=== Sample Data (5 rows) ===")
        sample = get_sample_data(limit=5)
        print(sample)
        
        # Example 3: Accidents by year
        print("\n=== Accidents by Year ===")
        yearly = accidents_by_year()
        print(yearly)
        
        # Example 4: Top communes
        print("\n=== Top 10 Dangerous Communes ===")
        top_com = top_communes(limit=10)
        print(top_com)
        
        # Example 5: Severity by conditions
        print("\n=== Severity by Conditions ===")
        severity = severity_by_conditions()
        print(severity.head(10))
        
        # Example 6: Export to CSV
        query = "SELECT * FROM accidents LIMIT 100;"
        export_query_to_csv(query, 'sample_export.csv')
        
        # Disconnect
        db.disconnect()
