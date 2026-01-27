-- ============================================================================
-- GEOGRAPHICAL ANALYSIS
-- ============================================================================

-- Top 20 most dangerous communes
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
LIMIT 20;

-- Top 20 departments by accident count
SELECT 
    a.code_dept,
    COUNT(*) as nombre_accidents,
    SUM(CASE WHEN a.gravite_max = 4 THEN 1 ELSE 0 END) as nombres_deces,
    ROUND(AVG(a.gravite_max)::numeric, 2) as gravite_moyenne,
    ROUND(100.0 * SUM(CASE WHEN a.gravite_max = 4 THEN 1 ELSE 0 END) / COUNT(*)::numeric, 2) as taux_fatal_percent
FROM accidents a
GROUP BY a.code_dept
ORDER BY nombre_accidents DESC
LIMIT 20;

-- Top 20 regions by accident count
SELECT 
    a.region,
    COUNT(*) as nombre_accidents,
    SUM(CASE WHEN a.gravite_max = 4 THEN 1 ELSE 0 END) as nombres_deces,
    ROUND(AVG(a.gravite_max)::numeric, 2) as gravite_moyenne
FROM accidents a
WHERE a.region IS NOT NULL
GROUP BY a.region
ORDER BY nombre_accidents DESC;

-- Accidents for a specific commune (Paris example)
SELECT 
    date_accident,
    heure,
    gravite_max,
    nombre_personnes,
    nombre_deces,
    conditions_meteo,
    luminosite,
    type_route
FROM accidents
WHERE code_com = '75056'
ORDER BY date_accident DESC
LIMIT 100;

-- Commune analysis: accidents by year
SELECT 
    EXTRACT(YEAR FROM date_accident)::int as annee,
    COUNT(*) as nombre,
    SUM(CASE WHEN gravite_max = 4 THEN 1 ELSE 0 END) as deces
FROM accidents
WHERE code_com = '75056'
GROUP BY EXTRACT(YEAR FROM date_accident)
ORDER BY annee DESC;

-- Department density analysis
SELECT 
    code_dept,
    COUNT(*) as nombre_accidents,
    ROUND(COUNT(*)::numeric / NULLIF(SUM(c.population), 0) * 100000, 2) as accidents_per_100k_habitants
FROM accidents a
LEFT JOIN communes c ON a.code_com = c.code_com
GROUP BY code_dept
ORDER BY nombre_accidents DESC;
