-- ============================================================================
-- ADVANCED ANALYSIS & INSIGHTS
-- ============================================================================

-- Year-over-year comparison
SELECT 
    EXTRACT(YEAR FROM date_accident)::int as annee,
    EXTRACT(MONTH FROM date_accident)::int as mois,
    COUNT(*) as nombre,
    LAG(COUNT(*)) OVER (PARTITION BY EXTRACT(MONTH FROM date_accident) ORDER BY EXTRACT(YEAR FROM date_accident)) as nombre_annee_precedente
FROM accidents
GROUP BY EXTRACT(YEAR FROM date_accident), EXTRACT(MONTH FROM date_accident)
ORDER BY annee DESC, mois;

-- Trend analysis: accidents per month with moving average
WITH monthly_data AS (
    SELECT 
        DATE_TRUNC('month', date_accident)::date as mois,
        COUNT(*) as nombre
    FROM accidents
    GROUP BY DATE_TRUNC('month', date_accident)
)
SELECT 
    mois,
    nombre,
    ROUND(AVG(nombre) OVER (ORDER BY mois ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)::numeric, 0) as moving_avg_3m
FROM monthly_data
ORDER BY mois DESC;

-- Peak danger hours by day of week
SELECT 
    jour_semaine,
    EXTRACT(HOUR FROM heure)::int as heure,
    COUNT(*) as nombre,
    ROUND(AVG(gravite_max)::numeric, 2) as gravite_moyenne
FROM accidents
WHERE heure IS NOT NULL
GROUP BY jour_semaine, EXTRACT(HOUR FROM heure)
ORDER BY jour_semaine, heure;

-- High-risk time windows
SELECT 
    EXTRACT(HOUR FROM heure)::int as heure,
    jour_semaine,
    COUNT(*) as nombre,
    SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) as deces,
    ROUND(100.0 * SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) / COUNT(*)::numeric, 2) as taux_fatal_percent
FROM accidents
WHERE heure IS NOT NULL
GROUP BY EXTRACT(HOUR FROM heure), jour_semaine
HAVING COUNT(*) > 50
ORDER BY taux_fatal_percent DESC
LIMIT 20;

-- Communes with increasing trends
WITH yearly_stats AS (
    SELECT 
        code_com,
        EXTRACT(YEAR FROM date_accident)::int as annee,
        COUNT(*) as nombre
    FROM accidents
    GROUP BY code_com, EXTRACT(YEAR FROM date_accident)
)
SELECT 
    code_com,
    MAX(CASE WHEN annee = 2021 THEN nombre ELSE 0 END) as count_2021,
    MAX(CASE WHEN annee = 2022 THEN nombre ELSE 0 END) as count_2022,
    MAX(CASE WHEN annee = 2023 THEN nombre ELSE 0 END) as count_2023,
    MAX(CASE WHEN annee = 2023 THEN nombre ELSE 0 END) - MAX(CASE WHEN annee = 2021 THEN nombre ELSE 0 END) as variation_2021_2023
FROM yearly_stats
GROUP BY code_com
HAVING MAX(CASE WHEN annee = 2023 THEN nombre ELSE 0 END) > 0
ORDER BY variation_2021_2023 DESC
LIMIT 20;

-- Fatal accidents statistics
SELECT 
    COUNT(*) as total_accidents,
    SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) as fatal_accidents,
    ROUND(100.0 * SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) / COUNT(*)::numeric, 2) as fatal_percent,
    SUM(nombre_deces) as total_deces
FROM accidents;

-- Accidents without injuries vs with severity
SELECT 
    CASE 
        WHEN gravite_max = 1 THEN 'Uninjured'
        WHEN gravite_max = 2 THEN 'Minor injury'
        WHEN gravite_max = 3 THEN 'Serious injury'
        WHEN gravite_max = 4 THEN 'Fatal'
        ELSE 'Unknown'
    END as severity,
    COUNT(*) as nombre,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER()::numeric, 2) as pourcentage
FROM accidents
WHERE gravite_max IS NOT NULL
GROUP BY gravite_max
ORDER BY gravite_max;

-- Multi-vehicle accidents analysis
SELECT 
    COUNT(*) as total_accidents,
    ROUND(AVG(COALESCE(nombre_personnes, 0))::numeric, 2) as avg_personnes,
    ROUND(AVG(COALESCE(nombre_deces, 0))::numeric, 2) as avg_deces,
    MAX(nombre_personnes) as max_personnes,
    MAX(nombre_deces) as max_deces
FROM accidents;
