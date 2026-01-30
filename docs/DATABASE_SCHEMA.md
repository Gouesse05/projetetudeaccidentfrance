#  Phase 3: Schéma PostgreSQL et Chargement des Données

## Vue d'ensemble

Phase 3 implémente la **couche persistence** du projet avec :
-  Schéma PostgreSQL complet (5 tables + référentiels)
-  Scripts de chargement avec validation
-  Requêtes d'analyse pré-compilées
-  Cache analytique (scores de danger)
-  Vues pour faciliter les analyses

**Objectif**: Transformer les CSV nettoyés → Base de données relationnelle optimisée pour les analyses d'assurance.

---

##  Architecture du Schéma

### Tables Principales

```

                    SCHÉMA POSTGRESQL                     
         accidents_schema (publique, 8 tables)            


RÉFÉRENTIELS:
 departements      (référenciel + données INSEE)
 communes          (géolocalisation + densité)

DONNÉES TRANSACTIONNELLES:
 accidents         (table principale, ~60k-80k rows)
 caracteristiques  (conditions de l'accident)
 lieux            (géolocalisation précise)
 usagers          (données des personnes impliquées)
 vehicules        (données des véhicules)

ANALYTIQUE:
 score_danger_commune (cache de scores composites)

VUES:
 v_accidents_enrichis (join de toutes les tables)
 v_resume_communes    (agrégations par commune)
```

### Diagramme Relationnel

```
departements (code_dept PK)
    ↓ (id_dept FK)
communes (code_com PK) 
    ↓ (id_com FK)        
accidents (num_acc PK) ←
    ↓ (id_accident FK)
     caracteristiques
     lieux
     usagers
     vehicules
    
score_danger_commune
    ↓ (id_com FK)
communes
```

### Détails des Tables

#### 1. **departements** (Référentiel)
```sql
CREATE TABLE departements (
    id_dept SERIAL PRIMARY KEY,
    code_dept VARCHAR(5) UNIQUE NOT NULL,        -- '75', '92', '13', ...
    nom_dept VARCHAR(100) NOT NULL,              -- 'Paris', 'Bouches-du-Rhône', ...
    region VARCHAR(100),                         -- 'Île-de-France', 'PACA', ...
    population BIGINT,                           -- Données INSEE
    surface_km2 DECIMAL(10, 2),
    densite_hab_km2 DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INDEXES:
- code_dept (UNIQUE)
```

#### 2. **communes** (Référentiel + Localisation)
```sql
CREATE TABLE communes (
    id_com SERIAL PRIMARY KEY,
    code_com VARCHAR(10) UNIQUE NOT NULL,        -- Code INSEE commune
    nom_com VARCHAR(100) NOT NULL,
    id_dept INTEGER FK REFERENCES departements,
    population BIGINT,
    densite_hab_km2 DECIMAL(10, 2),
    latitude DECIMAL(10, 8),                     -- Coordonnées centre commune
    longitude DECIMAL(10, 8),
    zone_urbaine BOOLEAN,                        -- TRUE si densité > 100/km²
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INDEXES:
- idx_communes_dept (id_dept)
- idx_communes_code (code_com) - pour jointures rapides

CLÉ ÉTRANGÈRE:
- id_dept → departements.id_dept (CASCADE)
```

#### 3. **accidents** (Table Principale)
```sql
CREATE TABLE accidents (
    id_accident SERIAL PRIMARY KEY,
    num_acc VARCHAR(20) UNIQUE NOT NULL,         -- Clé métier
    
    -- Date/Temps (INDEXÉE pour analyses temporelles)
    date_accident DATE NOT NULL,
    annee INTEGER NOT NULL,                      --  Indexé
    mois INTEGER CHECK (1-12),
    jour_mois INTEGER CHECK (1-31),
    jour_semaine INTEGER CHECK (1-7),            -- 1=Lundi, 7=Dimanche
    heure INTEGER CHECK (0-23),                  --  Indexé
    minute INTEGER CHECK (0-59),
    
    -- Localisation (INDEXÉE)
    id_com INTEGER FK REFERENCES communes,      --  Indexé
    
    -- Caractéristiques
    nombre_vehicules INTEGER CHECK (>0),
    nombre_personnes INTEGER CHECK (>=0),
    gravite_max INTEGER CHECK (1-4),             -- 1=Indemne, 2=Léger, 3=Hospitalisé, 4=Tué
    
    -- Métadonnées
    est_doublon BOOLEAN DEFAULT FALSE,
    source VARCHAR(50) DEFAULT 'data.gouv.fr',
    hash_md5 VARCHAR(32),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INDEXES:
- idx_accidents_date (date_accident) - pour rangées temporelles
- idx_accidents_annee (annee) - pour filtrages annuels
- idx_accidents_commune (id_com) - pour requêtes géographiques
- idx_accidents_gravite (gravite_max) - pour analyses critères
- idx_accidents_jour_semaine (jour_semaine) - pattern semaine/weekend
- idx_accidents_heure (heure) - patterns horaires
- idx_accidents_num_acc (num_acc) - clé métier
- idx_accidents_annee_mois (annee, mois) - composite pour temporel
- idx_accidents_date_gravite (date_accident, gravite_max) - composite

TRIGGERS:
- trg_update_accident_timestamp (UPDATE timestamp automatiquement)
- trg_detect_duplicates (Marquer doublons)

CLÉS ÉTRANGÈRES:
- id_com → communes.id_com (CASCADE)
```

#### 4. **caracteristiques** (Conditions)
```sql
CREATE TABLE caracteristiques (
    id_caract SERIAL PRIMARY KEY,
    id_accident INTEGER FK REFERENCES accidents (CASCADE),
    
    -- Conditions
    luminosite VARCHAR(50),                      -- 'jour', 'crépuscule', 'nuit'
    agglomeration BOOLEAN,                       -- 1=Oui, 0=Non
    intersection BOOLEAN,                        -- 1=À intersection
    conditions_atmosphere VARCHAR(100),          -- 'normal', 'pluie', 'brouillard', ...
    
    -- Route
    type_route VARCHAR(50),
    surface_route VARCHAR(50),
    infrastructure VARCHAR(100),
    type_collision VARCHAR(50),
    
    completude_pct DECIMAL(5, 2),                -- % de complétude de données
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INDEXES:
- idx_caract_accident (id_accident)

CLÉS ÉTRANGÈRES:
- id_accident → accidents.id_accident (CASCADE)
```

#### 5. **lieux** (Géolocalisation Précise)
```sql
CREATE TABLE lieux (
    id_lieu SERIAL PRIMARY KEY,
    id_accident INTEGER FK REFERENCES accidents (CASCADE),
    
    -- Géolocalisation  INDEXÉE pour heatmaps
    latitude DECIMAL(10, 8),
    longitude DECIMAL(10, 8),
    
    -- Descriptions
    type_route VARCHAR(50),
    surface_route VARCHAR(50),
    situation VARCHAR(100),
    infrastructure VARCHAR(100),
    est_metropole BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INDEXES:
- idx_lieux_accident (id_accident)
- idx_lieux_geom (latitude, longitude) - pour requêtes de proximité

CLÉS ÉTRANGÈRES:
- id_accident → accidents.id_accident (CASCADE)
```

#### 6. **usagers** (Personnes Impliquées)
```sql
CREATE TABLE usagers (
    id_usager SERIAL PRIMARY KEY,
    id_accident INTEGER FK REFERENCES accidents (CASCADE),
    num_vehicule INTEGER,                        -- 1=conducteur, 2+ passagers
    num_occupant INTEGER,
    
    -- Démographie (INDEXÉE pour analyses)
    date_naissance DATE,
    age INTEGER,                                 --  Indexé
    sexe VARCHAR(1),                             -- '1'=M, '2'=F, 'Unknown'
    
    -- Sécurité
    place_vehicule VARCHAR(50),
    equipement_securite VARCHAR(100),            -- 'ceinture', 'casque', ...
    
    -- Gravité pour cet usager
    gravite INTEGER CHECK (1-4),                 -- 1=Indemne, 2=Léger, 3=Hospitalisé, 4=Décédé
    
    -- État
    activite VARCHAR(50),                        -- 'travail', 'loisir', 'personnel', ...
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INDEXES:
- idx_usagers_accident (id_accident)
- idx_usagers_age (age) - pour distributions par âge
- idx_usagers_sexe (sexe) - pour analyses genre

CLÉS ÉTRANGÈRES:
- id_accident → accidents.id_accident (CASCADE)
```

#### 7. **vehicules** (Données Véhicules)
```sql
CREATE TABLE vehicules (
    id_vehicule SERIAL PRIMARY KEY,
    id_accident INTEGER FK REFERENCES accidents (CASCADE),
    num_vehicule INTEGER,                        -- Numéro du véhicule dans accident
    
    -- Caractéristiques
    categorie_vehicule VARCHAR(50),              -- 'voiture', 'camion', 'moto', ...
    
    -- Manœuvre
    sens_circulation VARCHAR(50),
    nombre_occupants INTEGER CHECK (>=0),
    type_manoeuvre VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INDEXES:
- idx_vehicules_accident (id_accident)
- idx_vehicules_categorie (categorie_vehicule) - pour analyses par type

CLÉS ÉTRANGÈRES:
- id_accident → accidents.id_accident (CASCADE)
```

#### 8. **score_danger_commune** (Cache Analytique)
```sql
CREATE TABLE score_danger_commune (
    id_score SERIAL PRIMARY KEY,
    id_com INTEGER FK REFERENCES communes (CASCADE),
    
    -- Compteurs
    nombre_accidents INTEGER DEFAULT 0,
    nombre_personnes_impliquees INTEGER DEFAULT 0,
    nombre_personnes_blessee INTEGER DEFAULT 0,
    nombre_personnes_tuees INTEGER DEFAULT 0,
    gravite_moyenne DECIMAL(5, 2),
    
    -- Score Composite (0-100)
    score_danger DECIMAL(5, 2),                  --  Indexé pour tri rapide
    score_frequence DECIMAL(5, 2),               -- 50% du score
    score_gravite DECIMAL(5, 2),                 -- 30% du score
    score_personnes DECIMAL(5, 2),               -- 20% du score
    
    -- Catégorisation
    categorie_risque VARCHAR(20),                -- 'TRÈS_ÉLEVÉ', 'ÉLEVÉ', 'MOYEN', 'FAIBLE'
    
    -- Temporalité
    date_calcul DATE,
    annee_reference INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INDEXES:
- idx_score_commune (id_com)
- idx_score_danger (score_danger) - pour tri efficace
- idx_score_categorie (categorie_risque) - pour filtres

CLÉS ÉTRANGÈRES:
- id_com → communes.id_com (CASCADE)

UTILISATION:
- Cache pré-calculé pour éviter aggrégations coûteuses
- Recalculé par procédure stockée calculer_scores_danger()
- Utilisé pour classement communes/départements
```

---

##  Vues Analytiques

### 1. **v_accidents_enrichis** (Jointure Complète)

```sql
VIEW: v_accidents_enrichis
 Accidents enrichis avec toutes les dimensions
 Colonnes: num_acc, date, lieu (commune, région, densité), 
             gravité, conditions (jour/heure), geolocalisation
 Usage: Base pour toutes les analyses ad-hoc

SELECT * FROM accidents_schema.v_accidents_enrichis
WHERE annee = 2022 
  AND jour_semaine IN (6, 7)  -- Weekends
  AND gravite_max >= 3        -- Accidents graves
ORDER BY gravite_max DESC;
```

### 2. **v_resume_communes** (Agrégations)

```sql
VIEW: v_resume_communes
 Une ligne par commune
 Colonnes: statistics (accidents, personnes, gravité moyenne, max)
            démographie (population, densité)
 Usage: Dashboard, comparaisons communes
 Index implicite: nom_com, densité

SELECT * FROM accidents_schema.v_resume_communes
ORDER BY nombre_accidents DESC
LIMIT 50;
```

---

##  Procédures Stockées

### **calculer_scores_danger()** (Recalcul des Scores)

```sql
-- Recalculer tous les scores par commune
SELECT * FROM accidents_schema.calculer_scores_danger();

-- Résultat: Nombre de scores calculés
-- Formule: score = (freq * 0.5) + (gravité * 0.3) + (personnes * 0.2)
```

---

##  Installation et Utilisation

### 1. **Créer le Schéma**

```bash
# Option 1: Via psql
psql -U postgres -d accidents_db -f src/database/schema.sql

# Option 2: Via Python
python src/database/load_postgresql.py --create-schema
```

### 2. **Charger les Données**

```bash
# Charger depuis CSV nettoyés (data/cleaned/)
python src/database/load_postgresql.py

# Avec truncate (reset DB)
python src/database/load_postgresql.py --force

# Sans mettre à jour communes
python src/database/load_postgresql.py --skip-communes
```

**Résultat Attendu:**
```
 Schéma PostgreSQL créé avec succès!

Tables créées:
  - departements (référentiel)
  - communes (référentiel + données démographiques)
  - accidents (table principale)
  - caracteristiques (conditions)
  - lieux (géolocalisation)
  - usagers (données personnes)
  - vehicules (données véhicules)
  - score_danger_commune (analytique)

Vues créées:
  - v_accidents_enrichis
  - v_resume_communes

STATISTIQUES CHARGEMENT:
  • Communes: 12,234
  • Accidents: 68,432
  • Caractéristiques: 68,432
  • Lieux: 68,432
  • Usagers: 245,123
  • Véhicules: 89,321
```

### 3. **Utiliser les Requêtes**

```python
from src.database.database_utils import DatabaseManager

db = DatabaseManager()

# Accidents graves (2022)
df = db.query_accidents(annee=2022, gravite_min=3)

# Communes les plus dangereuses
df = db.get_stats_communes(limit=20)

# Scores de danger
df = db.get_danger_scores(limit=50)

# Heatmap data
df = db.get_heatmap_data(annee=2023)

# Statistiques temporelles
df = db.get_stats_temporelles(annee=2022)

# Usagers par âge
df = db.get_stats_usagers()

# Rapport qualité
print(db.generate_data_report())

db.close_pool()
```

---

##  Cas d'Usage Analytiques

### 1. **Analyse de Risque par Région**

```python
# Top 10 communes les plus dangereuses en Île-de-France
df = db.query_accidents(dep='75')
df_stats = df.groupby('nom_com').agg({
    'nombre_personnes': 'sum',
    'gravite_max': ['mean', 'max']
}).sort_values(by='nombre_personnes', ascending=False).head(10)
```

### 2. **Patterns Temporels (Heures de Pointe)**

```python
# Accidents par heure
df = db.get_stats_temporelles(annee=2022)
df_heure = df[df['heure'].isin([7, 8, 9, 17, 18, 19])]
df_heure.groupby('heure')['nombre_accidents'].sum().plot()
```

### 3. **Analyse Démographique (Âge, Genre)**

```python
# Taux de mortalité par tranche d'âge
df = db.get_stats_usagers()
df['tranche_age'] = pd.cut(df['age'], bins=[0, 25, 45, 65, 100])
df.groupby('tranche_age').apply(lambda x: x['nombre_deces'] / x['nombre_usagers'] * 100)
```

### 4. **Scoring Communes pour Assurance**

```python
# Top 10 communes à risque très élevé
df = db.get_danger_scores(limit=100)
df_tres_eleve = df[df['categorie_risque'] == 'TRÈS_ÉLEVÉ']

# Paramètres de tarification
df_tres_eleve[['nom_com', 'score_danger', 'nombre_accidents', 
                'nombre_personnes_tuees', 'population']]
```

### 5. **Proximité Géographique (Requête Spatiale)**

```python
# Accidents à proximité (5km) d'une adresse
df = db.get_accidents_near(latitude=48.8566, longitude=2.3522, distance_km=5)
# Retourne accidents avec distance_km calculée
```

---

##  Sécurité et Permissions

```sql
-- Permissions par défaut (PUBLIC peut READ)
GRANT USAGE ON SCHEMA accidents_schema TO PUBLIC;
GRANT SELECT ON ALL TABLES IN SCHEMA accidents_schema TO PUBLIC;
GRANT SELECT ON ALL VIEWS IN SCHEMA accidents_schema TO PUBLIC;

-- Pour l'application (INSERT/UPDATE):
-- Créer rôle application avec permissions UPDATE seulement
CREATE ROLE app_user;
GRANT UPDATE ON accidents_schema.* TO app_user;
```

---

##  Performances Attendues

| Requête | Temps | Rows |
|---------|-------|------|
| SELECT * FROM accidents (limit 1000) | 50ms | 1000 |
| Stats communes (group by) | 200ms | 250 |
| Heatmap data (10k points) | 150ms | 10k |
| Requête proximité (5km) | 100ms | Variable |
| Danger scores (top 50) | 75ms | 50 |

**Optimisations:**
- Indexes composites sur (annee, mois), (date_accident, gravite_max)
- Cache danger_scores (pré-calculé)
- Vues materialisées (optionnel, Phase 4)

---

##  Prochaines Étapes (Phase 4)

1. **API FastAPI** : Endpoints REST sur requêtes ci-dessus
2. **Matérialisation Vues** : Pour très grandes analyses
3. **Partitioning** : Partitionner par année si > 500M rows
4. **Réplication** : Backup/Failover PostgreSQL

---

##  Fichiers Livérés

- `src/database/schema.sql` (544 lignes) - DDL complet
- `src/database/load_postgresql.py` (650 lignes) - Chargeur
- `src/database/database_utils.py` (550 lignes) - Requêtes
- `docs/DATABASE_SCHEMA.md` (CE FICHIER) - Documentation

**Total Phase 3: 1,700+ lignes de code + documentation**

