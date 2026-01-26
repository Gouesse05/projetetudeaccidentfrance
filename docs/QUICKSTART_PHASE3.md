#  Guide de Démarrage Rapide - Phase 3 (PostgreSQL)

## 1⃣ Prérequis

```bash
# PostgreSQL doit être installé et lancé
psql --version
psql -U postgres -c "SELECT version();"

# Python packages (dans requirements.txt)
pip install psycopg2-binary sqlalchemy pandas
```

## 2⃣ Configuration Environnement

Créer `.env` depuis `.env.example`:

```bash
cp .env.example .env
```

Éditer `.env`:
```ini
# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=accidents_db
DB_USER=postgres
DB_PASSWORD=postgres

# API (Phase 4)
API_HOST=localhost
API_PORT=8000

# Data
DATA_SOURCE=data.gouv.fr
```

## 3⃣ Créer la Base de Données PostgreSQL

```bash
# Option 1: Via SQL
psql -U postgres
CREATE DATABASE accidents_db ENCODING 'UTF8';
\c accidents_db
\i src/database/schema.sql

# Option 2: Via Python
python -c "
import psycopg2
conn = psycopg2.connect(host='localhost', user='postgres', password='postgres')
conn.autocommit = True
cursor = conn.cursor()
cursor.execute('CREATE DATABASE accidents_db ENCODING \"UTF8\";')
cursor.close()
conn.close()
"
```

## 4⃣ Charger les Données Nettoyées

**Prérequis:** Avoir exécuté Phase 1 & 2 (CSV nettoyés dans `data/cleaned/`)

```bash
# Charger données depuis CSV
python src/database/load_postgresql.py

# Résultat attendu:
#  Schéma PostgreSQL créé
#  68,432 accidents chargés
#  12,234 communes chargées
#  Scores de danger calculés
```

**Options:**
```bash
# Avec reset complet (tronquer avant chargement)
python src/database/load_postgresql.py --force

# Sans recharger communes (garder données existantes)
python src/database/load_postgresql.py --skip-communes
```

## 5⃣ Vérifier les Données

```bash
# Via psql
psql -U postgres -d accidents_db -c "
SELECT COUNT(*) as total_accidents FROM accidents_schema.accidents;
SELECT COUNT(*) as total_communes FROM accidents_schema.communes;
"

# Via Python
python -c "
from src.database import DatabaseManager
db = DatabaseManager()
print(db.generate_data_report())
"
```

## 6⃣ Requêtes Simples

```python
from src.database import DatabaseManager

db = DatabaseManager()

# 1. Accidents en 2022
df = db.query_accidents(annee=2022, limit=100)
print(df[['date_accident', 'nom_com', 'gravite_max']].head(10))

# 2. Communes les plus dangereuses
df = db.get_stats_communes(limit=10)
print(df[['nom_com', 'nombre_accidents', 'nombre_deces']])

# 3. Scores de danger
df = db.get_danger_scores(limit=10)
print(df[['nom_com', 'score_danger', 'categorie_risque']])

# 4. Data heatmap
df = db.get_heatmap_data(annee=2023, limit=1000)
print(f"{len(df)} points pour heatmap")

# 5. Statistiques usagers (âge)
df = db.get_stats_usagers(limit=10)
print(df[['age', 'nombre_usagers', 'nombre_deces']])

# Fermer connections
db.close_pool()
```

## 7⃣ Validations

```python
from src.database import DatabaseManager

db = DatabaseManager()

# Vérifier intégrité
stats = db.validate_data_integrity()
print(f"Accidents: {stats['accidents']}")
print(f"Sans commune: {stats['accidents_sans_commune']}")
print(f"Doublons détectés: {stats['doublons']}")

# Rapport complet
print(db.generate_data_report())
```

## 8⃣ Troubleshooting

### Erreur: "psycopg2.OperationalError: could not connect to server"

```bash
# Vérifier PostgreSQL lancé
sudo systemctl status postgresql
sudo systemctl start postgresql

# Ou sur macOS:
brew services start postgresql
```

### Erreur: "Database accidents_db does not exist"

```bash
psql -U postgres -c "CREATE DATABASE accidents_db ENCODING 'UTF8';"
```

### Erreur: "column XXXX does not exist"

```bash
# Schéma n'a pas été créé, relancer:
psql -U postgres -d accidents_db -f src/database/schema.sql
```

### Performance lente?

```bash
# Recalculer indexes
psql -U postgres -d accidents_db -c "
REINDEX DATABASE accidents_db;
ANALYZE;
"
```

##  Exemples d'Analyses

### Accidents graves par département

```python
df = db.query_accidents(gravite_min=3)
df_stats = df.groupby('code_dept').agg({
    'id_accident': 'count',
    'nombre_personnes': 'sum'
}).sort_values('nombre_personnes', ascending=False)
print(df_stats)
```

### Weekend vs Semaine

```python
df = db.get_stats_temporelles(annee=2022)
df['jour_type'] = df['jour_semaine'].apply(
    lambda x: 'Weekend' if x >= 6 else 'Semaine'
)
print(df.groupby('jour_type')['nombre_accidents'].sum())
```

### Heatmap (Folium)

```python
import folium
from src.database import DatabaseManager

db = DatabaseManager()
df = db.get_heatmap_data(annee=2023, limit=5000)

m = folium.Map(location=[46.2276, 2.2137], zoom_start=6)

for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=3,
        popup=f"Gravité: {row['gravite_max']}",
        color='red' if row['gravite_max'] == 4 else 'orange'
    ).add_to(m)

m.save('heatmap_accidents.html')
print(" Heatmap créée: heatmap_accidents.html")
```

---

##  Checklist Démarrage Phase 3

- [ ] PostgreSQL installé et lancé
- [ ] `.env` configuré (DB_HOST, DB_USER, DB_PASSWORD)
- [ ] `CREATE DATABASE accidents_db;`
- [ ] `python src/database/load_postgresql.py`
- [ ] Vérifier avec `python -c "from src.database import DatabaseManager; db = DatabaseManager()"`
- [ ] Tests réussis: `python -m pytest tests/test_database.py`

---

##  Fichiers Associés

- **Schema**: `src/database/schema.sql` (544 lignes)
- **Chargement**: `src/database/load_postgresql.py` (650 lignes)
- **Requêtes**: `src/database/database_utils.py` (550 lignes)
- **Documentation**: `docs/DATABASE_SCHEMA.md` (complète)
- **Tests**: `tests/test_database.py` (à créer en Phase 4)

---

**Phase 3 Complétée! **
Prêt pour Phase 4 (API FastAPI)
