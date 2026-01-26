# 📦 PRODUCT BACKLOG

## Plateforme d'Analyse des Accidents Routiers

**Version**: 2.0  
**Date**: 26 Janvier 2026  
**Product Owner**: Business Analysis Team  
**Statut**: ✅ Phase 5 Complete, Phase 6 Planifiée

---

## PRIORITÉS & ROADMAP

```
PHASE 5 (ACTUELLE)       | STATUS    | COMPLETION
─────────────────────────────────────────────────
Infrastructure           | ✅ DONE   | 100%
API REST                 | ✅ DONE   | 100%
Dashboard Streamlit      | ✅ DONE   | 100%
Tests & QA              | ✅ DONE   | 100%
Documentation BA        | 🔄 DOING  | 90%
GitHub Deployment       | ✅ DONE   | 100%
─────────────────────────────────────────────────

PHASE 6 (Q2 2026)        | STATUS    | TIMEFRAME
─────────────────────────────────────────────────
Real Data Integration   | ⏳ PLANNED | Apr-Jun
ML Predictions         | ⏳ PLANNED | May-Jun
Cloud Deployment       | ⏳ PLANNED | Jun
─────────────────────────────────────────────────
```

---

## BACKLOG GLOBAL (25 items)

### ✅ DONE (Phase 5) - 20 items

| ID | Title | Epic | Points | Status |
|----|-------|------|--------|--------|
| US-001 | Dashboard KPIs | EPIC-001 | 5 | ✅ |
| US-002 | Filtres Avancés | EPIC-001 | 8 | ✅ |
| US-003 | Onglets Analyse | EPIC-001 | 13 | ✅ |
| US-004 | Graphiques Plotly | EPIC-001 | 5 | ✅ |
| US-005 | Mise à Jour Dynamique | EPIC-001 | 3 | ✅ |
| US-006 | Classe d'Âge | EPIC-002 | 5 | ✅ |
| US-007 | Genre Analysis | EPIC-002 | 3 | ✅ |
| US-008 | Expérience Conducteur | EPIC-002 | 5 | ✅ |
| US-009 | Coûts Assurance | EPIC-002 | 8 | ✅ |
| US-010 | Profil Accident Grave | EPIC-002 | 5 | ✅ |
| US-011 | Alcool vs Gravité | EPIC-003 | 5 | ✅ |
| US-012 | Luminosité Analysis | EPIC-003 | 4 | ✅ |
| US-013 | Météo Analysis | EPIC-003 | 4 | ✅ |
| US-014 | Interprétations Auto | EPIC-003 | 5 | ✅ |
| US-015 | Recommandations | EPIC-003 | 5 | ✅ |
| US-016 | Pipeline ETL | EPIC-004 | 13 | ✅ |
| US-017 | Analyses Stats | EPIC-004 | 8 | ✅ |
| US-018 | Machine Learning | EPIC-004 | 8 | ✅ |
| US-019 | API REST | EPIC-004 | 13 | ✅ |
| US-020 | Tests Unitaires | EPIC-004 | 8 | ✅ |

**Total Phase 5**: 20 US | 135 points | ✅ 100% Done

---

### 🟡 NEXT SPRINT (Phase 6 Early) - 5 items

#### US-021: Intégrer Données Réelles DGCN

**ID**: US-021  
**Epic**: EPIC-005 (New: Data Integration)  
**Priorité**: 🔴 CRITIQUE  
**Points Story**: 13  
**Timeframe**: Apr 2026  
**Status**: ⏳ BACKLOG  

**Description**:  
Remplacer données simulées par vraies données du Gouvernement français (DGCN).

**Acceptation Criteria**:
- [ ] API DGCN intégrée
- [ ] Colonnes mappées correctement
- [ ] 200K+ records chargés
- [ ] Performance <5s dashboard
- [ ] Insights revalidés

**Tasks** (Subtasks):
1. [ ] Authentification API DGCN
2. [ ] Mapping schemas (local → DGCN)
3. [ ] Data validation & quality checks
4. [ ] Bulk loading infrastructure
5. [ ] Caching strategy (Redis)

**Dépendances**: Aucune (prêt à start)

**Risk**: API DGCN peut être instable (medium risk)

---

#### US-022: ML Predictions - Gravité Accident

**ID**: US-022  
**Epic**: EPIC-006 (New: Predictive Analytics)  
**Priorité**: 🟡 HAUTE  
**Points Story**: 13  
**Timeframe**: May 2026  
**Status**: ⏳ BACKLOG  

**Description**:  
Implémenter model ML prédisant la gravité d'un accident basé sur conditions.

**Input Features**:
- age, experience, alcoolémie, fatigue
- heure, luminosité, conditions_meteo
- vitesse, type_route

**Output**:
- Prédiction: Léger/Modéré/Grave/Mortel
- Probability: [0.2, 0.3, 0.35, 0.15]
- Confidence score

**Acceptation Criteria**:
- [ ] Model trained (Random Forest)
- [ ] Accuracy >75%
- [ ] Feature importance calculée
- [ ] Déployé dans API
- [ ] Dashboard UI pour predictions

**Techniques**:
- Random Forest Classifier (already code in ML module)
- Cross-validation 5-fold
- Feature scaling & selection

---

#### US-023: Export Rapports PDF

**ID**: US-023  
**Epic**: EPIC-001 (Extended)  
**Priorité**: 🟡 HAUTE  
**Points Story**: 8  
**Timeframe**: May 2026  
**Status**: ⏳ BACKLOG  

**Description**:  
Permettre export des analyses en rapports PDF professionnels.

**Format Rapport**:
1. Cover page (titre, date, auteur)
2. Executive summary (KPIs)
3. Filtres appliqués
4. Tous les graphiques
5. Interprétations
6. Recommandations
7. Appendix (données détaillées)

**Acceptation Criteria**:
- [ ] PDF generation working
- [ ] Tous les graphiques inclus
- [ ] Formatage professionnel
- [ ] Download button dans UI
- [ ] Performance <10s per report

**Library**: ReportLab ou WeasyPrint

---

#### US-024: Alertes Anomalies Real-Time

**ID**: US-024  
**Epic**: EPIC-07 (New: Monitoring)  
**Priorité**: 🟡 HAUTE  
**Points Story**: 8  
**Timeframe**: Jun 2026  
**Status**: ⏳ BACKLOG  

**Description**:  
Système d'alertes detekant anomalies en données ou prédictions.

**Anomalies à Détecter**:
- Spike accidents (>2x moyenne horaire)
- Corrélations causales changent
- Outliers dans prédictions
- Data quality issues

**Actions**:
- Email alert à analyste
- Notification dashboard
- Log anomalies

---

#### US-025: Mobile App (React Native)

**ID**: US-025  
**Epic**: EPIC-08 (New: Mobile)  
**Priorité**: 🟢 BASSE  
**Points Story**: 21  
**Timeframe**: H2 2026  
**Status**: ⏳ BACKLOG  

**Description**:  
Application mobile (iOS/Android) pour consultations dashboard.

**Features Clés**:
- KPIs widgets
- Filtres simplifiés
- Favoris dashboards
- Notifications

**Tech Stack**:
- React Native / Expo
- Redux (state management)
- Call API REST (existing)

**Notes**: Basse priorité, futur feature

---

## BACKLOG DÉTAILLÉ (Priorité)

### 🔴 CRITIQUE (Must Have)

```
✅ US-001 → US-020: Phase 5 (DONE)
🟡 US-021: Real Data Integration (NEXT)
🟡 US-022: ML Predictions (NEXT)
```

### 🟡 HAUTE (Should Have)

```
🟡 US-023: Export PDF
🟡 US-024: Alertes Anomalies
⏳ Refacto Filtering Logic (Code Quality)
⏳ CI/CD Pipeline GitHub Actions (DevOps)
⏳ Performance Optimization (Speed)
```

### 🟢 BASSE (Nice To Have)

```
🟢 US-025: Mobile App
⏳ Internationalisation (i18n)
⏳ Dark Mode
⏳ Custom Dashboards (User Builder)
⏳ Data Export Excel/CSV (Advanced)
```

---

## DÉPENDANCES & BLOCKERS

### Bloqueurs Actuels

| Item | Bloqueur | Status |
|------|----------|--------|
| US-021 | API DGCN auth access | ✅ Obtenu (pending) |
| US-024 | Email service config | ⏳ TBD |
| US-025 | Mobile development env | ⏳ TBD |

---

## ESTIMATION CAPACITÉ

### Velocity Historical

```
Sprint 1 (Semaine 1-2): 25 points ✅
Sprint 2 (Semaine 3-4): 25 points ✅
Sprint 3 (Semaine 5-6): 30 points ✅
Sprint 4 (Semaine 7-8): 30 points ✅
──────────────────────────────────
Average Velocity: 27.5 points/2-week sprint
```

### Forecast Phase 6

```
Sprint 5 (Apr 1-15):   25 points (US-021, US-023 partiel)
Sprint 6 (Apr 16-30):  25 points (US-021 fin, US-023 fin)
Sprint 7 (May 1-15):   30 points (US-022, US-024 start)
Sprint 8 (May 16-31):  30 points (US-024 fin)
Sprint 9 (Jun 1-15):   25 points (Buffer, refinements)
──────────────────────────────────────────────────────
Total Phase 6: ~135 points (5 epics)
Duration: 4.5 months (realistic)
```

---

## RELEASE PLAN

### Release 1.0 (Current - January 2026)
✅ Dashboard Streamlit complet  
✅ API REST 25+ endpoints  
✅ Infrastructure robuste  
✅ Tests & documentation  

**Features**: 20 US | 135 points | ✅ SHIPPED

---

### Release 2.0 (Target: June 2026)
🔄 Real data integration  
🔄 ML predictions (gravité)  
🔄 Export PDF rapports  
🔄 Alertes anomalies  

**Target Features**: 5 US | 52 points | ETA: Q2 2026

---

### Release 3.0 (Future: H2 2026)
⏳ Mobile app  
⏳ Advanced exports  
⏳ Custom dashboards  

---

## SUCCESS METRICS

### Phase 5 (Current)
- [x] 20/20 US completed
- [x] 85% test coverage
- [x] 0 critical bugs
- [x] <3s dashboard load time
- [x] 25+ API endpoints

### Phase 6 (Target)
- [ ] 5/5 new US completed
- [ ] 200K+ real records loaded
- [ ] ML model >75% accuracy
- [ ] Mobile app MVP ready
- [ ] 0 downtime deployments

### Global (Full Product)
- [ ] 25K+ daily active users
- [ ] 99.9% API uptime
- [ ] <100ms API response
- [ ] 0 data loss incidents

---

## STAKEHOLDER FEEDBACK (Expected)

### Analyste Sécurité Routière
> "Dashboard clairement laid out. Les filtres puissants. Veut vraies données."

### Manager Assurance
> "Modèle coûts simplifié mais juste. Veut prédictions ML."

### Décideur Public
> "Insights pertinents. Recommandations actionnables. Veut export rapports."

### Développeur Tiers
> "API bien structurée. Documentation claire. Peut intégrer facilement."

---

## DOCUMENT CONTROL

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 26/01/2026 | 1.0 | Initial | BA Team |
| TBD | 2.0 | Post Phase 6 | TBD |

**Approuvé par**: Product Owner  
**Reviewé par**: Engineering Lead  
**Statut**: ✅ FINAL - ACTIVE

---

**Next Review Date**: 10/02/2026 (Sprint planning)
