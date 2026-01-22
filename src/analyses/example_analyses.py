"""
Script d'exemple: Analyses des accidents routiers
À exécuter après avoir chargé les données nettoyées
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from datetime import datetime

# Configuration
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

# ============================================================================
# 1. CHARGEMENT DES DONNÉES
# ============================================================================

print("\n" + "="*80)
print("📊 ANALYSES ACCIDENTS ROUTIERS - EXEMPLE")
print("="*80)

# À adapter à vos chemins
DATA_DIR = "../../data/clean/"

print("\n1️⃣  Chargement des données...")

try:
    df_accidents = pd.read_csv(f"{DATA_DIR}clean_accidents.csv")
    df_caracteristiques = pd.read_csv(f"{DATA_DIR}clean_caracteristiques.csv")
    df_lieux = pd.read_csv(f"{DATA_DIR}clean_lieux.csv")
    df_usagers = pd.read_csv(f"{DATA_DIR}clean_usagers.csv")
    df_vehicules = pd.read_csv(f"{DATA_DIR}clean_vehicules.csv")
    
    print(f"  ✓ accidents: {len(df_accidents)} lignes")
    print(f"  ✓ caracteristiques: {len(df_caracteristiques)} lignes")
    print(f"  ✓ lieux: {len(df_lieux)} lignes")
    print(f"  ✓ usagers: {len(df_usagers)} lignes")
    print(f"  ✓ vehicules: {len(df_vehicules)} lignes")
    
except FileNotFoundError:
    print("  ✗ Erreur: fichiers non trouvés")
    print("  Exécutez d'abord: python src/pipeline/run_pipeline.py")
    exit(1)

# ============================================================================
# 2. EXPLORATION INITIALE
# ============================================================================

print("\n2️⃣  Exploration initiale...")

print("\nStructure df_accidents:")
print(df_accidents.info())

print("\nStatistiques descriptives:")
print(df_accidents.describe())

print(f"\nValeurs manquantes:")
print(df_accidents.isnull().sum())

# ============================================================================
# 3. ANALYSE UNIVARIÉE
# ============================================================================

print("\n" + "="*80)
print("📈 ANALYSE UNIVARIÉE")
print("="*80)

# Evolution temporelle
print("\n3a) Accidents par année:")
accidents_par_an = df_accidents.groupby('an').agg({
    'Num_Acc': 'count',
    'nbp': 'sum'
}).rename(columns={'Num_Acc': 'nombre', 'nbp': 'personnes'})
print(accidents_par_an)

# Visualisation
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

accidents_par_an['nombre'].plot(ax=ax1, kind='bar', color='steelblue')
ax1.set_title('Évolution du nombre d\'accidents par année', fontsize=12, fontweight='bold')
ax1.set_xlabel('Année')
ax1.set_ylabel('Nombre d\'accidents')
ax1.grid(True, alpha=0.3)

accidents_par_an['personnes'].plot(ax=ax2, kind='line', marker='o', color='darkred', linewidth=2)
ax2.set_title('Personnes impliquées par année', fontsize=12, fontweight='bold')
ax2.set_xlabel('Année')
ax2.set_ylabel('Nombre de personnes')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('accidents_par_annee.png', dpi=300, bbox_inches='tight')
plt.show()

# Distribution gravité
print("\n3b) Distribution de la gravité:")
gravite_dist = df_accidents['grav'].value_counts().sort_index()

labels_gravite = {
    1: 'Indemne',
    2: 'Blessé léger',
    3: 'Blessé hospitalisé',
    4: 'Tué'
}

for idx, count in gravite_dist.items():
    pct = (count / len(df_accidents)) * 100
    label = labels_gravite.get(idx, f'Code {idx}')
    print(f"  {label:25} : {count:8} ({pct:5.2f}%)")

# Visualisation
fig, ax = plt.subplots(figsize=(10, 6))
colors = ['green', 'orange', 'red', 'darkred']
gravite_dist.plot(kind='bar', ax=ax, color=colors[:len(gravite_dist)])
ax.set_title('Distribution de la gravité des accidents', fontsize=12, fontweight='bold')
ax.set_xlabel('Niveau de gravité')
ax.set_ylabel('Nombre d\'accidents')
ax.set_xticklabels([labels_gravite.get(i, f'Code {i}') for i in gravite_dist.index], rotation=45)
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('gravite_distribution.png', dpi=300, bbox_inches='tight')
plt.show()

# ============================================================================
# 4. ANALYSE BIVARIÉE
# ============================================================================

print("\n" + "="*80)
print("🔄 ANALYSE BIVARIÉE")
print("="*80)

# Gravité par jour
print("\n4a) Gravité par jour de la semaine:")
jours_noms = {1: 'Lundi', 2: 'Mardi', 3: 'Mercredi', 4: 'Jeudi',
              5: 'Vendredi', 6: 'Samedi', 7: 'Dimanche'}

crosstab = pd.crosstab(
    df_accidents['jour'],
    df_accidents['grav'],
    margins=True
)
print(crosstab)

# Test Chi-2
chi2, p_val, _, _ = stats.chi2_contingency(crosstab.iloc[:-1, :-1])
print(f"\n🔬 Chi-2: {chi2:.2f}, p-value: {p_val:.4f}")
if p_val < 0.05:
    print("   → Relation SIGNIFICATIVE entre jour et gravité")
else:
    print("   → Pas de relation significative")

# Visualisation
fig, ax = plt.subplots(figsize=(12, 6))
crosstab.iloc[:-1, :-1].plot(kind='bar', ax=ax, width=0.8)
ax.set_title('Distribution de la gravité par jour de la semaine', fontsize=12, fontweight='bold')
ax.set_xlabel('Jour de la semaine')
ax.set_ylabel('Nombre d\'accidents')
ax.set_xticklabels([jours_noms.get(i+1, f'Jour {i}') for i in range(7)], rotation=45)
ax.legend(title='Gravité', labels=[labels_gravite.get(i, f'Code {i}') for i in range(1, 5)])
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('gravite_par_jour.png', dpi=300, bbox_inches='tight')
plt.show()

# ============================================================================
# 5. ANALYSE SPATIALE
# ============================================================================

print("\n" + "="*80)
print("🗺️  ANALYSE SPATIALE")
print("="*80)

print("\n5a) Top 10 communes les plus accidentogènes:")
accidents_communes = df_accidents.groupby('com').agg({
    'Num_Acc': 'count',
    'nbp': 'sum'
}).rename(columns={'Num_Acc': 'nombre', 'nbp': 'personnes'}).sort_values('nombre', ascending=False)

print(accidents_communes.head(10))

# Visualisation
fig, ax = plt.subplots(figsize=(12, 6))
top10 = accidents_communes.head(10)
top10['nombre'].plot(kind='barh', ax=ax, color='steelblue')
ax.set_title('Top 10 communes les plus accidentogènes', fontsize=12, fontweight='bold')
ax.set_xlabel('Nombre d\'accidents')
ax.invert_yaxis()
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig('top10_communes.png', dpi=300, bbox_inches='tight')
plt.show()

# ============================================================================
# 6. ANALYSE DES CORRÉLATIONS
# ============================================================================

print("\n" + "="*80)
print("📊 ANALYSE DE CORRÉLATION")
print("="*80)

numeric_cols = df_accidents.select_dtypes(include=[np.number]).columns
corr_matrix = df_accidents[numeric_cols].corr()

print("\nMatrice de corrélation:")
print(corr_matrix.round(3))

# Heatmap
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=ax, cbar_kws={'label': 'Corrélation'})
ax.set_title('Matrice de corrélation - Variables accidents', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('correlation_matrix.png', dpi=300, bbox_inches='tight')
plt.show()

# ============================================================================
# 7. SCORE DE DANGER PAR COMMUNE
# ============================================================================

print("\n" + "="*80)
print("⚠️  SCORE DE DANGER")
print("="*80)

# Calcul
scores = df_accidents.groupby('com').agg({
    'Num_Acc': 'count',
    'grav': 'mean',
    'nbp': 'sum'
}).rename(columns={
    'Num_Acc': 'nombre_accidents',
    'grav': 'gravite_moyenne',
    'nbp': 'nombre_personnes'
})

# Normalisation
scores['score_accidents'] = (scores['nombre_accidents'] / scores['nombre_accidents'].max()) * 100
scores['score_gravite'] = (scores['gravite_moyenne'] / scores['gravite_moyenne'].max()) * 100
scores['score_personnes'] = (scores['nombre_personnes'] / scores['nombre_personnes'].max()) * 100

# Score composite (50% accidents, 30% gravité, 20% personnes)
scores['score_danger'] = (
    scores['score_accidents'] * 0.5 +
    scores['score_gravite'] * 0.3 +
    scores['score_personnes'] * 0.2
)

scores = scores.sort_values('score_danger', ascending=False)

print("\n🔴 Top 15 communes les plus dangereuses:")
print(scores[['nombre_accidents', 'gravite_moyenne', 'score_danger']].head(15))

# Visualisation
fig, ax = plt.subplots(figsize=(12, 8))
top15_communes = scores.head(15)
ax.barh(range(len(top15_communes)), top15_communes['score_danger'], color='darkred', alpha=0.7)
ax.set_yticks(range(len(top15_communes)))
ax.set_yticklabels(top15_communes.index)
ax.set_xlabel('Score de danger (0-100)')
ax.set_title('Top 15 communes par score de danger', fontsize=12, fontweight='bold')
ax.invert_yaxis()
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig('score_danger_top15.png', dpi=300, bbox_inches='tight')
plt.show()

# ============================================================================
# 8. RÉSUMÉ
# ============================================================================

print("\n" + "="*80)
print("📋 RÉSUMÉ EXECUTIF")
print("="*80)

resume = f"""

📊 VOLUME ET COUVERTURE
   • Total accidents: {len(df_accidents):,}
   • Période: {int(df_accidents['an'].min())}-{int(df_accidents['an'].max())}
   • Personnes impliquées: {int(df_accidents['nbp'].sum()):,}
   • Communes affectées: {df_accidents['com'].nunique():,}

💀 GRAVITÉ
   • Gravité moyenne: {df_accidents['grav'].mean():.2f}/4
   • % accidents graves (grav≥3): {((df_accidents['grav']>=3).sum() / len(df_accidents) * 100):.1f}%

🗺️  GÉOGRAPHIE
   • Top 10 communes: {(df_accidents.groupby('com').size().nlargest(10).sum() / len(df_accidents) * 100):.1f}% des accidents
   • Concentration: données concentrées ou dispersées?

📈 TENDANCES
   • Évolution annuelle: analyse tendance
   • Pics mensuels/hebdomadaires: variations saisonnières?

⚠️  FACTEURS DE RISQUE
   • Jour de semaine: différences significatives
   • Nombre véhicules: impact sur gravité?
   • Nombre personnes: corrélation avec accidents?

🎯 RECOMMANDATIONS
   • Géographique: focus zones rouge (score > 70)
   • Temporelle: campagnes prévention jours/heures critiques
   • Tarification: surprimes communes dangereuses
"""

print(resume)

print("\n" + "="*80)
print("✅ Analyses complétées!")
print("="*80)
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
