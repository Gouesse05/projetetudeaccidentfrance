-- ============================================================================
-- SEVERITY & CONDITIONS ANALYSIS
-- ============================================================================

-- Severity by weather conditions
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

-- Severity by light conditions
SELECT 
    luminosite,
    COUNT(*) as nombre,
    ROUND(AVG(gravite_max)::numeric, 2) as gravite_moyenne,
    SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) as deces,
    ROUND(100.0 * SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) / COUNT(*)::numeric, 2) as taux_fatal_percent
FROM accidents
WHERE luminosite IS NOT NULL
GROUP BY luminosite
ORDER BY nombre DESC;

-- Severity by road type
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

-- Combined conditions analysis
SELECT 
    conditions_meteo,
    luminosite,
    type_route,
    COUNT(*) as nombre,
    ROUND(AVG(gravite_max)::numeric, 2) as gravite_moyenne,
    SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) as deces
FROM accidents
WHERE conditions_meteo IS NOT NULL 
  AND luminosite IS NOT NULL 
  AND type_route IS NOT NULL
GROUP BY conditions_meteo, luminosite, type_route
ORDER BY nombre DESC
LIMIT 50;

-- Weather + Light interaction
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

-- Alcohol involvement analysis
SELECT 
    alcoolémie,
    COUNT(*) as nombre,
    ROUND(AVG(gravite_max)::numeric, 2) as gravite_moyenne,
    SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) as deces,
    ROUND(100.0 * SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) / COUNT(*)::numeric, 2) as taux_fatal_percent
FROM accidents
WHERE alcoolémie IS NOT NULL
GROUP BY alcoolémie
ORDER BY nombre DESC;

-- Most dangerous combinations
SELECT 
    conditions_meteo,
    luminosite,
    COUNT(*) as nombre,
    ROUND(100.0 * SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) / COUNT(*)::numeric, 2) as taux_fatal_percent
FROM accidents
WHERE conditions_meteo IS NOT NULL AND luminosite IS NOT NULL
GROUP BY conditions_meteo, luminosite
HAVING COUNT(*) > 100
ORDER BY taux_fatal_percent DESC
LIMIT 10;
