#!/usr/bin/env python
"""
Script de Migration PostgreSQL vers Render

Usage:
    # Migrate data from local to Render
    python scripts/migrate_to_render.py --action backup --local-db /path/to/dump.sql
    python scripts/migrate_to_render.py --action restore --render-db postgres://user:pass@host/db
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

def backup_local_db(db_host: str, db_user: str, db_name: str, output_file: str = None):
    """Backup PostgreSQL local vers fichier"""
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"backups/accidents_db_backup_{timestamp}.sql"
    
    Path(output_file).parent.mkdir(exist_ok=True)
    
    print(f"📦 Backing up local database to {output_file}...")
    
    try:
        result = subprocess.run([
            'pg_dump',
            '-h', db_host,
            '-U', db_user,
            '-d', db_name,
            '-v',  # Verbose
            '-F', 'p',  # Plain text format
            '-f', output_file
        ], check=True, capture_output=True, text=True)
        
        print(f"✅ Backup completed: {output_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"❌ Backup failed: {e.stderr}")
        return None

def restore_render_db(db_url: str, dump_file: str):
    """Restore PostgreSQL dump vers Render"""
    print(f"📥 Restoring backup to Render ({dump_file})...")
    
    try:
        result = subprocess.run([
            'psql',
            db_url,
            '-f', dump_file,
            '-v', 'ON_ERROR_STOP=1'
        ], check=True, capture_output=True, text=True)
        
        print(f"✅ Restore completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Restore failed: {e.stderr}")
        return False

def load_data_from_csvs(db_host: str, db_user: str, db_name: str, db_password: str):
    """Load data from Phase 1 CSVs usando PostgreSQLLoader"""
    print(f"📊 Loading data from CSVs to {db_host}...")
    
    try:
        from src.database.load_postgresql import PostgreSQLLoader
        from src.config import DATA_DIR
        
        loader = PostgreSQLLoader(
            host=db_host,
            port=5432,
            user=db_user,
            password=db_password,
            dbname=db_name
        )
        
        print("Loading accidents...")
        loader.load_accidents(f"{DATA_DIR}/accidents.csv")
        
        print("Loading accident locations...")
        loader.load_accident_locations(f"{DATA_DIR}/accident_locations.csv")
        
        print("Loading communes...")
        loader.load_communes(f"{DATA_DIR}/communes.csv")
        
        print("Loading usagers...")
        loader.load_usagers(f"{DATA_DIR}/usagers.csv")
        
        print("Loading vehicles...")
        loader.load_vehicles(f"{DATA_DIR}/vehicules.csv")
        
        print("✅ Data loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return False

def verify_migration(db_host: str, db_user: str, db_name: str, db_password: str):
    """Verify data migration"""
    print(f"🔍 Verifying migration to {db_host}...")
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("""
            SELECT COUNT(*)::int as table_count
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchone()[0]
        print(f"  📋 Tables: {tables}")
        
        # Check data
        cursor.execute("SELECT COUNT(*)::int FROM accidents")
        accidents = cursor.fetchone()[0]
        print(f"  🚗 Accidents: {accidents:,}")
        
        cursor.execute("SELECT COUNT(*)::int FROM usagers")
        usagers = cursor.fetchone()[0]
        print(f"  👤 Usagers: {usagers:,}")
        
        cursor.execute("SELECT COUNT(*)::int FROM vehicules")
        vehicles = cursor.fetchone()[0]
        print(f"  🚕 Vehicles: {vehicles:,}")
        
        cursor.close()
        conn.close()
        
        if accidents > 0 and usagers > 0 and vehicles > 0:
            print(f"✅ Migration verified successfully")
            return True
        else:
            print(f"⚠️  Some tables are empty")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Migrate PostgreSQL database to Render"
    )
    
    parser.add_argument(
        '--action',
        choices=['backup', 'restore', 'load', 'verify'],
        required=True,
        help='Action to perform'
    )
    
    parser.add_argument(
        '--local-db',
        default='localhost',
        help='Local database host or dump file'
    )
    
    parser.add_argument(
        '--render-db',
        help='Render database URL (postgres://user:pass@host/db)'
    )
    
    parser.add_argument(
        '--db-user',
        default=os.getenv('DB_USER', 'postgres'),
        help='Database user'
    )
    
    parser.add_argument(
        '--db-password',
        default=os.getenv('DB_PASSWORD'),
        help='Database password'
    )
    
    parser.add_argument(
        '--db-name',
        default='accidents_db',
        help='Database name'
    )
    
    args = parser.parse_args()
    
    print("🚀 PostgreSQL Migration Tool")
    print("=" * 50)
    
    if args.action == 'backup':
        backup_local_db(args.local_db, args.db_user, args.db_name)
    
    elif args.action == 'restore':
        if not args.render_db:
            print("❌ --render-db required for restore action")
            sys.exit(1)
        restore_render_db(args.render_db, args.local_db)
    
    elif args.action == 'load':
        if not args.db_password:
            print("❌ --db-password required for load action")
            sys.exit(1)
        load_data_from_csvs(
            args.render_db or args.local_db,
            args.db_user,
            args.db_name,
            args.db_password
        )
    
    elif args.action == 'verify':
        if not args.db_password:
            print("❌ --db-password required for verify action")
            sys.exit(1)
        verify_migration(
            args.render_db or args.local_db,
            args.db_user,
            args.db_name,
            args.db_password
        )

if __name__ == '__main__':
    main()
