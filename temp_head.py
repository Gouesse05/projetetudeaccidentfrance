"""
Streamlit Dashboard - Accidents Routiers AVANCÉ
Filtres interactifs + Démographie + Données assurance
UX/UI Amélioré avec CSS Custom
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
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS STYLING
# ============================================================================

CUSTOM_CSS = """
<style>
    /* Variables couleurs */
    :root {
        --primary-color: #FF6B6B;
        --secondary-color: #4ECDC4;
        --accent-color: #FFE66D;
        --dark-bg: #1A1A2E;
        --light-bg: #F7F9FB;
        --text-primary: #2C3E50;
        --text-secondary: #95A5A6;
        --border-color: #E0E0E0;
        --success: #2ECC71;
        --warning: #F39C12;
        --danger: #E74C3C;
    }

    /* GÉNÉRAL */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body, .main {
        background: linear-gradient(135deg, #F7F9FB 0%, #E8EEF5 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: var(--text-primary);
    }

    /* HEADER PRINCIPAL */
    .main-header {
        background: linear-gradient(135deg, #FF6B6B 0%, #E74C3C 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(255, 107, 107, 0.2);
        text-align: center;
    }

    .main-header h1 {
        font-size: 2.5em;
        font-weight: 700;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    }

    .main-header p {
        font-size: 1.1em;
        opacity: 0.95;
        font-weight: 300;
    }

    /* SIDEBAR STYLING - MINIMAL */
    [data-testid="stSidebar"] {
        padding: 20px;
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: inherit;
    }

    [data-testid="stSidebar"] .stSelectbox, 
    [data-testid="stSidebar"] .stMultiSelect,
    [data-testid="stSidebar"] .stSlider {
        margin-bottom: 20px;
    }
    
    [data-testid="stSidebar"] label {
        color: inherit !important;
        font-weight: normal !important;
        font-size: inherit !important;
    }
    
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] select,
    [data-testid="stSidebar"] textarea {
        color: inherit !important;
        background-color: inherit !important;
        border: inherit !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        transition: all 0.3s ease;
    }

    /* CARDS & CONTAINERS */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border-left: 5px solid var(--primary-color);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }

    .metric-card.success {
        border-left-color: var(--success);
    }

    .metric-card.warning {
        border-left-color: var(--warning);
    }

    .metric-card.danger {
        border-left-color: var(--danger);
    }

    /* TABS STYLING */
    [data-testid="stTabs"] [aria-selected="true"] {
        background-color: var(--primary-color);
        color: white;
        border-radius: 10px 10px 0 0;
    }

    [data-testid="stTabs"] [aria-selected="false"] {
        background-color: #ECF0F1;
        color: var(--text-primary);
    }

    /* BUTTONS */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, #E74C3C 100%);
        color: white;
        border: none;
        padding: 12px 25px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
    }

    /* INPUT FIELDS */
    .stSelectbox, .stMultiSelect, .stSlider, .stNumberInput {
        background: white;
        border-radius: 8px;
        border: 2px solid var(--border-color);
        transition: border-color 0.3s ease;
    }

    .stSelectbox:focus-within, 
    .stMultiSelect:focus-within,
    .stSlider:focus-within {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(255, 107, 107, 0.1);
    }

    /* METRICS */
    [data-testid="stMetricDelta"] {
        color: var(--success);
        font-weight: 600;
    }

    .stMetric {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        border-top: 4px solid var(--primary-color);
        transition: all 0.3s ease;
    }

    .stMetric:hover {
        transform: translateY(-4px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
    }

    /* SUCCESS/WARNING/ERROR BOXES */
    [data-testid="stSuccess"], [data-testid="stInfo"], 
    [data-testid="stWarning"], [data-testid="stError"] {
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid;
        margin: 15px 0;
    }

    [data-testid="stSuccess"] {
        background-color: #D5F4E6;
        border-left-color: var(--success);
        color: #27AE60;
    }

    [data-testid="stWarning"] {
        background-color: #FCF3E0;
        border-left-color: var(--warning);
        color: #D68910;
    }

    [data-testid="stError"] {
        background-color: #FADBD8;
        border-left-color: var(--danger);
        color: #C0392B;
    }

    [data-testid="stInfo"] {
        background-color: #D6EAF8;
        border-left-color: var(--secondary-color);
        color: #1F618D;
    }

    /* DIVIDER */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--primary-color), transparent);
        margin: 25px 0;
    }

    /* HEADINGS */
    h1, h2, h3 {
        color: var(--text-primary);
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    h1 {
        font-size: 2.2em;
        border-bottom: 3px solid var(--primary-color);
        padding-bottom: 10px;
    }

    h2 {
        font-size: 1.8em;
    }

    h3 {
        font-size: 1.4em;
    }

    /* SMALL TEXT & FOOTER */
    small {
        color: var(--text-secondary);
        font-size: 0.9em;
    }

    .footer-text {
        text-align: center;
        color: var(--text-secondary);
        margin-top: 40px;
        padding-top: 20px;
        border-top: 2px solid var(--border-color);
        font-size: 0.95em;
    }

    /* DATAFRAME STYLING */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }

    /* CHARTS CONTAINER */
    .plotly-container {
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        padding: 15px;
        background: white;
    }

    /* RESPONSIF */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.8em;
        }

        h1 {
            font-size: 1.6em;
        }

        h2 {
            font-size: 1.3em;
        }
    }

    /* SCROLL BAR */
    ::-webkit-scrollbar {
        width: 10px;
    }

    ::-webkit-scrollbar-track {
        background: var(--light-bg);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--primary-color);
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #E74C3C;
    }
</style>
"""

# Injecter le CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

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

