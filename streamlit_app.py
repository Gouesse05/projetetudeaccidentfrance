"""
Streamlit Dashboard - Accidents Routiers AVANCÉ
Filtres interactifs + Dashboard dynamique + Interprétations temps réel
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
    """Générer données réalistes avec patterns"""
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
    
    # Patterns réalistes
    for idx in df.index:
        heure = df.loc[idx, 'heure']
        saison = df.loc[idx, 'saison']
        jour = df.loc[idx, 'jour_semaine']
        
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
        
        # Week-end = plus d'alcool
        if jour in ['Saturday', 'Sunday']:
            alcool_prob = 0.25
            fatigue_prob = 0.05
        else:
            alcool_prob = 0.10
            fatigue_prob = 0.15
        
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
        
        # Données finales
        df.loc[idx, 'gravite'] = np.random.choice([1, 2, 3, 4], p=gravite_prob)
        df.loc[idx, 'nombre_victimes'] = max(1, int(np.random.poisson(victimes_base)))
        df.loc[idx, 'type_route'] = np.random.choice(['Autoroute', 'RN', 'Départementale', 'Route locale'])
        df.loc[idx, 'alcoolémie'] = np.random.random() < alcool_prob
        df.loc[idx, 'fatigue'] = np.random.random() < fatigue_prob
        df.loc[idx, 'vitesse'] = int(np.random.normal(75, 25))
    
    return df

# Charger données
df = generate_smart_accident_data()
gravite_map = {1: 'Léger', 2: 'Modéré', 3: 'Grave', 4: 'Mortel'}
df['gravite_label'] = df['gravite'].map(gravite_map)
df['type_jour'] = df['jour_semaine'].apply(lambda x: 'Week-end' if x in ['Saturday', 'Sunday'] else 'Jour Travail')

# ============================================================================
# LAYOUT PRINCIPAL
# ============================================================================

st.title("🚗 Dashboard Accidents - Filtres Avancés & Interactif")

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
    
    # Filtre saison
    saisons_selected = st.multiselect(
        "🌡️ Saisons",
        options=df['saison'].unique(),
        default=df['saison'].unique(),
        help="Sélectionner 1+ saisons pour filtrer"
    )
    
    st.markdown("---")
    
    # Filtre type jour
    jours_selected = st.multiselect(
        "📅 Type Jour",
        options=['Jour Travail', 'Week-end'],
        default=['Jour Travail', 'Week-end'],
        help="Jour travail vs Week-end"
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
col1, col2, col3, col4, col5 = st.columns(5)

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
    alcool = df_filtered['alcoolémie'].sum()
    pct_alcool = (alcool/len(df_filtered)*100) if len(df_filtered) > 0 else 0
    st.metric("🍺 Alcool", f"{alcool:,}", delta=f"{pct_alcool:.1f}%")

with col5:
    vitesse_moy = df_filtered['vitesse'].mean()
    st.metric("⚡ Vitesse Moy", f"{vitesse_moy:.0f} km/h", delta=f"{(vitesse_moy/df['vitesse'].mean()-1)*100:.1f}%")

st.markdown("---")

# Tabs pour navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Tendances", "🔗 Causalité", "📊 Comparaisons", "⚠️ Facteurs Risque", "💡 Insights"])

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
# TAB 2: CAUSALITÉ
# ============================================================================

with tab2:
    st.subheader("🔗 Liens de Causalité")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Alcool vs Gravité")
        df_filtered['alcool_cat'] = df_filtered['alcoolémie'].map({True: 'Avec Alcool', False: 'Sans Alcool'})
        causal_alcool = df_filtered.groupby(['alcool_cat', 'gravite_label']).size().reset_index(name='Nombre')
        fig = px.bar(causal_alcool, x='alcool_cat', y='Nombre', color='gravite_label',
                    barmode='group', title='Impact alcool sur gravité')
        st.plotly_chart(fig, use_container_width=True)
        
        # Interprétation
        if len(df_filtered) > 0:
            alcool_grave = df_filtered[df_filtered['alcoolémie']]['gravite'].mean()
            sans_alcool_grave = df_filtered[~df_filtered['alcoolémie']]['gravite'].mean()
            impact = (alcool_grave / sans_alcool_grave - 1) * 100 if sans_alcool_grave > 0 else 0
            st.success(f"**Interprétation**: Alcool augmente gravité de +{impact:.0f}% ⚠️")
    
    with col2:
        st.subheader("Luminosité vs Gravité")
        causal_lumino = df_filtered.groupby(['luminosite', 'gravite_label']).size().reset_index(name='Nombre')
        fig = px.bar(causal_lumino, x='luminosite', y='Nombre', color='gravite_label',
                    barmode='group', title='Impact luminosité')
        st.plotly_chart(fig, use_container_width=True)
        
        # Interprétation
        if len(df_filtered) > 0:
            nuit_grave = df_filtered[df_filtered['luminosite'] == 'Nuit']['gravite'].mean()
            jour_grave = df_filtered[df_filtered['luminosite'] == 'Plein jour']['gravite'].mean()
            impact = (nuit_grave / jour_grave - 1) * 100 if jour_grave > 0 else 0
            st.success(f"**Interprétation**: Nuit augmente gravité de +{impact:.0f}% (visibilité réduite)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Météo vs Gravité")
        causal_meteo = df_filtered.groupby(['conditions_meteo', 'gravite_label']).size().reset_index(name='Nombre')
        fig = px.bar(causal_meteo, x='conditions_meteo', y='Nombre', color='gravite_label',
                    barmode='group', title='Impact conditions météo')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Type Route vs Gravité")
        causal_route = df_filtered.groupby(['type_route', 'gravite_label']).size().reset_index(name='Nombre')
        fig = px.bar(causal_route, x='type_route', y='Nombre', color='gravite_label',
                    barmode='stack', title='Accidents par type de route')
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 3: COMPARAISONS
# ============================================================================

with tab3:
    st.subheader("📊 Comparaisons Détaillées")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Travail vs Week-end")
        comp_jour = df_filtered.groupby('type_jour').agg({
            'gravite': 'mean',
            'nombre_victimes': 'mean',
            'alcoolémie': lambda x: (x.sum()/len(x)*100),
            'fatigue': lambda x: (x.sum()/len(x)*100)
        }).round(2)
        st.dataframe(comp_jour, use_container_width=True)
    
    with col2:
        st.subheader("Par Saison")
        comp_saison = df_filtered.groupby('saison').agg({
            'gravite': 'mean',
            'nombre_victimes': 'mean',
            'alcoolémie': lambda x: (x.sum()/len(x)*100) if len(x) > 0 else 0,
        }).round(2)
        st.dataframe(comp_saison, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Par Luminosité")
        comp_lumino = df_filtered.groupby('luminosite').agg({
            'gravite': 'mean',
            'nombre_victimes': 'mean',
            'alcoolémie': lambda x: (x.sum()/len(x)*100) if len(x) > 0 else 0,
        }).round(2)
        st.dataframe(comp_lumino, use_container_width=True)
    
    with col2:
        st.subheader("Par Météo")
        comp_meteo = df_filtered.groupby('conditions_meteo').agg({
            'gravite': 'mean',
            'nombre_victimes': 'mean',
            'alcoolémie': lambda x: (x.sum()/len(x)*100) if len(x) > 0 else 0,
        }).round(2)
        st.dataframe(comp_meteo, use_container_width=True)

# ============================================================================
# TAB 4: FACTEURS RISQUE
# ============================================================================

with tab4:
    st.subheader("⚡ Analyse Facteurs de Risque")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Alcool vs Fatigue")
        risk_alcool_fatigue = df_filtered.groupby(['alcoolémie', 'fatigue']).size().reset_index(name='Nombre')
        risk_alcool_fatigue['alcoolémie'] = risk_alcool_fatigue['alcoolémie'].map({True: 'Alcool', False: 'Non'})
        risk_alcool_fatigue['fatigue'] = risk_alcool_fatigue['fatigue'].map({True: 'Fatigue', False: 'Non'})
        fig = px.bar(risk_alcool_fatigue, x='alcoolémie', y='Nombre', color='fatigue',
                    barmode='group', title='Combinaisons risque')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Vitesse vs Gravité")
        df_filtered['vitesse_cat'] = pd.cut(df_filtered['vitesse'], 
                                           bins=[0, 50, 80, 120, 200],
                                           labels=['<50', '50-80', '80-120', '>120'])
        risk_vitesse = df_filtered.groupby(['vitesse_cat', 'gravite_label']).size().reset_index(name='Nombre')
        fig = px.bar(risk_vitesse, x='vitesse_cat', y='Nombre', color='gravite_label',
                    barmode='stack', title='Vitesse vs Gravité')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("📈 Tableau Facteurs Risque")
    
    facteurs_df = pd.DataFrame({
        'Facteur': ['Alcool', 'Fatigue', 'Nuit', 'Mauvais Temps', 'Vitesse >80', 'Week-end'],
        'Nombre Accidents': [
            df_filtered['alcoolémie'].sum(),
            df_filtered['fatigue'].sum(),
            len(df_filtered[df_filtered['luminosite'] == 'Nuit']),
            len(df_filtered[df_filtered['conditions_meteo'] != 'Sec']),
            len(df_filtered[df_filtered['vitesse'] > 80]),
            len(df_filtered[df_filtered['type_jour'] == 'Week-end'])
        ]
    })
    
    if len(df_filtered) > 0:
        facteurs_df['% du Total'] = (facteurs_df['Nombre Accidents'] / len(df_filtered) * 100).round(1)
    
    st.dataframe(facteurs_df, use_container_width=True)

# ============================================================================
# TAB 5: INSIGHTS
# ============================================================================

with tab5:
    st.subheader("💡 Insights & Recommandations")
    
    if len(df_filtered) > 0:
        # Heure la plus dangereuse
        heure_gravite = df_filtered.groupby('heure')['gravite'].mean()
        heure_max = heure_gravite.idxmax()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **🕐 Heure Critique: {int(heure_max)}h-{int(heure_max)+1}h**
            
            Gravité moyenne: {heure_gravite[heure_max]:.2f}/4
            
            **Action**: Patrouilles renforcées, signalisation accrue
            """)
        
        # Saison la plus dangereuse
        saison_gravite = df_filtered.groupby('saison')['gravite'].mean()
        saison_max = saison_gravite.idxmax()
        
        with col2:
            st.info(f"""
            **🌡️ Saison Critique: {saison_max}**
            
            Gravité moyenne: {saison_gravite[saison_max]:.2f}/4
            
            **Action**: Campagnes sensibilisation saisonnière
            """)
        
        # Profil accident grave
        st.markdown("---")
        st.subheader("⚠️ Profil Type: Accident GRAVE")
        
        df_grave = df_filtered[df_filtered['gravite'] >= 3]
        
        if len(df_grave) > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("🍺 Alcool (%)", f"{(df_grave['alcoolémie'].sum()/len(df_grave)*100):.0f}%")
            with col2:
                st.metric("😴 Fatigue (%)", f"{(df_grave['fatigue'].sum()/len(df_grave)*100):.0f}%")
            with col3:
                st.metric("👥 Victimes Moy", f"{df_grave['nombre_victimes'].mean():.1f}")
            
            st.warning(f"""
            **Profil Complet**:
            - Heure moyenne: {df_grave['heure'].mean():.0f}h
            - Vitesse moyenne: {df_grave['vitesse'].mean():.0f} km/h
            - Nuit: {(len(df_grave[df_grave['luminosite']=='Nuit'])/len(df_grave)*100):.0f}%
            - Mauvais temps: {(len(df_grave[df_grave['conditions_meteo']!='Sec'])/len(df_grave)*100):.0f}%
            """)
    else:
        st.warning("⚠️ Aucune donnée ne correspond à ces filtres")

st.markdown("---")
st.markdown("<div style='text-align: center;'><small>Dashboard Avancé Interactif | Filtres Multiples | Phase 5 Production Ready</small></div>", 
           unsafe_allow_html=True)
