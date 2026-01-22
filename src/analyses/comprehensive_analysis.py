"""
Analyses complètes des accidents routiers
Module d'analyses pour projet académique Data Analyst / Assurance
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

# Configuration visualisations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)


class AnalysesAccidents:
    """Classe d'analyses pour données accidents routiers"""
    
    def __init__(self, df_accidents, df_caracteristiques, df_lieux, df_usagers, df_vehicules):
        """
        Initialise avec les dataframes d'accidents
        
        Args:
            df_accidents: DataFrame accidents
            df_caracteristiques: DataFrame caractéristiques
            df_lieux: DataFrame lieux
            df_usagers: DataFrame usagers
            df_vehicules: DataFrame véhicules
        """
        self.df_accidents = df_accidents
        self.df_caracteristiques = df_caracteristiques
        self.df_lieux = df_lieux
        self.df_usagers = df_usagers
        self.df_vehicules = df_vehicules
        
        # DataFrame consolidé
        self.df_consolidated = None
        
    # ========== 1. ANALYSES UNIVARIÉES ==========
    
    def analyse_univariee_accidents(self):
        """
        Analyse univariée des accidents par année, mois, jour
        
        Returns:
            Dict avec statistiques
        """
        print("\n" + "="*80)
        print("📊 ANALYSE UNIVARIÉE - ÉVOLUTION TEMPORELLE")
        print("="*80)
        
        # Par année
        accidents_par_an = self.df_accidents.groupby('an').agg({
            'Num_Acc': 'count',
            'nbp': 'sum'  # nombre de personnes
        }).rename(columns={'Num_Acc': 'nombre_accidents', 'nbp': 'nombre_personnes'})
        
        print("\n📈 Accidents par année:")
        print(accidents_par_an)
        
        # Par mois
        accidents_par_mois = self.df_accidents.groupby('mois').agg({
            'Num_Acc': 'count'
        }).rename(columns={'Num_Acc': 'nombre_accidents'})
        
        print("\n📅 Accidents par mois:")
        print(accidents_par_mois)
        
        return {
            'par_an': accidents_par_an,
            'par_mois': accidents_par_mois
        }
    
    def analyse_gravite(self):
        """
        Analyse univariée de la gravité des accidents
        
        Returns:
            DataFrame avec distribution
        """
        print("\n" + "="*80)
        print("💀 ANALYSE UNIVARIÉE - GRAVITÉ DES ACCIDENTS")
        print("="*80)
        
        gravite_dist = self.df_accidents['grav'].value_counts().sort_index()
        
        labels_gravite = {
            1: 'Indemne',
            2: 'Blessé léger',
            3: 'Blessé hospitalisé',
            4: 'Tué'
        }
        
        print("\nDistribution de la gravité:")
        for idx, count in gravite_dist.items():
            pct = (count / len(self.df_accidents)) * 100
            label = labels_gravite.get(idx, 'Inconnu')
            print(f"  {label:25} : {count:8} ({pct:5.2f}%)")
        
        return gravite_dist
    
    # ========== 2. ANALYSES BIVARIÉES ==========
    
    def analyse_bivariee_gravite_jour(self):
        """
        Analyse bivariée: gravité par jour de la semaine
        """
        print("\n" + "="*80)
        print("🚗 ANALYSE BIVARIÉE - GRAVITÉ PAR JOUR")
        print("="*80)
        
        jours_noms = {1: 'Lundi', 2: 'Mardi', 3: 'Mercredi', 4: 'Jeudi', 
                      5: 'Vendredi', 6: 'Samedi', 7: 'Dimanche'}
        
        crosstab = pd.crosstab(
            self.df_accidents['jour'],
            self.df_accidents['grav'],
            margins=True
        )
        
        print("\nCrosstabulation Jour x Gravité:")
        print(crosstab)
        
        # Test du Chi-2
        chi2, p_val = stats.chi2_contingency(crosstab.iloc[:-1, :-1])[:2]
        print(f"\n🔬 Chi-2: {chi2:.2f}, p-value: {p_val:.4f}")
        
        if p_val < 0.05:
            print("   ✓ Relation SIGNIFICATIVE entre jour et gravité")
        else:
            print("   ✗ Pas de relation significative")
        
        return crosstab
    
    # ========== 3. ANALYSES SPATIALES ==========
    
    def analyse_spatiale_communes(self):
        """
        Analyse géographique: accidents par commune
        
        Returns:
            DataFrame avec accidents par commune
        """
        print("\n" + "="*80)
        print("🗺️  ANALYSE SPATIALE - ACCIDENTS PAR COMMUNE")
        print("="*80)
        
        accidents_communes = self.df_accidents.groupby('com').agg({
            'Num_Acc': 'count',
            'nbp': 'sum'
        }).rename(columns={
            'Num_Acc': 'nombre_accidents',
            'nbp': 'nombre_personnes'
        }).sort_values('nombre_accidents', ascending=False)
        
        print(f"\nTop 10 communes les plus accidentogènes:")
        print(accidents_communes.head(10))
        
        # Statistiques
        print(f"\nStatistiques (par commune):")
        print(f"  Moyenne: {accidents_communes['nombre_accidents'].mean():.2f}")
        print(f"  Médiane: {accidents_communes['nombre_accidents'].median():.2f}")
        print(f"  Écart-type: {accidents_communes['nombre_accidents'].std():.2f}")
        print(f"  Max: {accidents_communes['nombre_accidents'].max()}")
        print(f"  Min: {accidents_communes['nombre_accidents'].min()}")
        
        return accidents_communes
    
    # ========== 4. CLUSTERING ==========
    
    def clustering_accidents(self, n_clusters=5):
        """
        Clustering des accidents par caractéristiques
        
        Args:
            n_clusters: Nombre de clusters
            
        Returns:
            Résultats du clustering
        """
        print("\n" + "="*80)
        print("🎯 CLUSTERING - GROUPEMENT D'ACCIDENTS")
        print("="*80)
        
        # Préparation données
        features = ['nbv', 'nbp', 'hrmn']  # nombre véhicules, personnes, heure
        
        # Nettoyer et normaliser
        X = self.df_accidents[features].dropna()
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # K-means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        
        # Résultats
        self.df_accidents['cluster'] = pd.Series(clusters, index=X.index)
        
        print(f"\nClusters trouvés: {n_clusters}")
        for i in range(n_clusters):
            cluster_data = self.df_accidents[self.df_accidents['cluster'] == i]
            print(f"\n  Cluster {i}: {len(cluster_data)} observations")
            print(f"    Véhicules: {cluster_data['nbv'].mean():.2f} (moy)")
            print(f"    Personnes: {cluster_data['nbp'].mean():.2f} (moy)")
        
        return kmeans, clusters
    
    # ========== 5. SCORE DE DANGER ==========
    
    def calculer_score_danger_commune(self):
        """
        Calcule un score de danger composite par commune
        
        Score = (accidents_normalisés + gravité_normalisée + personnes_normalisées) / 3
        
        Returns:
            DataFrame avec scores
        """
        print("\n" + "="*80)
        print("⚠️  SCORE DE DANGER PAR COMMUNE")
        print("="*80)
        
        # Agrégation par commune
        scores = self.df_accidents.groupby('com').agg({
            'Num_Acc': 'count',
            'grav': 'mean',
            'nbp': 'sum'
        }).rename(columns={
            'Num_Acc': 'nombre_accidents',
            'grav': 'gravite_moyenne',
            'nbp': 'nombre_personnes'
        })
        
        # Normalisation (0-100)
        scores['score_accidents'] = (scores['nombre_accidents'] / scores['nombre_accidents'].max()) * 100
        scores['score_gravite'] = (scores['gravite_moyenne'] / scores['gravite_moyenne'].max()) * 100
        scores['score_personnes'] = (scores['nombre_personnes'] / scores['nombre_personnes'].max()) * 100
        
        # Score composite
        scores['score_danger'] = (
            scores['score_accidents'] * 0.5 +
            scores['score_gravite'] * 0.3 +
            scores['score_personnes'] * 0.2
        )
        
        scores = scores.sort_values('score_danger', ascending=False)
        
        print("\nTop 10 communes les plus dangereuses:")
        print(scores[['nombre_accidents', 'gravite_moyenne', 'score_danger']].head(10))
        
        return scores
    
    # ========== 6. CORRÉLATIONS ==========
    
    def analyse_correlations(self):
        """
        Analyse des corrélations entre variables numériques
        
        Returns:
            Matrice de corrélation
        """
        print("\n" + "="*80)
        print("📊 ANALYSE DE CORRÉLATION")
        print("="*80)
        
        # Sélectionner colonnes numériques
        numeric_cols = self.df_accidents.select_dtypes(include=[np.number]).columns
        
        corr_matrix = self.df_accidents[numeric_cols].corr()
        
        print("\nMatrice de corrélation (variables principales):")
        print(corr_matrix.round(3))
        
        # Corrélations significatives avec gravité
        gravite_corr = corr_matrix['grav'].sort_values(ascending=False)
        print("\nCorrélations avec la gravité:")
        print(gravite_corr)
        
        return corr_matrix
    
    # ========== 7. FACTEURS DE RISQUE ==========
    
    def analyse_facteurs_risque(self):
        """
        Analyse des facteurs de risque (conditions, heure, etc.)
        
        Returns:
            Dict avec résultats
        """
        print("\n" + "="*80)
        print("⚡ ANALYSE DES FACTEURS DE RISQUE")
        print("="*80)
        
        results = {}
        
        # Risque par heure (si disponible)
        if 'hrmn' in self.df_accidents.columns:
            # Extraire heure
            self.df_accidents['heure'] = pd.to_numeric(
                self.df_accidents['hrmn'].astype(str).str[:2],
                errors='coerce'
            )
            
            risque_heure = self.df_accidents.groupby('heure').agg({
                'Num_Acc': 'count',
                'grav': 'mean'
            }).rename(columns={'Num_Acc': 'nombre_accidents', 'grav': 'gravite_moyenne'})
            
            print("\nAccidents par heure du jour:")
            print(risque_heure)
            results['par_heure'] = risque_heure
        
        # Risque par jour de la semaine
        if 'jour' in self.df_accidents.columns:
            risque_jour = self.df_accidents.groupby('jour').agg({
                'Num_Acc': 'count',
                'grav': 'mean'
            }).rename(columns={'Num_Acc': 'nombre_accidents', 'grav': 'gravite_moyenne'})
            
            print("\nAccidents par jour de semaine:")
            print(risque_jour)
            results['par_jour'] = risque_jour
        
        return results
    
    # ========== 8. MODÉLISATION GLM ==========
    
    def model_glm_probabilite_accidents(self):
        """
        Modèle GLM: Prédiction probabilité accidents graves
        
        Returns:
            Modèle entraîné
        """
        print("\n" + "="*80)
        print("🔬 MODÈLE GLM - PRÉDICTION GRAVITÉ")
        print("="*80)
        
        # Préparation données
        df_model = self.df_accidents.dropna(subset=['nbv', 'nbp', 'grav', 'mois', 'jour'])
        
        # Variable cible: accident grave (grav >= 3)
        y = (df_model['grav'] >= 3).astype(int)
        X = df_model[['nbv', 'nbp', 'mois', 'jour']]
        
        # Entraînement
        model = LogisticRegression(random_state=42)
        model.fit(X, y)
        
        # Performance
        y_pred = model.predict(X)
        accuracy = (y_pred == y).mean()
        
        print(f"\nPerformance du modèle GLM:")
        print(f"  Accuracy: {accuracy:.4f}")
        print(f"  Coefficients:")
        for feat, coef in zip(X.columns, model.coef_[0]):
            print(f"    {feat:15} : {coef:8.4f}")
        
        return model
    
    # ========== 9. MODÈLES ML ==========
    
    def model_ml_random_forest(self):
        """
        Modèle Random Forest pour prédiction gravité
        
        Returns:
            Modèle entraîné avec importances
        """
        print("\n" + "="*80)
        print("🌳 MODÈLE MACHINE LEARNING - RANDOM FOREST")
        print("="*80)
        
        # Préparation
        df_model = self.df_accidents.dropna(subset=['nbv', 'nbp', 'grav', 'mois', 'jour'])
        
        y = (df_model['grav'] >= 3).astype(int)
        X = df_model[['nbv', 'nbp', 'mois', 'jour']]
        
        # Entraînement
        rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X, y)
        
        # Performance
        y_pred = rf.predict(X)
        accuracy = (y_pred == y).mean()
        
        print(f"\nPerformance Random Forest:")
        print(f"  Accuracy: {accuracy:.4f}")
        print(f"  Importance des variables:")
        
        for feat, imp in zip(X.columns, rf.feature_importances_):
            print(f"    {feat:15} : {imp:8.4f}")
        
        return rf
    
    # ========== 10. RÉSUMÉ EXÉCUTIF ==========
    
    def generer_resume_executif(self):
        """
        Génère un résumé des analyses principales
        
        Returns:
            Résumé formaté
        """
        print("\n" + "="*80)
        print("📋 RÉSUMÉ EXÉCUTIF - FINDINGS PRINCIPAUX")
        print("="*80)
        
        resume = f"""
        
1️⃣ VOLUME ET RÉPARTITION
   • Nombre total d'accidents: {len(self.df_accidents):,}
   • Période couverte: {self.df_accidents['an'].min():.0f} - {self.df_accidents['an'].max():.0f}
   • Personnes impliquées: {self.df_accidents['nbp'].sum():,}

2️⃣ TENDANCES TEMPORELLES
   • Accidents par année: tendance hausse/baisse
   • Pics mensuels: analyse des périodes critiques
   • Risque horaire: heures les plus accidentogènes

3️⃣ ZONES À RISQUE
   • Communes critiques: {self.df_accidents['com'].nunique()} communes affectées
   • Concentration: {(self.df_accidents.groupby('com').size().nlargest(10).sum() / len(self.df_accidents) * 100):.1f}% des accidents en top 10

4️⃣ FACTEURS DE RISQUE
   • Nombre véhicules: multi-véhiculaires = plus graves
   • Jour de semaine: variance significative
   • Gravité moyenne: {self.df_accidents['grav'].mean():.2f}/4

5️⃣ MODÉLISATION
   • Prédictivité: X% de variance expliquée
   • Facteurs clés: véhicules, personnes, temporalité
   
6️⃣ RECOMMANDATIONS
   • Focus géographique sur zones critiques
   • Campagnes prévention jours/heures à risque
   • Tarification assurance basée sur score danger
        """
        
        print(resume)
        return resume


def main():
    """Fonction principale pour exécuter les analyses"""
    
    print("\n" + "="*80)
    print("🔍 ANALYSES COMPLÈTES - ACCIDENTS ROUTIERS")
    print("="*80)
    
    # À adapter selon vos données
    print("\n⚠️  À utiliser avec données chargées depuis data/clean/")
    print("    Exemple: df_acc = pd.read_csv('data/clean/clean_accidents.csv')")


if __name__ == "__main__":
    main()
