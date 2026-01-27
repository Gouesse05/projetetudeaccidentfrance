-- ============================================================================
-- TEMPORAL ANALYSIS
-- ============================================================================

-- Accidents by year
SELECT 
    EXTRACT(YEAR FROM date_accident)::int as annee,
    COUNT(*) as nombre_accidents,
    SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) as nombre_deces,
    ROUND(AVG(gravite_max)::numeric, 2) as gravite_moyenne
FROM accidents
GROUP BY EXTRACT(YEAR FROM date_accident)
ORDER BY annee DESC;

-- Accidents by month (all years)
SELECT 
    EXTRACT(MONTH FROM date_accident)::int as mois,
    COUNT(*) as nombre,
    SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) as deces,
    ROUND(AVG(gravite_max)::numeric, 2) as gravite_moyenne
FROM accidents
GROUP BY EXTRACT(MONTH FROM date_accident)
ORDER BY mois;

-- Accidents by month for a specific year
SELECT 
    EXTRACT(MONTH FROM date_accident)::int as mois,
    COUNT(*) as nombre,
    SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) as deces
FROM accidents
WHERE EXTRACT(YEAR FROM date_accident) = 2022
GROUP BY EXTRACT(MONTH FROM date_accident)
ORDER BY mois;

-- Accidents by day of week
SELECT 
    jour_semaine,
    COUNT(*) as nombre,
    ROUND(AVG(gravite_max)::numeric, 2) as gravite_moyenne,
    SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) as deces
FROM accidents
GROUP BY jour_semaine
ORDER BY jour_semaine;

-- Accidents by hour of day
SELECT 
    EXTRACT(HOUR FROM heure)::int as heure,
    COUNT(*) as nombre,
    ROUND(AVG(gravite_max)::numeric, 2) as gravite_moyenne,
    ROUND(100.0 * SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) / COUNT(*)::numeric, 2) as taux_fatal_percent
FROM accidents
WHERE heure IS NOT NULL
GROUP BY EXTRACT(HOUR FROM heure)
ORDER BY heure;

-- Day vs night comparison
SELECT 
    CASE 
        WHEN EXTRACT(HOUR FROM heure) BETWEEN 22 AND 23 OR EXTRACT(HOUR FROM heure) BETWEEN 0 AND 5 THEN 'Night (22h-6h)'
        ELSE 'Day (6h-22h)'
    END as periode,
    COUNT(*) as nombre,
    ROUND(AVG(gravite_max)::numeric, 2) as gravite_moyenne,
    SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) as deces
FROM accidents
WHERE heure IS NOT NULL
GROUP BY periode;

-- Weekend vs weekday
SELECT 
    CASE 
        WHEN jour_semaine IN ('samedi', 'dimanche') THEN 'Weekend'
        ELSE 'Weekday'
    END as type_jour,
    COUNT(*) as nombre,
    ROUND(AVG(gravite_max)::numeric, 2) as gravite_moyenne,
    SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) as deces
FROM accidents
GROUP BY type_jour;
