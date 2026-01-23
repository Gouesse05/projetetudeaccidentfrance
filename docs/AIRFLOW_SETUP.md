# 🚀 Guide Installation Airflow

## Installation Airflow dans le venv

### 1️⃣ Installation des dépendances

```bash
# Activer le venv
source venv/bin/activate

# Installer Airflow (peut prendre quelques minutes)
pip install -r requirements.txt

# Ou installation minimale
pip install apache-airflow==2.7.3 apache-airflow-providers-postgres==5.10.0
```

### 2️⃣ Initialiser Airflow

```bash
# Définir le répertoire Airflow
export AIRFLOW_HOME=/home/sdd/projetetudeapi/airflow_home

# Initialiser la base de données
airflow db init

# Créer un utilisateur admin
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@accidents.local \
  --password password123
```

### 3️⃣ Démarrer Airflow

```bash
# Terminal 1: WebServer (interface web)
airflow webserver --port 8080

# Terminal 2 (nouveau): Scheduler (planificateur)
airflow scheduler
```

### 4️⃣ Accéder à l'interface

Ouvre dans ton navigateur: **http://localhost:8080**

- **Identifiant**: admin
- **Mot de passe**: password123

---

## 📋 Utilisation des DAGs

### Lister les DAGs

```bash
airflow dags list
```

**Résultat attendu:**
```
dag_id                  | filepath
accidents_etl_pipeline  | /dags/accidents_pipeline.py
accidents_maintenance   | /dags/maintenance.py
```

### Tester une DAG

```bash
# Test sans exécuter les dépendances
airflow dags test accidents_etl_pipeline 2024-01-01

# Test d'une tâche spécifique
airflow tasks test accidents_etl_pipeline download_data 2024-01-01
```

### Exécuter une DAG manuellement

```bash
# Déclencher une exécution manuelle
airflow dags trigger -e 2024-01-01 accidents_etl_pipeline

# Vérifier le statut
airflow dags list-runs --dag-id accidents_etl_pipeline
```

### Monitorer l'exécution

Via l'interface web:
1. Aller à: **Dags → accidents_etl_pipeline**
2. Cliquer sur **Graph View** pour voir les tâches
3. Cliquer sur une tâche pour voir les logs

---

## 🔄 DAGs Disponibles

### 1. `accidents_etl_pipeline`

**Orchestration du pipeline ETL complet**

```
Début
  ↓
Vérifier répertoires
  ↓
Télécharger données (data.gouv.fr)
  ↓
Nettoyer données
  ↓
Charger PostgreSQL
  ↓
Valider données
  ↓
Nettoyer fichiers temp
  ↓
Fin
```

**Planification**: Lundi 3h du matin

**Commandes utiles**:
```bash
# Voir la structure de la DAG
airflow dags show accidents_etl_pipeline

# Lancer immédiatement
airflow dags trigger -e 2024-01-01 accidents_etl_pipeline

# Voir les exécutions passées
airflow dags list-runs --dag-id accidents_etl_pipeline
```

### 2. `accidents_maintenance`

**Maintenance et monitoring du système**

```
Début
  ↓
Vérification santé BD
Vérification espace disque
  ↓
Backup base de données
  ↓
Nettoyage anciens backups
  ↓
Générer rapport
  ↓
Fin
```

**Planification**: Chaque jour à 1h du matin

**Fichiers créés**:
- Backups: `/home/sdd/projetetudeapi/backups/accidents_db_*.sql`
- Rapport: `/tmp/maintenance_report.txt`

---

## 🐛 Troubleshooting

### Erreur: "Airflow Home is not defined"

```bash
export AIRFLOW_HOME=/home/sdd/projetetudeapi/airflow_home
```

### Erreur: "No module named 'src'"

```bash
# Vérifier que tu es dans le bon répertoire
cd /home/sdd/projetetudeapi

# Ajouter au PYTHONPATH
export PYTHONPATH=/home/sdd/projetetudeapi:$PYTHONPATH
```

### Erreur de connexion PostgreSQL

```bash
# Vérifier la config dans src/config.py
# S'assurer que PostgreSQL tourne
pg_isready -h localhost -p 5432

# Tester la connexion
psql -h localhost -U postgres -d accidents
```

### Réinitialiser Airflow

```bash
# ⚠️ Attention: Supprime tout l'historique!
rm -rf airflow_home/
export AIRFLOW_HOME=/home/sdd/projetetudeapi/airflow_home
airflow db init
```

---

## 📊 Monitoring Avancé

### Logs détaillés

```bash
# Logs d'une DAG spécifique
tail -f airflow_home/logs/accidents_etl_pipeline/

# Logs d'une tâche
tail -f airflow_home/logs/accidents_etl_pipeline/download_data/
```

### Métriques Airflow

Via le webUI: **Admin → Logs** ou **Admin → Metrics**

### Configuration PostgreSQL pour Airflow

Airflow utilise une BD pour stocker l'état des DAGs (défaut: SQLite)

Pour utiliser PostgreSQL comme métabase Airflow:

```bash
# Installer le provider
pip install apache-airflow-providers-postgres

# Configurer dans airflow.cfg
sql_alchemy_conn = postgresql+psycopg2://user:password@localhost:5432/airflow
```

---

## 🚀 Déploiement Production

### Sur Render

```bash
# Procfile (ajouter les deux processus)
webserver: airflow webserver --port $PORT
scheduler: airflow scheduler
```

### Variables d'environnement Airflow

```bash
# .env ou variables Render
AIRFLOW_HOME=/app/airflow_home
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql://...
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__DAGS_FOLDER=/app/dags
AIRFLOW__CORE__LOAD_DEFAULT_CONNECTIONS=False
```

---

## ✅ Checklist

- [ ] Airflow installé: `pip install apache-airflow`
- [ ] Environnement: `export AIRFLOW_HOME=...`
- [ ] BD initialisée: `airflow db init`
- [ ] Admin créé: `airflow users create --username admin ...`
- [ ] Webserver démarré: `airflow webserver --port 8080`
- [ ] Scheduler démarré: `airflow scheduler`
- [ ] DAGs visibles: `http://localhost:8080`
- [ ] DAG accidents_etl_pipeline testée
- [ ] DAG accidents_maintenance testée

---

## 📚 Ressources

- [Airflow Docs](https://airflow.apache.org/)
- [Airflow Providers](https://registry.astronomer.io/)
- [Airflow CLI](https://airflow.apache.org/docs/apache-airflow/stable/cli-and-env-variables-ref.html)

---

**Prêt à orchestrer ton pipeline! 🚀**
