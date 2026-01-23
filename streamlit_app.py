"""
Streamlit Dashboard - Accidents Routiers AVANCÉ
Filtres interactifs + Démographie + Données assurance
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Dashboard Accidents - Advanced",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CACHE & DATA GENERATION
# ============================================================================

@st.cache_data
def generate_smart_accident_data():
    """Générer données réalistes avec patterns + démographie + assurance"""
    np.random.seed(42)
    n_records = 5000
    
    dates = pd.date_range('2023-01-01', periods=n_records, freq='12H')
    
    df = pd.DataFrame({
        'date': dates,
        'heure': np.random.randint(0, 24, n_records),
        'jour_semaine': dates.day_name(),
        'mois': dates.month,
    })
    
    # Saison
    df['saison'] = df['mois'].apply(
        lambda m: 'Hiver' if m in [12, 1, 2] else 
                 'Printemps' if m in [3, 4, 5] else
                 'Été' if m in [6, 7, 8] else 'Automne'
    )
    
    # DÉMOGRAPHIE
    df['age'] = np.random.normal(40, 15, n_records).astype(int)
    df['age'] = df['age'].clip(18, 85)
    
    # Classe d'âge
    def get_classe_age(age):
        if age < 25:
            return '18-24 (Jeunes)'
        elif age < 35:
            return '25-34'
        elif age < 45:
            return '35-44'
        elif age < 55:
            return '45-54'
        elif age < 65:
            return '55-64'
        else:
            return '65+ (Seniors)'
    
    df['classe_age'] = df['age'].apply(get_classe_age)
    df['genre'] = np.random.choice(['Homme', 'Femme'], n_records, p=[0.65, 0.35])
    df['annee_permis'] = np.random.randint(1985, 2023, n_records)
    df['experience'] = 2023 - df['annee_permis']
    
    # Initialiser colonnes
    df['gravite'] = 1
    df['nombre_victimes'] = 0
    df['type_route'] = 'RN'
    df['luminosite'] = 'Plein jour'
    df['conditions_meteo'] = 'Sec'
    df['alcoolémie'] = False
    df['fatigue'] = False
    df['vitesse'] = 75
    df['departement'] = np.random.choice(['75', '92', '93', '94', '91', '77', '78'], n_records)
    df['agglomeration'] = np.random.choice(['Paris', 'IDF', 'Banlieue'], n_records)
    
    # COÛT ASSURANCE (facteurs multiples)
    df['cout_assurance_base'] = 500  # EUR/an
    
    # Patterns réalistes
    for idx in df.index:
        heure = df.loc[idx, 'heure']
        saison = df.loc[idx, 'saison']
        jour = df.loc[idx, 'jour_semaine']
        age = df.loc[idx, 'age']
        experience = df.loc[idx, 'experience']
        
        # Heures de pointe
        if heure in [7, 8, 9, 17, 18, 19]:
            gravite_prob = [0.35, 0.3, 0.2, 0.15]
            victimes_base = 1.8
        else:
            gravite_prob = [0.45, 0.28, 0.18, 0.09]
            victimes_base = 1.3
        
        # Saison été = plus d'accidents
        if saison == 'Été':
            gravite_prob = [p * 0.9 if i < 2 else p * 1.2 for i, p in enumerate(gravite_prob)]
            victimes_base *= 1.15
        
        # AGE: Jeunes + Seniors = plus dangereux
        if age < 25:
            gravite_prob = [p * 0.8 if i < 2 else p * 1.4 for i, p in enumerate(gravite_prob)]
            alcool_prob = 0.30
            fatigue_prob = 0.10
        elif age > 70:
            gravite_prob = [p * 0.85 if i < 2 else p * 1.35 for i, p in enumerate(gravite_prob)]
            alcool_prob = 0.05
            fatigue_prob = 0.25
        else:
            alcool_prob = 0.12
            fatigue_prob = 0.12
        
        # EXPERIENCE: Conducteurs novices = plus de risque
        if experience < 2:
            gravite_prob = [p * 0.7 if i < 2 else p * 1.5 for i, p in enumerate(gravite_prob)]
            alcool_prob *= 1.5
        
        # Week-end: plus d'alcool, moins de fatigue travail
        if jour in ['Saturday', 'Sunday']:
            alcool_prob *= 1.2 if age < 35 else 0.9
            fatigue_prob = 0.05
        else:
            fatigue_prob *= 1.5 if experience < 2 else 1.0
        
        # Nuit = plus dangereux
        if heure >= 22 or heure <= 5:
            gravite_prob = [p * 0.8 if i < 2 else p * 1.3 for i, p in enumerate(gravite_prob)]
            alcool_prob *= 1.8
            victimes_base *= 1.3
            df.loc[idx, 'luminosite'] = 'Nuit'
        elif heure in [7, 8, 17, 18, 19, 20]:
            df.loc[idx, 'luminosite'] = 'Crépuscule'
        else:
            df.loc[idx, 'luminosite'] = 'Plein jour'
        
        # Mauvais temps
        if np.random.random() < 0.2:
            gravite_prob = [p * 0.7 if i < 2 else p * 1.5 for i, p in enumerate(gravite_prob)]
            df.loc[idx, 'conditions_meteo'] = np.random.choice(['Pluie', 'Neige', 'Brouillard'])
        
        # Données finales - Normaliser probabilités
        gravite_prob = [p / sum(gravite_prob) for p in gravite_prob]  # Normaliser à 1.0
        df.loc[idx, 'gravite'] = np.random.choice([1, 2, 3, 4], p=gravite_prob)
        df.loc[idx, 'nombre_victimes'] = max(1, int(np.random.poisson(victimes_base)))
        df.loc[idx, 'type_route'] = np.random.choice(['Autoroute', 'RN', 'Départementale', 'Route locale'])
        df.loc[idx, 'alcoolémie'] = np.random.random() < alcool_prob
        df.loc[idx, 'fatigue'] = np.random.random() < fatigue_prob
        df.loc[idx, 'vitesse'] = int(np.random.normal(75, 25))
        
        # COÛT ASSURANCE DYNAMIQUE
        cout = 500
        
        # Âge: jeunes + seniors = plus cher
        if age < 25:
            cout *= 2.0  # x2
        elif age > 70:
            cout *= 1.8  # x1.8
        else:
            cout *= 0.8  # -20%
        
        # Expérience: novice = plus cher
        if experience < 2:
            cout *= 1.5  # +50%
        elif experience > 10:
            cout *= 0.7  # -30% (bonus fidelité)
        
        # Historique sinistres (gravite = proxy)
        if df.loc[idx, 'gravite'] >= 3:
            cout *= 1.3
        elif df.loc[idx, 'gravite'] == 2:
            cout *= 1.1
        
        # Genre (statiquement, hommes paient plus)
        if df.loc[idx, 'genre'] == 'Homme':
            cout *= 1.15
        
        df.loc[idx, 'cout_assurance_base'] = int(cout)
    
    # Coût assurance annuel estimé (avec bonus/malus)
    df['cout_assurance_annuel'] = df['cout_assurance_base']
    
    return df

# Charger données
df = generate_smart_accident_data()
gravite_map = {1: 'Léger', 2: 'Modéré', 3: 'Grave', 4: 'Mortel'}
df['gravite_label'] = df['gravite'].map(gravite_map)
df['type_jour'] = df['jour_semaine'].apply(lambda x: 'Week-end' if x in ['Saturday', 'Sunday'] else 'Jour Travail')

# ============================================================================
# LAYOUT PRINCIPAL
# ============================================================================

st.title("🚗 Dashboard Accidents - Filtres Avancés & Démographie")

# Sidebar: Filtres
st.sidebar.title("🔧 Filtres Avancés")
st.sidebar.markdown("---")

with st.sidebar:
    # Filtre dates
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        min_date = st.date_input("Date Min", df['date'].min())
    with col_date2:
        max_date = st.date_input("Date Max", df['date'].max())
    
    st.markdown("---")
    
    # FILTRE DÉMOGRAPHIE
    st.subheader("👤 Profil Conducteur")
    
    classes_age = st.multiselect(
        "📊 Classe d'âge",
        options=sorted(df['classe_age'].unique()),
        default=sorted(df['classe_age'].unique()),
        help="Sélectionner 1+ classes d'âge"
    )
    
    genres = st.multiselect(
        "👥 Genre",
        options=['Homme', 'Femme'],
        default=['Homme', 'Femme']
    )
    
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        exp_min = st.slider("Expérience Min (ans)", 0, 38, 0)
    with col_exp2:
        exp_max = st.slider("Expérience Max (ans)", 0, 38, 38)
    
    st.markdown("---")
    
    # Filtre saison
    saisons_selected = st.multiselect(
        "🌡️ Saisons",
        options=df['saison'].unique(),
        default=df['saison'].unique()
    )
    
    st.markdown("---")
    
    # Filtre type jour
    jours_selected = st.multiselect(
        "📅 Type Jour",
        options=['Jour Travail', 'Week-end'],
        default=['Jour Travail', 'Week-end']
    )
    
    st.markdown("---")
    
    # Filtre heure
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        heure_min = st.slider("Heure Min", 0, 23, 0)
    with col_h2:
        heure_max = st.slider("Heure Max", 0, 23, 23)
    
    st.markdown("---")
    
    # Filtre gravité
    gravite_selected = st.multiselect(
        "⚠️ Gravité",
        options=['Léger', 'Modéré', 'Grave', 'Mortel'],
        default=['Léger', 'Modéré', 'Grave', 'Mortel']
    )
    
    st.markdown("---")
    
    # Filtre facteurs de risque
    st.subheader("⚡ Facteurs de Risque")
    alcool_filter = st.checkbox("🍺 Avec Alcool", value=False)
    fatigue_filter = st.checkbox("😴 Avec Fatigue", value=False)
    
    st.markdown("---")
    
    # Filtre conditions
    meteo_selected = st.multiselect(
        "🌧️ Conditions Météo",
        options=df['conditions_meteo'].unique(),
        default=df['conditions_meteo'].unique()
    )
    
    luminosite_selected = st.multiselect(
        "💡 Luminosité",
        options=df['luminosite'].unique(),
        default=df['luminosite'].unique()
    )
    
    st.markdown("---")
    
    # Filtre route
    route_selected = st.multiselect(
        "🛣️ Type de Route",
        options=df['type_route'].unique(),
        default=df['type_route'].unique()
    )
    
    st.markdown("---")
    
    # Filtre vitesse
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        vitesse_min = st.slider("Vitesse Min (km/h)", int(df['vitesse'].min()), int(df['vitesse'].max()), int(df['vitesse'].min()))
    with col_v2:
        vitesse_max = st.slider("Vitesse Max (km/h)", int(df['vitesse'].min()), int(df['vitesse'].max()), int(df['vitesse'].max()))

# ============================================================================
# APPLIQUER TOUS LES FILTRES
# ============================================================================

df_filtered = df[
    (df['date'].dt.date >= min_date) & 
    (df['date'].dt.date <= max_date) &
    (df['classe_age'].isin(classes_age)) &
    (df['genre'].isin(genres)) &
    (df['experience'] >= exp_min) & 
    (df['experience'] <= exp_max) &
    (df['saison'].isin(saisons_selected)) &
    (df['type_jour'].isin(jours_selected)) &
    (df['heure'] >= heure_min) & 
    (df['heure'] <= heure_max) &
    (df['gravite_label'].isin(gravite_selected)) &
    (df['conditions_meteo'].isin(meteo_selected)) &
    (df['luminosite'].isin(luminosite_selected)) &
    (df['type_route'].isin(route_selected)) &
    (df['vitesse'] >= vitesse_min) & 
    (df['vitesse'] <= vitesse_max)
]

if alcool_filter:
    df_filtered = df_filtered[df_filtered['alcoolémie'] == True]

if fatigue_filter:
    df_filtered = df_filtered[df_filtered['fatigue'] == True]

# ============================================================================
# DASHBOARD PRINCIPAL
# ============================================================================

# KPIs dynamiques
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("📊 Accidents", f"{len(df_filtered):,}", delta=f"{(len(df_filtered)/len(df)*100):.1f}%")

with col2:
    victimes = df_filtered['nombre_victimes'].sum()
    st.metric("👥 Victimes", f"{victimes:,}", delta=f"{(victimes/df['nombre_victimes'].sum()*100):.1f}%")

with col3:
    graves = len(df_filtered[df_filtered['gravite'] >= 3])
    pct = (graves/len(df_filtered)*100) if len(df_filtered) > 0 else 0
    st.metric("⚠️ Graves+", f"{graves:,}", delta=f"{pct:.1f}%")

with col4:
    cout_moy = df_filtered['cout_assurance_annuel'].mean() if len(df_filtered) > 0 else 0
    st.metric("💰 Assurance Moy", f"{cout_moy:.0f}€/an", delta=f"{(cout_moy/df['cout_assurance_annuel'].mean()-1)*100:.1f}%")

with col5:
    age_moy = df_filtered['age'].mean() if len(df_filtered) > 0 else 0
    st.metric("👤 Âge Moyen", f"{age_moy:.0f} ans", delta=f"{(age_moy/df['age'].mean()-1)*100:.1f}%")

with col6:
    exp_moy = df_filtered['experience'].mean() if len(df_filtered) > 0 else 0
    st.metric("📅 Expérience Moy", f"{exp_moy:.1f} ans", delta=f"{(exp_moy/df['experience'].mean()-1)*100:.1f}%")

st.markdown("---")

# Tabs pour navigation
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📈 Tendances", "👤 Démographie", "💰 Assurance", "🔗 Causalité", "⚠️ Risque", "💡 Insights"])

# ============================================================================
# TAB 1: TENDANCES
# ============================================================================

with tab1:
    st.subheader("📈 Tendances Temporelles")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Accidents par Heure")
        acc_heure = df_filtered.groupby('heure').size()
        fig = px.bar(x=acc_heure.index, y=acc_heure.values,
                    color=acc_heure.values, color_continuous_scale='Reds',
                    title='Distribution horaire')
        fig.update_layout(xaxis_title="Heure", yaxis_title="Nombre", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Gravité par Heure")
        grave_heure = df_filtered.groupby('heure')['gravite'].mean()
        fig = px.line(x=grave_heure.index, y=grave_heure.values,
                     title='Gravité moyenne par heure', markers=True)
        fig.update_layout(xaxis_title="Heure", yaxis_title="Gravité", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribution par Jour Semaine")
        acc_jour = df_filtered['jour_semaine'].value_counts()
        ordre = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        acc_jour = acc_jour.reindex([j for j in ordre if j in acc_jour.index])
        fig = px.bar(x=acc_jour.index, y=acc_jour.values,
                    color=acc_jour.values, color_continuous_scale='Blues')
        fig.update_layout(xaxis_title="Jour", yaxis_title="Nombre", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Distribution par Saison")
        acc_saison = df_filtered['saison'].value_counts()
        fig = px.pie(values=acc_saison.values, names=acc_saison.index,
                    title='Répartition saisonnière')
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 2: DÉMOGRAPHIE
# ============================================================================

with tab2:
    st.subheader("👤 Analyse Démographique")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Accidents par Classe d'Âge")
        acc_age = df_filtered['classe_age'].value_counts().sort_index()
        gravite_age = df_filtered.groupby('classe_age')['gravite'].mean()
        
        fig = px.bar(
            x=acc_age.index, y=acc_age.values,
            color=gravite_age[acc_age.index].values,
            color_continuous_scale='RdYlGn_r',
            title='Accidents et gravité par classe d\'âge'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Accidents par Genre")
        acc_genre = df_filtered['genre'].value_counts()
        gravite_genre = df_filtered.groupby('genre')['gravite'].mean()
        
        fig = px.bar(
            x=acc_genre.index, y=acc_genre.values,
            color=gravite_genre[acc_genre.index].values,
            color_continuous_scale='RdYlGn_r',
            title='Distribution par genre'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Expérience du Conducteur")
        df_filtered['exp_cat'] = pd.cut(df_filtered['experience'], 
                                        bins=[0, 2, 5, 10, 40],
                                        labels=['<2 ans', '2-5 ans', '5-10 ans', '>10 ans'])
        acc_exp = df_filtered['exp_cat'].value_counts().sort_index()
        gravite_exp = df_filtered.groupby('exp_cat')['gravite'].mean()
        
        fig = px.bar(
            x=acc_exp.index, y=acc_exp.values,
            color=gravite_exp[acc_exp.index].values,
            color_continuous_scale='RdYlGn_r',
            title='Accidents par expérience'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Tableau Résumé Démographie")
        demo_table = df_filtered.groupby('classe_age').agg({
            'gravite': 'mean',
            'nombre_victimes': 'mean',
            'alcoolémie': lambda x: (x.sum()/len(x)*100) if len(x) > 0 else 0,
            'age': 'count'
        }).round(2)
        demo_table.columns = ['Gravité Moy', 'Victimes Moy', 'Alcool %', 'Nombre']
        st.dataframe(demo_table, use_container_width=True)

# ============================================================================
# TAB 3: ASSURANCE
# ============================================================================

with tab3:
    st.subheader("💰 Analyse Coûts Assurance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Coût Assurance par Classe d'Âge")
        cout_age = df_filtered.groupby('classe_age')['cout_assurance_annuel'].mean()
        fig = px.bar(
            x=cout_age.index, y=cout_age.values,
            color=cout_age.values,
            color_continuous_scale='Reds',
            title='Prime moyenne annuelle'
        )
        fig.update_layout(yaxis_title="Coût (€/an)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Coût par Genre")
        cout_genre = df_filtered.groupby('genre')['cout_assurance_annuel'].mean()
        fig = px.bar(
            x=cout_genre.index, y=cout_genre.values,
            color=cout_genre.values,
            color_continuous_scale='Reds',
            title='Prime moyenne par genre'
        )
        fig.update_layout(yaxis_title="Coût (€/an)")
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Coût par Expérience")
        cout_exp = df_filtered.groupby('exp_cat')['cout_assurance_annuel'].mean()
        fig = px.bar(
            x=cout_exp.index, y=cout_exp.values,
            color=cout_exp.values,
            color_continuous_scale='Reds',
            title='Prime par expérience'
        )
        fig.update_layout(yaxis_title="Coût (€/an)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Tableau Détaillé Assurance")
        assurance_table = df_filtered.groupby('classe_age').agg({
            'cout_assurance_annuel': ['mean', 'min', 'max', 'std'],
            'gravite': 'mean'
        }).round(0)
        st.dataframe(assurance_table, use_container_width=True)
    
    st.markdown("---")
    st.info("""
    **💡 Facteurs de Coût Assurance**:
    - **Âge**: Jeunes (18-24) x2.0 | Seniors (65+) x1.8
    - **Expérience**: Novice (<2ans) +50% | Expert (>10ans) -30%
    - **Historique**: Graves +30% | Modérés +10%
    - **Genre**: Hommes +15% (risque statistique)
    """)

# ============================================================================
# TAB 4: CAUSALITÉ
# ============================================================================

with tab4:
    st.subheader("🔗 Liens de Causalité")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Âge vs Gravité")
        df_filtered['age_cat'] = pd.cut(df_filtered['age'], 
                                        bins=[15, 25, 35, 45, 55, 65, 90],
                                        labels=['18-25', '25-35', '35-45', '45-55', '55-65', '65+'])
        causal_age = df_filtered.groupby(['age_cat', 'gravite_label']).size().reset_index(name='Nombre')
        fig = px.bar(causal_age, x='age_cat', y='Nombre', color='gravite_label',
                    barmode='group', title='Impact âge sur gravité')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Expérience vs Gravité")
        causal_exp = df_filtered.groupby(['exp_cat', 'gravite_label']).size().reset_index(name='Nombre')
        fig = px.bar(causal_exp, x='exp_cat', y='Nombre', color='gravite_label',
                    barmode='group', title='Impact expérience')
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Alcool vs Gravité")
        df_filtered['alcool_cat'] = df_filtered['alcoolémie'].map({True: 'Avec Alcool', False: 'Sans Alcool'})
        causal_alcool = df_filtered.groupby(['alcool_cat', 'gravite_label']).size().reset_index(name='Nombre')
        fig = px.bar(causal_alcool, x='alcool_cat', y='Nombre', color='gravite_label',
                    barmode='group', title='Impact alcool')
        st.plotly_chart(fig, use_container_width=True)
        
        if len(df_filtered) > 0:
            alcool_grave = df_filtered[df_filtered['alcoolémie']]['gravite'].mean()
            sans_alcool_grave = df_filtered[~df_filtered['alcoolémie']]['gravite'].mean()
            impact = (alcool_grave / sans_alcool_grave - 1) * 100 if sans_alcool_grave > 0 else 0
            st.success(f"**Interprétation**: Alcool augmente gravité de +{impact:.0f}%")
    
    with col2:
        st.subheader("Luminosité vs Gravité")
        causal_lumino = df_filtered.groupby(['luminosite', 'gravite_label']).size().reset_index(name='Nombre')
        fig = px.bar(causal_lumino, x='luminosite', y='Nombre', color='gravite_label',
                    barmode='group', title='Impact luminosité')
        st.plotly_chart(fig, use_container_width=True)
        
        if len(df_filtered) > 0:
            nuit_grave = df_filtered[df_filtered['luminosite'] == 'Nuit']['gravite'].mean()
            jour_grave = df_filtered[df_filtered['luminosite'] == 'Plein jour']['gravite'].mean()
            impact = (nuit_grave / jour_grave - 1) * 100 if jour_grave > 0 else 0
            st.success(f"**Interprétation**: Nuit augmente gravité de +{impact:.0f}%")

# ============================================================================
# TAB 5: FACTEURS RISQUE
# ============================================================================

with tab5:
    st.subheader("⚡ Analyse Facteurs de Risque")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Classe d'Âge + Genre")
        risk_age_genre = df_filtered.groupby(['classe_age', 'genre']).size().reset_index(name='Nombre')
        fig = px.bar(risk_age_genre, x='classe_age', y='Nombre', color='genre',
                    barmode='group', title='Distribution âge + genre')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Expérience + Alcool")
        risk_exp_alcool = df_filtered.groupby(['exp_cat', 'alcoolémie']).size().reset_index(name='Nombre')
        risk_exp_alcool['alcoolémie'] = risk_exp_alcool['alcoolémie'].map({True: 'Alcool', False: 'Non'})
        fig = px.bar(risk_exp_alcool, x='exp_cat', y='Nombre', color='alcoolémie',
                    barmode='group', title='Expérience + alcool')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("📊 Tableau Facteurs Risque")
    
    facteurs_df = pd.DataFrame({
        'Facteur': ['Alcool', 'Fatigue', 'Nuit', 'Mauvais Temps', 'Vitesse >80', 'Jeunes <25', 'Novices <2ans', 'Seniors >70'],
        'Nombre': [
            df_filtered['alcoolémie'].sum(),
            df_filtered['fatigue'].sum(),
            len(df_filtered[df_filtered['luminosite'] == 'Nuit']),
            len(df_filtered[df_filtered['conditions_meteo'] != 'Sec']),
            len(df_filtered[df_filtered['vitesse'] > 80]),
            len(df_filtered[df_filtered['classe_age'] == '18-24 (Jeunes)']),
            len(df_filtered[df_filtered['experience'] < 2]),
            len(df_filtered[df_filtered['classe_age'] == '65+ (Seniors)'])
        ]
    })
    
    if len(df_filtered) > 0:
        facteurs_df['% du Total'] = (facteurs_df['Nombre'] / len(df_filtered) * 100).round(1)
    
    st.dataframe(facteurs_df, use_container_width=True)

# ============================================================================
# TAB 6: INSIGHTS
# ============================================================================

with tab6:
    st.subheader("💡 Insights & Recommandations")
    
    if len(df_filtered) > 0:
        # Classe d'âge la plus accidentée
        classe_accidents = df_filtered['classe_age'].value_counts()
        classe_max = classe_accidents.idxmax()
        
        # Coût moyen
        cout_moyen = df_filtered['cout_assurance_annuel'].mean()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"""
            **👤 Classe d'Âge Critique: {classe_max}**
            
            {classe_accidents[classe_max]} accidents
            
            **Action**: Campagne sensibilisation ciblée
            """)
        
        with col2:
            st.warning(f"""
            **💰 Coût Assurance Moyen: {cout_moyen:.0f}€/an**
            
            Min: {df_filtered['cout_assurance_annuel'].min():.0f}€
            Max: {df_filtered['cout_assurance_annuel'].max():.0f}€
            
            **Surcoût sécurité**: +{((cout_moyen/df['cout_assurance_annuel'].mean()-1)*100):.0f}%
            """)
        
        with col3:
            age_moyen = df_filtered['age'].mean()
            st.info(f"""
            **👤 Âge Moyen: {age_moyen:.0f} ans**
            
            Expérience: {df_filtered['experience'].mean():.1f} ans
            
            **Profil**: {'Jeune conducteur' if age_moyen < 30 else 'Conducteur expérimenté' if age_moyen > 50 else 'Conducteur standard'}
            """)
        
        # Profil accident grave
        st.markdown("---")
        st.subheader("⚠️ Profil Type: Accident GRAVE")
        
        df_grave = df_filtered[df_filtered['gravite'] >= 3]
        
        if len(df_grave) > 0:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("👤 Âge Moyen", f"{df_grave['age'].mean():.0f} ans")
            with col2:
                st.metric("⚡ Expérience", f"{df_grave['experience'].mean():.1f} ans")
            with col3:
                st.metric("🍺 Alcool %", f"{(df_grave['alcoolémie'].sum()/len(df_grave)*100):.0f}%")
            with col4:
                st.metric("💰 Coût Ass.", f"{df_grave['cout_assurance_annuel'].mean():.0f}€")
            
            st.error(f"""
            **Profil Complet Accident Grave**:
            - Genre: {df_grave['genre'].mode()[0] if len(df_grave) > 0 else 'N/A'}
            - Classe d'âge: {df_grave['classe_age'].mode()[0] if len(df_grave) > 0 else 'N/A'}
            - Heure moyenne: {df_grave['heure'].mean():.0f}h
            - Vitesse moyenne: {df_grave['vitesse'].mean():.0f} km/h
            - Nuit: {(len(df_grave[df_grave['luminosite']=='Nuit'])/len(df_grave)*100):.0f}%
            - Mauvais temps: {(len(df_grave[df_grave['conditions_meteo']!='Sec'])/len(df_grave)*100):.0f}%
            - Victimes moyenne: {df_grave['nombre_victimes'].mean():.1f}
            """)
    else:
        st.warning("⚠️ Aucune donnée ne correspond à ces filtres")

st.markdown("---")
st.markdown("<div style='text-align: center;'><small>Dashboard Avancé | Démographie + Assurance | Phase 5 Production Ready</small></div>", 
           unsafe_allow_html=True)
