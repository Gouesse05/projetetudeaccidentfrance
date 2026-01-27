-- ============================================================================
-- DATA MANIPULATION & EXPORT
-- ============================================================================

-- Create a materialized view for common analysis
CREATE MATERIALIZED VIEW IF NOT EXISTS v_accidents_enrichis AS
SELECT 
    a.*,
    c.nom as commune_nom,
    c.population,
    c.densite_hab_km2,
    CASE 
        WHEN EXTRACT(HOUR FROM a.heure) BETWEEN 22 AND 23 OR EXTRACT(HOUR FROM a.heure) BETWEEN 0 AND 5 THEN 'Night'
        ELSE 'Day'
    END as period_type,
    CASE 
        WHEN jour_semaine IN ('samedi', 'dimanche') THEN 'Weekend'
        ELSE 'Weekday'
    END as weekend_flag
FROM accidents a
LEFT JOIN communes c ON a.code_com = c.code_com;

-- Create summary table for year
CREATE TEMP TABLE accidents_summary_2023 AS
SELECT 
    code_com,
    EXTRACT(MONTH FROM date_accident)::int as mois,
    COUNT(*) as nombre_accidents,
    SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) as deces,
    ROUND(AVG(gravite_max)::numeric, 2) as gravite_moyenne
FROM accidents
WHERE EXTRACT(YEAR FROM date_accident) = 2023
GROUP BY code_com, EXTRACT(MONTH FROM date_accident);

-- Export data: Top communes with all metrics
SELECT 
    ROW_NUMBER() OVER (ORDER BY nombre_accidents DESC) as rank,
    a.code_com,
    c.nom,
    COUNT(*) as nombre_accidents,
    SUM(CASE WHEN a.gravite_max = 4 THEN 1 ELSE 0 END) as deces,
    SUM(a.nombre_personnes) as personnes_impliquees,
    ROUND(AVG(a.gravite_max)::numeric, 2) as gravite_moyenne,
    c.population,
    ROUND(COUNT(*)::numeric / NULLIF(c.population, 0) * 100000, 2) as accidents_per_100k
FROM accidents a
JOIN communes c ON a.code_com = c.code_com
GROUP BY a.code_com, c.nom, c.population
ORDER BY nombre_accidents DESC;

-- Export data: Detailed accident records for a specific year
SELECT 
    date_accident,
    heure,
    code_com,
    code_dept,
    jour_semaine,
    gravite_max,
    nombre_personnes,
    nombre_deces,
    conditions_meteo,
    luminosite,
    type_route,
    alcoolémie
FROM accidents
WHERE EXTRACT(YEAR FROM date_accident) = 2023
ORDER BY date_accident DESC;

-- Data quality checks
SELECT 
    'Total records' as check_name,
    COUNT(*) as count_value
FROM accidents
UNION ALL
SELECT 'Records with NULL date_accident', COUNT(*) FROM accidents WHERE date_accident IS NULL
UNION ALL
SELECT 'Records with NULL code_com', COUNT(*) FROM accidents WHERE code_com IS NULL
UNION ALL
SELECT 'Records with NULL gravite_max', COUNT(*) FROM accidents WHERE gravite_max IS NULL
UNION ALL
SELECT 'Records with NULL heure', COUNT(*) FROM accidents WHERE heure IS NULL
UNION ALL
SELECT 'Distinct communes', COUNT(DISTINCT code_com) FROM accidents
UNION ALL
SELECT 'Distinct departments', COUNT(DISTINCT code_dept) FROM accidents
UNION ALL
SELECT 'Date range (from)', MIN(date_accident)::text FROM accidents
UNION ALL
SELECT 'Date range (to)', MAX(date_accident)::text FROM accidents;

-- Find data inconsistencies
SELECT 
    'gravite_max out of range' as issue,
    COUNT(*) as count_value
FROM accidents
WHERE gravite_max NOT IN (1, 2, 3, 4)
UNION ALL
SELECT 'nombre_deces without fatal', COUNT(*)
FROM accidents
WHERE nombre_deces > 0 AND gravite_max != 4
UNION ALL
SELECT 'negative nombre_personnes', COUNT(*)
FROM accidents
WHERE nombre_personnes < 0;

-- Backup data to CSV format (using COPY)
-- Note: Execute these with psql --host localhost --database accidents_db --username postgres -c "COPY query TO '/tmp/accidents_dump.csv' WITH CSV HEADER;"

-- COPY (
--   SELECT * FROM accidents WHERE EXTRACT(YEAR FROM date_accident) = 2023 LIMIT 10000
-- ) TO '/tmp/accidents_2023_sample.csv' WITH CSV HEADER;

-- COPY (
--   SELECT 
--       code_com,
--       COUNT(*) as nombre,
--       SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) as deces
--   FROM accidents
--   GROUP BY code_com
--   ORDER BY nombre DESC
-- ) TO '/tmp/accidents_by_commune.csv' WITH CSV HEADER;
