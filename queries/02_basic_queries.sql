-- ============================================================================
-- BASIC DATA QUERIES
-- ============================================================================

-- Count total accidents
SELECT COUNT(*) as total_accidents FROM accidents;

-- Get sample data
SELECT * FROM accidents LIMIT 10;

-- Get distinct years
SELECT DISTINCT EXTRACT(YEAR FROM date_accident) as annee
FROM accidents
ORDER BY annee DESC;

-- Count by gravity level
SELECT 
    gravite_max,
    COUNT(*) as nombre
FROM accidents
WHERE gravite_max IS NOT NULL
GROUP BY gravite_max
ORDER BY gravite_max;

-- Basic statistics
SELECT 
    COUNT(*) as total_accidents,
    COUNT(DISTINCT code_com) as communes,
    COUNT(DISTINCT code_dept) as departments,
    MIN(date_accident) as date_min,
    MAX(date_accident) as date_max,
    AVG(nombre_personnes::float) as avg_personnes,
    SUM(nombre_deces) as total_deces
FROM accidents;
