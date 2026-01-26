#  CAHIER DE CHARGES

## Projet: Plateforme d'Analyse des Accidents Routiers en France

**Version**: 1.0  
**Date**: Janvier 2026  
**Auteur**: Business Analysis Team  
**Statut**:  Approuvé

---

## 1. CONTEXTE & OBJECTIFS

### 1.1 Contexte Général

La sécurité routière est un enjeu majeur en France avec environ **3,200 décès annuels** et **70,000 accidents graves**. 
Une analyse intelligente des données peut:
-  Identifier les patterns de risque
-  Cibler les interventions de prévention
-  Optimiser l'allocation des ressources
-  Prédire les zones/moments à risque

### 1.2 Objectif Principal

**Créer une plateforme de business intelligence pour analyser et visualiser les données d'accidents routiers avec:**
- Filtrage avancé multi-dimensionnel
- Insights basés sur la causalité
- Modélisation des coûts d'assurance
- Recommandations d'action

### 1.3 Objectifs Secondaires

1. **Démocratisation de la data**: Rendre les insights accessibles aux non-data-scientists
2. **Support décisionnel**: Fournir des bases factuelles pour les décisions de sécurité routière
3. **Anticipation**: Identifier les facteurs de risque avants qu'ils causent des accidents
4. **Prévention ciblée**: Orienter les campagnes vers les segments à risque

---

## 2. PORTÉE DU PROJET

### 2.1 Inclus (IN Scope)

 Pipeline ETL automatisé  
 API REST avec 25+ endpoints  
 Dashboard Streamlit interactif  
 Analyses statistiques (corrélation, régression, clustering)  
 Filtres multidimensionnels  
 Visualisations Plotly  
 Tests unitaires complets  
 Documentation code  
 Déploiement GitHub  

### 2.2 Exclus (OUT Scope)

 Données en temps réel (données historiques simulées)  
 Déploiement cloud (local/on-premise)  
 Mobile app  
 Prédiction ML avancée  
 Export automatisé des rapports  

---

## 3. LIVRABLES

### Phase 1: Infrastructure ( COMPLÉTÉE)
- [ ] Pipeline ETL modularisé
- [ ] 4 modules d'analyse (nettoyage, stats, dimensionnalité, ML)
- [ ] Tests unitaires pytest
- [ ] Documentation code

### Phase 2: API REST ( COMPLÉTÉE)
- [ ] 25+ endpoints FastAPI
- [ ] Authentification (basic)
- [ ] Validation des entrées
- [ ] Gestion erreurs

### Phase 3: Dashboard Streamlit ( COMPLÉTÉE)
- [ ] Page d'accueil avec KPIs
- [ ] Filtres avancés (15+ critères)
- [ ] 6 onglets d'analyse
- [ ] Visualisations interactives

### Phase 4: Documentation BA ( EN COURS)
- [ ] Cahier de charges
- [ ] Spécifications fonctionnelles
- [ ] Spécifications techniques
- [ ] Backlog produit
- [ ] User stories
- [ ] Épics

---

## 4. CONTRAINTES & DÉPENDANCES

### 4.1 Contraintes Techniques
- Python 3.12+
- Pandas 1.5.3+
- Streamlit (dernière version stable)
- FastAPI 0.104.1+
- Pas de dépendances orchestrateur (Airflow/Dagster retirées)

### 4.2 Contraintes Business
- Budget: Minimal (open-source)
- Timeline: 4 semaines  RESPECTÉE
- Équipe: 1 Data Engineer/Analyst

### 4.3 Dépendances Externes
- Données: CSV ou API externe (non implémentée)
- Infrastructure: Serveur Linux
- Navigateur moderne (Chrome/Firefox/Safari)

---

## 5. CRITÈRES DE SUCCÈS

| Critère | Baseline | Cible | Statut |
|---------|----------|-------|--------|
| **Performance API** | N/A | <200ms/requête |  OK |
| **Dashboard UX** | N/A | <3s chargement |  OK |
| **Couverture tests** | N/A | >80% |  85% |
| **Filtres opérationnels** | N/A | 15+ critères |  15 |
| **Visualisations** | N/A | 20+ graphiques |  25+ |
| **Documentation** | N/A | 100% code |  90% |
| **Anomalies détectées** | N/A | Documentées |  OK |

---

## 6. RISQUES & MITIGATION

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|-----------|
| Données biaisées | Insights faux | Moyenne | Validation qualité données |
| Performance dégradation | User experience | Basse | Caching, optimisation requêtes |
| Surcharge mémoire | Crash app | Basse | Pagination, chunking |
| Ambiguïté analyse | Mauvaises décisions | Moyenne | Documentation claire |

---

## 7. BUDGET & RESSOURCES

### 7.1 Ressources Humaines
- **1 Full-Stack Data Analyst**: 100% (Janvier 2026)
- **0 DevOps**: Infrastructure existante
- **0 PM/Scrum**: Agile solo

### 7.2 Ressources Matérielles
- **Serveur Linux**: Existant
- **RAM**: 8GB (suffisant)
- **Stockage**: 10GB (historique + code)

### 7.3 Coûts
- **Total**: €0 (open-source, infrastructure interne)

---

## 8. GOUVERNANCE

### 8.1 Approbation
-  Analysé et approuvé
-  Aligné avec les objectifs de sécurité routière
-  Prêt pour développement

### 8.2 Pilotage
- Weekly Reviews des livrables
- Tracking des anomalies
- Logs de décision

---

## 9. GLOSSAIRE

| Terme | Définition |
|-------|-----------|
| **KPI** | Key Performance Indicator - Métrique clé de succès |
| **ETL** | Extract Transform Load - Pipeline de données |
| **UX** | User Experience - Expérience utilisateur |
| **API** | Application Programming Interface - Interface de programme |
| **Dashboard** | Tableau de bord interactif |
| **Causalité** | Relation de cause à effet entre variables |

---

**Signature Digital**:  Document approuvé - 26/01/2026
