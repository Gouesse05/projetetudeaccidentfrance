# SQL Queries for Direct PostgreSQL Access

This directory contains pure SQL queries for direct database analysis without needing Python or any libraries.

## Files Overview

### 1. `01_schema.sql`
Explore the database structure:
- List all tables
- Get column definitions
- Check table sizes

### 2. `02_basic_queries.sql`
Basic data exploration:
- Count total accidents
- Sample data
- Basic statistics
- Gravity level distribution

### 3. `03_temporal_analysis.sql`
Time-based analysis:
- Accidents by year
- Accidents by month
- Day of week analysis
- Hour of day analysis
- Day vs night comparison
- Weekend vs weekday

### 4. `04_geographical_analysis.sql`
Location-based analysis:
- Top dangerous communes
- Top dangerous departments
- Top dangerous regions
- Specific commune analysis
- Accidents per capita

### 5. `05_severity_analysis.sql`
Condition and severity analysis:
- Weather conditions impact
- Light conditions impact
- Road type analysis
- Alcohol involvement
- Most dangerous combinations

### 6. `06_advanced_analysis.sql`
Advanced statistical analysis:
- Year-over-year trends
- Moving averages
- Peak danger hours
- High-risk time windows
- Fatal accident statistics
- Multi-vehicle analysis

### 7. `07_data_export.sql`
Data export and quality checks:
- Create materialized views
- Data quality checks
- Consistency checks
- Export queries for CSV/JSON

## How to Use

### Option 1: Using psql command line

```bash
# Connect to database
psql -h localhost -U postgres -d accidents_db

# Run a SQL file
\i queries/01_schema.sql

# Run a specific query
\c accidents_db
SELECT * FROM accidents LIMIT 5;
```

### Option 2: Execute specific SQL file

```bash
# From bash, execute entire file
psql -h localhost -U postgres -d accidents_db -f queries/01_schema.sql

# Export results to CSV
psql -h localhost -U postgres -d accidents_db -f queries/04_geographical_analysis.sql -o results.csv
```

### Option 3: Using pgAdmin or DBeaver
1. Open your SQL client (pgAdmin, DBeaver, etc.)
2. Create a new SQL query window
3. Copy and paste queries from the files
4. Execute directly in the interface

### Option 4: Using Python with psycopg2

```python
import psycopg2

conn = psycopg2.connect("dbname=accidents_db user=postgres password=yourpassword host=localhost")
cursor = conn.cursor()

# Read SQL file
with open('queries/01_schema.sql', 'r') as f:
    query = f.read()

# Execute queries
for line in query.split(';'):
    if line.strip():
        cursor.execute(line)
        print(cursor.fetchall())

conn.close()
```

## Common Commands

### List tables
```sql
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
```

### View schema
```sql
\d accidents
```

### Get row count
```sql
SELECT COUNT(*) FROM accidents;
```

### Export query to CSV
```bash
psql -h localhost -U postgres -d accidents_db -c "
  SELECT * FROM accidents LIMIT 1000;
" > output.csv
```

### Create backup
```bash
pg_dump -h localhost -U postgres accidents_db > backup.sql
```

### Restore from backup
```bash
psql -h localhost -U postgres accidents_db < backup.sql
```

## Database Connection Details

| Parameter | Default |
|-----------|---------|
| Host | localhost |
| Port | 5432 |
| Database | accidents_db |
| User | postgres |
| Password | (from .env) |

## Quick Reference: Most Useful Queries

### Top 10 Most Dangerous Locations
```sql
SELECT code_com, nom, COUNT(*) as nombre
FROM accidents a
JOIN communes c ON a.code_com = c.code_com
GROUP BY code_com, nom
ORDER BY nombre DESC
LIMIT 10;
```

### Fatal Accidents Rate
```sql
SELECT 
    SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END)::float / COUNT(*) * 100 as fatal_rate
FROM accidents;
```

### Accidents by Weather
```sql
SELECT conditions_meteo, COUNT(*) 
FROM accidents 
GROUP BY conditions_meteo 
ORDER BY COUNT(*) DESC;
```

### Peak Danger Hour
```sql
SELECT EXTRACT(HOUR FROM heure)::int as heure, COUNT(*) 
FROM accidents 
GROUP BY EXTRACT(HOUR FROM heure) 
ORDER BY COUNT(*) DESC LIMIT 1;
```

## Tips

1. **Performance**: Use LIMIT when exploring large queries
2. **Indexes**: Check for missing indexes on frequently filtered columns
3. **EXPLAIN**: Use EXPLAIN ANALYZE to optimize slow queries
4. **Transactions**: Always commit or rollback after modifications
5. **Backups**: Create regular backups before running UPDATE/DELETE queries

## Notes

- All queries are read-only except for data export operations
- Some queries may take time on large datasets
- Adjust LIMIT and WHERE clauses for better performance
- Always test on sample data first

---

**Last Updated**: January 2026  
**Database Version**: PostgreSQL 12+  
**Test Data**: French Road Accident Database (2021-2024)
