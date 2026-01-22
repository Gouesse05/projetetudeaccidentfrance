-- =============================================================================
-- SCHÉMA POSTGRESQL - BASE DE DONNÉES ACCIDENTS ROUTIERS
-- =============================================================================
-- Description: Base de données pour analyse accidents corporels routiers
-- Domaine: Gestion du risque assurance responsabilité civile
-- Créé: 2026-01-22
-- =============================================================================

-- Paramètres de la session
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

-- =============================================================================
-- 1. SUPPRESSION DES OBJETS EXISTANTS (si nécessaire)
-- =============================================================================

DROP TABLE IF EXISTS usagers CASCADE;
DROP TABLE IF EXISTS vehicules CASCADE;
DROP TABLE IF EXISTS lieux CASCADE;
DROP TABLE IF EXISTS caracteristiques CASCADE;
DROP TABLE IF EXISTS accidents CASCADE;
DROP TABLE IF EXISTS communes CASCADE;
DROP TABLE IF EXISTS departements CASCADE;

DROP SCHEMA IF EXISTS accidents_schema CASCADE;

-- =============================================================================
-- 2. CRÉATION DU SCHÉMA
-- =============================================================================

CREATE SCHEMA accidents_schema;
GRANT ALL ON SCHEMA accidents_schema TO PUBLIC;

-- =============================================================================
-- 3. TABLES DE RÉFÉRENCE
-- =============================================================================

-- Table: Départements
CREATE TABLE accidents_schema.departements (
    id_dept SERIAL PRIMARY KEY,
    code_dept VARCHAR(5) UNIQUE NOT NULL,
    nom_dept VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    population BIGINT,
    surface_km2 DECIMAL(10, 2),
    densite_hab_km2 DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE accidents_schema.departements IS 'Référentiel des départements français';
COMMENT ON COLUMN accidents_schema.departements.code_dept IS 'Code INSEE du département (ex: 75)';

-- Table: Communes
CREATE TABLE accidents_schema.communes (
    id_com SERIAL PRIMARY KEY,
    code_com VARCHAR(10) UNIQUE NOT NULL,
    nom_com VARCHAR(100) NOT NULL,
    id_dept INTEGER NOT NULL REFERENCES accidents_schema.departements(id_dept) ON DELETE CASCADE,
    population BIGINT,
    densite_hab_km2 DECIMAL(10, 2),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(10, 8),
    zone_urbaine BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE accidents_schema.communes IS 'Référentiel des communes françaises';
COMMENT ON COLUMN accidents_schema.communes.code_com IS 'Code INSEE de la commune';
COMMENT ON COLUMN accidents_schema.communes.zone_urbaine IS 'TRUE si commune urbaine (densité > 100 hab/km²)';

-- Index
CREATE INDEX idx_communes_dept ON accidents_schema.communes(id_dept);
CREATE INDEX idx_communes_code ON accidents_schema.communes(code_com);

-- =============================================================================
-- 4. TABLES PRINCIPALES
-- =============================================================================

-- Table: Accidents
CREATE TABLE accidents_schema.accidents (
    id_accident SERIAL PRIMARY KEY,
    num_acc VARCHAR(20) UNIQUE NOT NULL,
    
    -- Date et temps
    date_accident DATE NOT NULL,
    annee INTEGER NOT NULL,
    mois INTEGER CHECK (mois BETWEEN 1 AND 12),
    jour_mois INTEGER CHECK (jour_mois BETWEEN 1 AND 31),
    jour_semaine INTEGER CHECK (jour_semaine BETWEEN 1 AND 7),
    heure INTEGER CHECK (heure BETWEEN 0 AND 23),
    minute INTEGER CHECK (minute BETWEEN 0 AND 59),
    
    -- Localisation
    id_com INTEGER NOT NULL REFERENCES accidents_schema.communes(id_com) ON DELETE CASCADE,
    
    -- Caractéristiques accidents
    nombre_vehicules INTEGER CHECK (nombre_vehicules > 0),
    nombre_personnes INTEGER CHECK (nombre_personnes >= 0),
    gravite_max INTEGER CHECK (gravite_max BETWEEN 1 AND 4),
    
    -- Gravité: 1=Indemne, 2=Blessé léger, 3=Blessé hospitalisé, 4=Tué
    
    -- Métadonnées
    est_doublon BOOLEAN DEFAULT FALSE,
    source VARCHAR(50) DEFAULT 'data.gouv.fr',
    hash_md5 VARCHAR(32),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE accidents_schema.accidents IS 'Table principale: accidents routiers corporels';
COMMENT ON COLUMN accidents_schema.accidents.num_acc IS 'Numéro unique d''accident (clé métier)';
COMMENT ON COLUMN accidents_schema.accidents.gravite_max IS '1=Indemne, 2=Blessé léger, 3=Blessé hospitalisé, 4=Tué';

-- Indexes critiques
CREATE INDEX idx_accidents_date ON accidents_schema.accidents(date_accident);
CREATE INDEX idx_accidents_annee ON accidents_schema.accidents(annee);
CREATE INDEX idx_accidents_commune ON accidents_schema.accidents(id_com);
CREATE INDEX idx_accidents_gravite ON accidents_schema.accidents(gravite_max);
CREATE INDEX idx_accidents_jour_semaine ON accidents_schema.accidents(jour_semaine);
CREATE INDEX idx_accidents_heure ON accidents_schema.accidents(heure);
CREATE INDEX idx_accidents_num_acc ON accidents_schema.accidents(num_acc);

-- Index composite pour analyses temporelles
CREATE INDEX idx_accidents_annee_mois ON accidents_schema.accidents(annee, mois);
CREATE INDEX idx_accidents_date_gravite ON accidents_schema.accidents(date_accident, gravite_max);

-- Table: Caractéristiques accidents
CREATE TABLE accidents_schema.caracteristiques (
    id_caract SERIAL PRIMARY KEY,
    id_accident INTEGER NOT NULL REFERENCES accidents_schema.accidents(id_accident) ON DELETE CASCADE,
    
    -- Conditions
    luminosite VARCHAR(50),  -- jour, crépuscule, nuit, etc.
    agglomeration BOOLEAN,   -- 1=Agglomération, 0=Hors agglomération
    intersection BOOLEAN,    -- 1=Intersection, 0=Hors intersection
    conditions_atmosphere VARCHAR(100),
    
    -- Route et infrastructure
    type_route VARCHAR(50),
    surface_route VARCHAR(50),
    infrastructure VARCHAR(100),
    
    -- Type collision
    type_collision VARCHAR(50),
    
    -- Données manquantes
    completude_pct DECIMAL(5, 2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE accidents_schema.caracteristiques IS 'Détails des conditions et caractéristiques des accidents';

CREATE INDEX idx_caract_accident ON accidents_schema.caracteristiques(id_accident);

-- Table: Lieux
CREATE TABLE accidents_schema.lieux (
    id_lieu SERIAL PRIMARY KEY,
    id_accident INTEGER NOT NULL REFERENCES accidents_schema.accidents(id_accident) ON DELETE CASCADE,
    
    -- Géolocalisation
    latitude DECIMAL(10, 8),
    longitude DECIMAL(10, 8),
    
    -- Descriptifs
    type_route VARCHAR(50),
    surface_route VARCHAR(50),
    situation VARCHAR(100),
    infrastructure VARCHAR(100),
    
    -- Hors métropole?
    est_metropole BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE accidents_schema.lieux IS 'Localisation géographique des accidents';

CREATE INDEX idx_lieux_accident ON accidents_schema.lieux(id_accident);
CREATE INDEX idx_lieux_geom ON accidents_schema.lieux(latitude, longitude);

-- Table: Usagers
CREATE TABLE accidents_schema.usagers (
    id_usager SERIAL PRIMARY KEY,
    id_accident INTEGER NOT NULL REFERENCES accidents_schema.accidents(id_accident) ON DELETE CASCADE,
    num_vehicule INTEGER,
    num_occupant INTEGER,
    
    -- Démographie
    date_naissance DATE,
    age INTEGER,
    sexe VARCHAR(1),  -- 1=Masculin, 2=Féminin
    
    -- Position et sécurité
    place_vehicule VARCHAR(50),
    equipement_securite VARCHAR(100),
    
    -- Gravité pour cet usager
    gravite INTEGER CHECK (gravite BETWEEN 1 AND 4),
    
    -- État
    activite VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE accidents_schema.usagers IS 'Données des usagers impliqués dans accidents';
COMMENT ON COLUMN accidents_schema.usagers.gravite IS '1=Indemne, 2=Blessé léger, 3=Hospitalisé, 4=Tué';

CREATE INDEX idx_usagers_accident ON accidents_schema.usagers(id_accident);
CREATE INDEX idx_usagers_age ON accidents_schema.usagers(age);
CREATE INDEX idx_usagers_sexe ON accidents_schema.usagers(sexe);

-- Table: Véhicules
CREATE TABLE accidents_schema.vehicules (
    id_vehicule SERIAL PRIMARY KEY,
    id_accident INTEGER NOT NULL REFERENCES accidents_schema.accidents(id_accident) ON DELETE CASCADE,
    num_vehicule INTEGER,
    
    -- Caractéristiques
    categorie_vehicule VARCHAR(50),
    
    -- Sens circulation
    sens_circulation VARCHAR(50),
    
    -- Nombre occupants
    nombre_occupants INTEGER CHECK (nombre_occupants >= 0),
    
    -- Manœuvre/impact
    type_manoeuvre VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE accidents_schema.vehicules IS 'Données des véhicules impliqués dans accidents';

CREATE INDEX idx_vehicules_accident ON accidents_schema.vehicules(id_accident);
CREATE INDEX idx_vehicules_categorie ON accidents_schema.vehicules(categorie_vehicule);

-- =============================================================================
-- 5. TABLES D'ANALYSE
-- =============================================================================

-- Table: Score de danger par commune (cache analytique)
CREATE TABLE accidents_schema.score_danger_commune (
    id_score SERIAL PRIMARY KEY,
    id_com INTEGER NOT NULL REFERENCES accidents_schema.communes(id_com) ON DELETE CASCADE,
    
    -- Métriques
    nombre_accidents INTEGER DEFAULT 0,
    nombre_personnes_impliquees INTEGER DEFAULT 0,
    nombre_personnes_blessee INTEGER DEFAULT 0,
    nombre_personnes_tuees INTEGER DEFAULT 0,
    gravite_moyenne DECIMAL(5, 2),
    
    -- Score composite (0-100)
    score_danger DECIMAL(5, 2),
    score_frequence DECIMAL(5, 2),
    score_gravite DECIMAL(5, 2),
    score_personnes DECIMAL(5, 2),
    
    -- Catégorisation
    categorie_risque VARCHAR(20),  -- 'TRÈS_ÉLEVÉ', 'ÉLEVÉ', 'MOYEN', 'FAIBLE'
    
    -- Période
    date_calcul DATE,
    annee_reference INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE accidents_schema.score_danger_commune IS 'Scores de danger composite par commune (table de cache)';

CREATE INDEX idx_score_commune ON accidents_schema.score_danger_commune(id_com);
CREATE INDEX idx_score_danger ON accidents_schema.score_danger_commune(score_danger);
CREATE INDEX idx_score_categorie ON accidents_schema.score_danger_commune(categorie_risque);

-- =============================================================================
-- 6. VUE POUR ANALYSES RAPIDES
-- =============================================================================

-- Vue: Accidents enrichis
CREATE VIEW accidents_schema.v_accidents_enrichis AS
SELECT
    a.id_accident,
    a.num_acc,
    a.date_accident,
    a.annee,
    a.mois,
    a.jour_semaine,
    a.heure,
    a.nombre_vehicules,
    a.nombre_personnes,
    a.gravite_max,
    
    -- Localisation
    c.code_com,
    c.nom_com,
    d.code_dept,
    d.nom_dept,
    d.region,
    c.population,
    c.densite_hab_km2,
    c.zone_urbaine,
    
    -- Géographie
    l.latitude,
    l.longitude,
    
    -- Dates
    CASE WHEN a.jour_semaine = 6 OR a.jour_semaine = 7 THEN 'Weekend' ELSE 'Semaine' END as periode,
    CASE 
        WHEN a.heure >= 6 AND a.heure < 9 THEN 'Heures de pointe matin'
        WHEN a.heure >= 17 AND a.heure < 20 THEN 'Heures de pointe soir'
        WHEN a.heure >= 22 OR a.heure < 6 THEN 'Nuit'
        ELSE 'Heures creuses'
    END as plage_horaire,
    
    -- Métadonnées
    a.created_at,
    a.updated_at
    
FROM accidents_schema.accidents a
LEFT JOIN accidents_schema.communes c ON a.id_com = c.id_com
LEFT JOIN accidents_schema.departements d ON c.id_dept = d.id_dept
LEFT JOIN accidents_schema.lieux l ON a.id_accident = l.id_accident;

-- Vue: Résumé par commune
CREATE VIEW accidents_schema.v_resume_communes AS
SELECT
    c.id_com,
    c.code_com,
    c.nom_com,
    d.code_dept,
    d.nom_dept,
    d.region,
    c.population,
    c.densite_hab_km2,
    c.zone_urbaine,
    
    COUNT(DISTINCT a.id_accident) as nombre_accidents,
    SUM(a.nombre_personnes) as nombre_personnes_impliquees,
    AVG(a.gravite_max) as gravite_moyenne,
    MAX(a.gravite_max) as gravite_max,
    
    COUNT(DISTINCT a.id_accident) * 1.0 / COUNT(*) as ratio_accidents_par_annee
    
FROM accidents_schema.communes c
LEFT JOIN accidents_schema.departements d ON c.id_dept = d.id_dept
LEFT JOIN accidents_schema.accidents a ON c.id_com = a.id_com
GROUP BY c.id_com, c.code_com, c.nom_com, d.code_dept, d.nom_dept, d.region, 
         c.population, c.densite_hab_km2, c.zone_urbaine;

-- =============================================================================
-- 7. TRIGGERS POUR MAINTENANCE
-- =============================================================================

-- Trigger: Mise à jour timestamp updated_at pour accidents
CREATE OR REPLACE FUNCTION accidents_schema.update_accident_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_accident_timestamp
BEFORE UPDATE ON accidents_schema.accidents
FOR EACH ROW
EXECUTE FUNCTION accidents_schema.update_accident_timestamp();

-- Trigger: Détection doublons
CREATE OR REPLACE FUNCTION accidents_schema.detect_duplicates()
RETURNS TRIGGER AS $$
BEGIN
    -- Marquer comme doublon si même num_acc et date
    IF EXISTS (
        SELECT 1 FROM accidents_schema.accidents 
        WHERE num_acc = NEW.num_acc AND id_accident != NEW.id_accident
    ) THEN
        NEW.est_doublon = TRUE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_detect_duplicates
BEFORE INSERT OR UPDATE ON accidents_schema.accidents
FOR EACH ROW
EXECUTE FUNCTION accidents_schema.detect_duplicates();

-- =============================================================================
-- 8. PROCÉDURES STOCKÉES
-- =============================================================================

-- Procédure: Recalculer les scores de danger
CREATE OR REPLACE FUNCTION accidents_schema.calculer_scores_danger()
RETURNS TABLE (nombre_scores_calcules INTEGER) AS $$
DECLARE
    v_count INTEGER := 0;
BEGIN
    TRUNCATE TABLE accidents_schema.score_danger_commune;
    
    INSERT INTO accidents_schema.score_danger_commune (
        id_com,
        nombre_accidents,
        nombre_personnes_impliquees,
        nombre_personnes_tuees,
        gravite_moyenne,
        score_danger,
        score_frequence,
        score_gravite,
        score_personnes,
        categorie_risque,
        date_calcul,
        annee_reference
    )
    SELECT
        c.id_com,
        COUNT(DISTINCT a.id_accident) as nb_accidents,
        COALESCE(SUM(a.nombre_personnes), 0),
        COALESCE(COUNT(CASE WHEN a.gravite_max = 4 THEN 1 END), 0),
        COALESCE(AVG(a.gravite_max), 0),
        
        -- Score composite (pondéré)
        ROUND(
            (COUNT(DISTINCT a.id_accident) / MAX(stats.max_accidents) * 100) * 0.5 +
            (COALESCE(AVG(a.gravite_max), 0) / 4 * 100) * 0.3 +
            (COALESCE(SUM(a.nombre_personnes), 0) / MAX(stats.max_personnes) * 100) * 0.2
        , 2) as score_danger,
        
        ROUND((COUNT(DISTINCT a.id_accident) / MAX(stats.max_accidents) * 100), 2),
        ROUND((COALESCE(AVG(a.gravite_max), 0) / 4 * 100), 2),
        ROUND((COALESCE(SUM(a.nombre_personnes), 0) / MAX(stats.max_personnes) * 100), 2),
        
        CASE 
            WHEN (COUNT(DISTINCT a.id_accident) / MAX(stats.max_accidents) * 100) > 70 THEN 'TRÈS_ÉLEVÉ'
            WHEN (COUNT(DISTINCT a.id_accident) / MAX(stats.max_accidents) * 100) > 50 THEN 'ÉLEVÉ'
            WHEN (COUNT(DISTINCT a.id_accident) / MAX(stats.max_accidents) * 100) > 25 THEN 'MOYEN'
            ELSE 'FAIBLE'
        END,
        
        CURRENT_DATE,
        EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER
        
    FROM accidents_schema.communes c
    LEFT JOIN accidents_schema.accidents a ON c.id_com = a.id_com
    CROSS JOIN (
        SELECT 
            MAX(accident_count) as max_accidents,
            MAX(person_count) as max_personnes
        FROM (
            SELECT 
                COUNT(DISTINCT a2.id_accident) as accident_count,
                SUM(a2.nombre_personnes) as person_count
            FROM accidents_schema.accidents a2
            GROUP BY a2.id_com
        ) stats_temp
    ) stats
    GROUP BY c.id_com;
    
    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN QUERY SELECT v_count;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 9. DONNÉES INITIALES (Référentiels)
-- =============================================================================

-- Insérer quelques départements (exemple)
INSERT INTO accidents_schema.departements (code_dept, nom_dept, region, population, surface_km2, densite_hab_km2)
VALUES 
    ('75', 'Paris', 'Île-de-France', 2165423, 105.4, 20541),
    ('92', 'Hauts-de-Seine', 'Île-de-France', 1613329, 176.5, 9138),
    ('93', 'Seine-Saint-Denis', 'Île-de-France', 1458269, 236.2, 6172),
    ('94', 'Val-de-Marne', 'Île-de-France', 1308709, 245.5, 5330),
    ('13', 'Bouches-du-Rhône', 'Provence-Alpes-Côte d''Azur', 2023474, 5087.9, 398),
    ('69', 'Rhône', 'Auvergne-Rhône-Alpes', 1861040, 2861.1, 651)
ON CONFLICT (code_dept) DO NOTHING;

-- =============================================================================
-- 10. GRANT PERMISSIONS
-- =============================================================================

GRANT USAGE ON SCHEMA accidents_schema TO PUBLIC;
GRANT SELECT ON ALL TABLES IN SCHEMA accidents_schema TO PUBLIC;
GRANT SELECT ON ALL VIEWS IN SCHEMA accidents_schema TO PUBLIC;

-- =============================================================================
-- FIN CRÉATION SCHÉMA
-- =============================================================================

-- Status
\echo '✅ Schéma PostgreSQL créé avec succès!'
\echo ''
\echo 'Tables créées:'
\echo '  - departements (référentiel)'
\echo '  - communes (référentiel + données démographiques)'
\echo '  - accidents (table principale)'
\echo '  - caracteristiques (conditions)'
\echo '  - lieux (géolocalisation)'
\echo '  - usagers (données personnes)'
\echo '  - vehicules (données véhicules)'
\echo '  - score_danger_commune (analytique)'
\echo ''
\echo 'Vues créées:'
\echo '  - v_accidents_enrichis'
\echo '  - v_resume_communes'
\echo ''
