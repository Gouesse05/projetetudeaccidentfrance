#  SPÉCIFICATIONS FONCTIONNELLES

## Plateforme d'Analyse des Accidents Routiers

**Version**: 2.0  
**Date**: 26 Janvier 2026  
**Auteur**: Business Analyst  
**Statut**:  Finalisées

---

## 1. INTRODUCTION

### 1.1 But du Document
Documenter **tous les comportements attendus** du système du point de vue utilisateur, sans détails techniques.

### 1.2 Audience
- Product Managers
- Analystes métier
- Testeurs QA
- Utilisateurs finaux

---

## 2. DESCRIPTION GÉNÉRALE DU SYSTÈME

### 2.1 Périmètre Fonctionnel

La plateforme offre **3 interfaces principales**:

```

   Plateforme Analyse Accidents Routiers 

  1. Dashboard Streamlit (Interface UX)  
  2. API REST (Intégrations)             
  3. Pipeline ETL (Traitement données)   

```

### 2.2 Utilisateurs Cibles

| Persona | Besoin Principal | Fréquence |
|---------|-----------------|-----------|
| **Analyste de Sécurité Routière** | Insights accidents + recommandations | Quotidien |
| **Manager Trésorerie/Assurance** | Analyse coûts assurance par profil | Hebdomadaire |
| **Décideur Public** | KPIs hauts niveaux + tendances | Mensuel |
| **Développeur** | Accès API pour intégrations | À la demande |

---

## 3. FONCTIONNALITÉS PRINCIPALES

##  SECTION A: DASHBOARD STREAMLIT

### A1. ÉCRAN D'ACCUEIL - Tableau de Bord Synthétique

**ID**: FUNC-A1  
**Priorité**:  CRITIQUE

#### Description
L'utilisateur voit à l'ouverture du dashboard une vue synthétique avec KPIs clés.

#### Comportements Attendus

**A1.1 - Affichage KPIs Dynamiques**
-  Afficher 6 KPIs en cartes metrics:
  - Nombre total d'accidents (filtré)
  - Nombre victimes totales
  - Nombre accidents graves (gravité >= 3)
  - Coût assurance moyen
  - Âge moyen conducteurs
  - Expérience moyenne

-  Chaque KPI affiche:
  - Valeur absolue
  - Delta en % par rapport à l'ensemble des données

**A1.2 - Mise à Jour Temps Réel**
-  Les KPIs se mettent à jour instantanément quand filtres changent
-  Latence acceptable: <500ms

**A1.3 - Couleurs & Styling**
-  Accidents graves: couleur rouge (alerte)
-  Alcool détecté: couleur orange
-  Coûts assurance: couleur rouge progressif

**Critère d'Acceptation**:
- [ ] Tous les 6 KPIs s'affichent
- [ ] Mise à jour dynamique au changement de filtres
- [ ] Pas d'erreur API
- [ ] Latence <500ms

---

### A2. BARRE LATÉRALE - Filtres Avancés

**ID**: FUNC-A2  
**Priorité**:  CRITIQUE

#### Description
La barre latérale gauche contient tous les filtres permettant l'analyse multi-dimensionnelle.

#### Comportements Attendus

**A2.1 - Filtre Dates**
-  2 champs date picker:
  - Date Min (défaut: 01/01/2023)
  - Date Max (défaut: 31/12/2023)
-  Validation: Date Min <= Date Max

**A2.2 - Filtres Démographiques** (NEW)
-  Multi-select classe d'âge:
  - 18-24 (Jeunes)
  - 25-34
  - 35-44
  - 45-54
  - 55-64
  - 65+ (Seniors)
-  Multi-select genre: Homme / Femme
-  Double slider expérience: Min/Max (0-38 ans)

**A2.3 - Filtres Temporels**
-  Multi-select saisons: Hiver, Printemps, Été, Automne
-  Multi-select type jour: Jour Travail, Week-end
-  Double slider heure: Min/Max (0-23)

**A2.4 - Filtres Gravité & Risque**
-  Multi-select gravité: Léger, Modéré, Grave, Mortel
-  Checkbox alcool: Avec/Sans
-  Checkbox fatigue: Avec/Sans

**A2.5 - Filtres Conditions**
-  Multi-select météo: Sec, Pluie, Neige, Brouillard
-  Multi-select luminosité: Plein jour, Crépuscule, Nuit
-  Multi-select type route: Autoroute, RN, Départementale, Route locale
-  Double slider vitesse: Min/Max (km/h)

**A2.6 - Comportement Filtres**
-  Tous les filtres sont combinables (AND logic)
-  Reset button pour réinitialiser tous les filtres
-  Sauvegarde locale des filtres (sessionStorage)

**Critère d'Acceptation**:
- [ ] 15+ filtres disponibles
- [ ] Comportement AND (tous critères appliqués)
- [ ] Validation des entrées
- [ ] UX fluide sans lag

---

### A3. ONGLETS D'ANALYSE - 6 Vues Spécialisées

**ID**: FUNC-A3  
**Priorité**:  CRITIQUE

#### Description
6 onglets thématiques permettant différentes perspectives d'analyse.

---

#### **ONGLET 1:  Tendances Temporelles**

**Comportements Attendus**:

**A3.1.1 - Accidents par Heure**
-  Graphique bar chart (Plotly)
-  X-axis: Heure (0-23)
-  Y-axis: Nombre d'accidents
-  Couleur: gradient rouge (Reds)
-  Hover: affiche exact count

**A3.1.2 - Gravité par Heure**
-  Graphique line chart
-  X-axis: Heure
-  Y-axis: Gravité moyenne
-  Markers sur points
-  Trend visible

**A3.1.3 - Distribution Jour Semaine**
-  Bar chart coloré (Blues)
-  Ordre chronologique lundi-dimanche
-  Hover: count + %

**A3.1.4 - Distribution Saison**
-  Pie chart avec couleurs distinctes
-  Labels: Saison + %
-  Explode automne (légère)

**Critère d'Acceptation**:
- [ ] 4 graphiques affichés
- [ ] Interactivité Plotly (zoom, hover, export)
- [ ] Mise à jour avec filtres

---

#### **ONGLET 2:  Démographie**

**Comportements Attendus**:

**A3.2.1 - Accidents par Classe d'Âge**
-  Bar chart multi-colore
-  X-axis: Classe d'âge
-  Y-axis: Nombre
-  Couleur: gradient gravité (RdYlGn_r)

**A3.2.2 - Accidents par Genre**
-  Bar chart
-  Homme vs Femme
-  Comparaison visuelle claire

**A3.2.3 - Expérience du Conducteur**
-  Bar chart par catégorie:
  - <2 ans
  - 2-5 ans
  - 5-10 ans
  - >10 ans

**A3.2.4 - Tableau Résumé**
-  Tableau pivot:
  - Colonne: Classe d'âge
  - Lignes:
    - Gravité moyenne
    - Victimes moyennes
    - % Alcool détecté
    - Nombre accidents

**Critère d'Acceptation**:
- [ ] 4 visualisations par classe d'âge
- [ ] Tableau exportable (CSV)
- [ ] Données cohérentes entre graphiques

---

#### **ONGLET 3:  Assurance**

**Comportements Attendus**:

**A3.3.1 - Coûts par Classe d'Âge**
-  Bar chart couleur Reds
-  Y-axis: Coût en €/an
-  Tri décroissant

**A3.3.2 - Coûts par Genre**
-  Bar chart Homme vs Femme
-  Différence claire visible

**A3.3.3 - Coûts par Expérience**
-  Bar chart 4 catégories
-  Novices plus chers
-  Experts moins chers

**A3.3.4 - Tableau Détaillé**
-  Statistiques par classe d'âge:
  - Coût moyen
  - Coût min
  - Coût max
  - Écart-type
  - Gravité moyenne

**A3.3.5 - Info Box Facteurs**
-  Affiche multiplicateurs coûts:
  - Âge: Jeunes x2.0, Seniors x1.8
  - Expérience: Novice +50%, Expert -30%
  - Historique: Graves +30%, Modérés +10%
  - Genre: Hommes +15%

**Critère d'Acceptation**:
- [ ] Coûts affichés avec devise (€)
- [ ] Tableau avec 5+ statistiques
- [ ] Explications claires des facteurs

---

#### **ONGLET 4:  Causalité**

**Comportements Attendus**:

**A3.4.1 - Âge vs Gravité**
-  Bar chart groupé par tranches d'âge
-  Couleur: Léger/Modéré/Grave/Mortel
-  Mode: group (pas stacked)

**A3.4.2 - Expérience vs Gravité**
-  Bar chart groupé par catégories expérience
-  Même couleurs gravité

**A3.4.3 - Alcool vs Gravité**
-  Bar chart: Avec Alcool vs Sans
-  Distribution gravité pour chaque cas
-  **Interprétation texte**: "Alcool augmente gravité de +X%"

**A3.4.4 - Luminosité vs Gravité**
-  Bar chart: Plein jour, Crépuscule, Nuit
-  **Interprétation texte**: "Nuit augmente gravité de +X%"

**A3.4.5 - Météo vs Gravité**
-  Bar chart: Sec, Pluie, Neige, Brouillard

**A3.4.6 - Route vs Gravité**
-  Bar chart stacked par type route

**Critère d'Acceptation**:
- [ ] Causalités clairement visibles
- [ ] Interprétations générées automatiquement
- [ ] Calculs exacts (vérifiables)
- [ ] Texte métier (pas technique)

---

#### **ONGLET 5:  Facteurs de Risque**

**Comportements Attendus**:

**A3.5.1 - Classe d'Âge + Genre**
-  Bar chart groupé 2D
-  X: Classe d'âge
-  Color: Genre

**A3.5.2 - Expérience + Alcool**
-  Bar chart groupé
-  X: Catégorie expérience
-  Color: Alcool Oui/Non

**A3.5.3 - Tableau Facteurs Risque**
-  8 facteurs listés:
  1. Alcool (nombre + %)
  2. Fatigue (nombre + %)
  3. Nuit (nombre + %)
  4. Mauvais temps (nombre + %)
  5. Vitesse >80 (nombre + %)
  6. Jeunes <25 (nombre + %)
  7. Novices <2 ans (nombre + %)
  8. Seniors >70 (nombre + %)

**Critère d'Acceptation**:
- [ ] Tableau actualisé avec filtres
- [ ] Pourcentages corrects
- [ ] Combinaisons risque visibles

---

#### **ONGLET 6:  Insights & Recommandations**

**Comportements Attendus**:

**A3.6.1 - Heure Critique (Info Box)**
-  Titre: " Heure Critique: XXh"
-  Affiche: Gravité moyenne à cette heure
-  Recommandation: Action suggérée

**A3.6.2 - Saison Critique (Info Box)**
-  Titre: " Saison Critique: XXXX"
-  Affiche: Nombre accidents
-  Recommandation: Campagne ciblée

**A3.6.3 - KPIs Profil (3 métriques)**
-  Âge moyen des accidents graves
-  Expérience moyenne
-  Coût assurance moyen

**A3.6.4 - Profil Type Accident Grave**
-  Genre prédominant
-  Classe d'âge prédominante
-  Heure moyenne
-  Vitesse moyenne
-  % accidents nuit
-  % mauvais temps
-  Victimes moyennes

**Critère d'Acceptation**:
- [ ] Insights générés correctement
- [ ] Recommandations pertinentes
- [ ] Cas "pas de données" géré

---

## 4. INTERFACE API REST

### FUNC-B1: Endpoints Disponibles

**ID**: FUNC-B1  
**Priorité**:  HAUTE

#### Catégories d'Endpoints

**B1.1 - Data Loading**
- POST `/api/load-data` → Charger données
- GET `/api/data/sample` → Données d'exemple

**B1.2 - Analyses Statistiques**
- GET `/api/stats/descriptive` → Statistiques descriptives
- GET `/api/stats/correlation` → Matrice corrélation
- GET `/api/stats/chi2?var1=X&var2=Y` → Test chi-carré

**B1.3 - Clustering & Réduction**
- POST `/api/analysis/clustering` → K-means clustering
- GET `/api/analysis/pca` → Analyse PCA
- GET `/api/analysis/mca` → Analyse MCA

**B1.4 - Machine Learning**
- POST `/api/ml/predict-severity` → Prédire gravité
- POST `/api/ml/feature-importance` → Importance features

**Critère d'Acceptation**:
- [ ] 25+ endpoints implémentés
- [ ] Documentation complète (Swagger)
- [ ] Validation des entrées
- [ ] Gestion erreurs appropriée

---

## 5. EXIGENCES DE DONNÉES

### FUNC-C1: Sources et Format

**ID**: FUNC-C1  
**Priorité**:  HAUTE

#### C1.1 - Sources Acceptées
-  CSV files
-  JSON arrays
-  API externes (à implémenter)

#### C1.2 - Colonnes Requises
```
date, heure, jour_semaine, mois
classe_age, genre, annee_permis, experience
gravite, nombre_victimes, nombre_vehicles
type_route, luminosite, conditions_meteo
alcoolémie, fatigue, vitesse
departement, agglomeration
cout_assurance_annuel
```

#### C1.3 - Qualité Données
-  Pas de valeurs NULL en colonnes essentielles
-  Types cohérents
-  Ranges valides

---

## 6. EXIGENCES NON-FONCTIONNELLES

### PERF-1: Performance

| Métrique | Cible | Statut |
|----------|-------|--------|
| Chargement page | <3s |  OK |
| Réponse API | <200ms |  OK |
| Dashboard filtrage | <500ms |  OK |
| Rendu graphiques | <1s |  OK |

### PERF-2: Disponibilité

-  99.5% uptime (local)
-  Gestion gracieuse des erreurs
-  Timeouts configurés

### PERF-3: Sécurité

-  Pas de données sensibles loggées
-  Validation tous les inputs
-  Authentification basique (optionnel)

---

## 7. CRITÈRES D'ACCEPTATION GLOBAUX

- [x] Tous les filtres fonctionnent correctement
- [x] Visualisations mises à jour dynamiquement
- [x] Pas d'erreur non gérée
- [x] Performance acceptable
- [x] UX fluide et intuitive
- [x] Documentation utilisateur
- [x] Tests utilisateurs passent

---

**Approuvé par**: Business Analyst  
**Date**: 26/01/2026  
**Version Finale**:  2.0
