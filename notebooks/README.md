# Jupyter Notebooks - Data Science Examples

## Overview

This directory contains Jupyter Notebooks demonstrating how to use the Accidents database SDK for data analysis and machine learning.

## Notebooks

### 0. **Which Notebook Should I Use?**

| Scenario | Notebook |
|----------|----------|
| **I have direct DB access** | `01_Getting_Started.ipynb` |
| **I only have API access** (remote) | `03_API_Data_Access.ipynb` |
| **I want ML/Predictive models** | `02_Advanced_ML_Analysis.ipynb` |

---

### 1. `01_Getting_Started.ipynb` 
**For: Direct Database Access (Local Development)**

**When to use:** 
- You have PostgreSQL credentials
- Working locally with direct DB connection
- Need maximum performance for large queries

Topics covered:
- Connecting to the database using `DatabaseManager`
- Fetching data as Pandas DataFrames
- Basic exploratory data analysis (EDA)
- Correlation analysis
- Dimensionality reduction (PCA and Factor Analysis)
- K-Means clustering
- Creating interactive visualizations with Plotly
- Exporting results

**Key Functions:**
```python
from src.database.database_utils import DatabaseManager

db = DatabaseManager()

# Get data as DataFrames
df_accidents = db.query_accidents(annee=2022, limit=1000)
df_communes = db.get_stats_communes(limit=50)
df_danger = db.get_danger_scores(limit=30)
df_temporal = db.get_stats_temporelles(annee=2022)
```

### 3. `03_API_Data_Access.ipynb`
**For: REST API Access (Recommended for Most Users)**

**When to use:**
- Working remotely (no direct DB access)
- Data scientist without database credentials
- Production environment where API is the gateway
- Sharing notebooks with team (no sensitive DB creds)

Topics covered:
- Making HTTP requests to FastAPI
- Fetching data as Pandas DataFrames
- Working with API endpoints
- No database credentials needed
- EDA with API data
- Exporting results

**Key Functions:**
```python
import requests

API_BASE_URL = 'http://localhost:8000'
BASE_ENDPOINT = f'{API_BASE_URL}/api/v1'

# Get data via API
response = requests.get(f'{BASE_ENDPOINT}/accidents', 
                       params={'annee': 2022, 'limit': 1000})
df_accidents = pd.DataFrame(response.json())
df_danger = pd.DataFrame(requests.get(f'{BASE_ENDPOINT}/danger-scores').json())
```

**Advantages:**
✅ No database credentials exposed
✅ Works with remote servers  
✅ Built-in validation
✅ Easy to share
✅ Consistent data format

### 2. `02_Advanced_ML_Analysis.ipynb`
**For: Advanced machine learning and predictive modeling**

Topics covered:
- Feature engineering
- Predictive modeling (Random Forest, Gradient Boosting)
- Model evaluation and performance metrics
- Feature importance analysis
- Risk scoring by location
- Temporal pattern analysis
- Anomaly detection
- Key insights and recommendations

**Models Included:**
- Random Forest Classifier
- Feature importance extraction
- Anomaly detection with Elliptic Envelope
- Classification metrics (confusion matrix, ROC-AUC)

## Installation & Setup

### 1. Install Jupyter
```bash
pip install jupyter jupyterlab
```

### 2. Install required packages
```bash
pip install pandas numpy matplotlib seaborn scikit-learn plotly
```

### 3. Set up environment variables
Create a `.env` file in the project root:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=accidents_db
DB_USER=postgres
DB_PASSWORD=your_password
```

### 4. Start Jupyter
```bash
cd /path/to/projetetudeapi
jupyter lab
```

Then navigate to the notebooks directory and open a notebook.

## Available Data Methods

### Query Methods (return DataFrames)

```python
# Accidents with filters
db.query_accidents(annee=2022, mois=6, dep='75', gravite_min=2, limit=1000)

# Accidents by location
db.get_accidents_by_commune(code_com='75056', limit=100)
db.get_accidents_by_region('Ile-de-France', annee=2022)

# Statistical aggregates
db.get_stats_temporelles(annee=2022)  # By day/hour
db.get_stats_communes(limit=50)        # By commune
db.get_stats_departements(limit=50)    # By department

# Risk analysis
db.get_danger_scores(limit=50)         # Danger ranking
db.get_commune_danger_score('75056')   # Specific commune

# Demographics
db.get_stats_usagers(limit=50)         # By age/gender

# Custom SQL
df = db.query_to_dataframe(custom_sql_query)
```

## Data Structure

### Main Columns Available

**Temporal:**
- `date_accident`, `annee`, `mois`, `jour_semaine`, `heure`

**Location:**
- `code_com`, `id_com`, `code_dept`, `id_dept`, `region`

**Severity:**
- `gravite_max` (0=unrecorded, 1=uninjured, 2=minor, 3=serious, 4=fatal)
- `nombre_personnes`, `nombre_deces`

**Features:**
- `conditions_meteo`, `luminosite`, `type_route`, `alcoolémie`

**Additional:**
- `population`, `densite_hab_km2` (for communes)
- `score_danger`, `categorie_risque` (computed)

## Example Analysis Workflow

```python
# 1. Import and connect
from src.database.database_utils import DatabaseManager
db = DatabaseManager()

# 2. Fetch data
df = db.query_accidents(annee=2022, limit=5000)

# 3. EDA
df.describe()
df.groupby('jour_semaine')['gravite_max'].mean()

# 4. Feature engineering
df['is_fatal'] = (df['gravite_max'] == 4).astype(int)
df['is_night'] = ((df['heure'] >= 22) | (df['heure'] <= 5)).astype(int)

# 5. Model building
from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier()
clf.fit(df[features], df['is_fatal'])

# 6. Visualization
import plotly.express as px
px.bar(df.groupby('jour_semaine')['gravite_max'].mean())

# 7. Export
df.to_csv('analysis_results.csv', index=False)
```

## Tips for Data Scientists

1. **Performance:** Use `limit` parameter in queries to start small
2. **Missing Data:** Always check for NaN values with `.isnull().sum()`
3. **Categorical Variables:** Encode before modeling with `LabelEncoder` or `pd.get_dummies()`
4. **Scaling:** Use `StandardScaler` for distance-based algorithms
5. **Class Imbalance:** Fatal accidents (~0.5%) are rare, use stratified sampling
6. **Memory:** For large datasets, use chunking or aggregation functions

## Common Analyses

### Temporal Analysis
```python
df_temps = db.get_stats_temporelles()
df_temps.groupby('heure')['nombre_accidents'].plot()
```

### Geospatial Analysis
```python
df_communes = db.get_stats_communes(limit=100)
df_communes.plot.scatter(x='densite_hab_km2', y='nombre_accidents')
```

### Risk Modeling
```python
df_danger = db.get_danger_scores()
df_danger['risk_category'] = pd.cut(df_danger['score_danger'], 
                                    bins=[0, 30, 50, 100])
```

### Demographic Analysis
```python
df_users = db.get_stats_usagers()
df_users.groupby(['classe_age', 'genre'])['nombre'].sum()
```

## Troubleshooting

**Problem:** Database connection refused
- Check `.env` file with correct DB credentials
- Ensure PostgreSQL is running

**Problem:** Missing columns
- Check `db.query_accidents(limit=1)` to see available columns
- Use schema views like `v_accidents_enrichis`

**Problem:** Memory error
- Reduce `limit` parameter
- Use aggregation functions from DatabaseManager

**Problem:** Slow queries
- Use temporal/spatial filters to reduce data
- Avoid complex joins in custom SQL

## Contributing

Want to add more example analyses? 
- Create a new notebook following the naming convention `0X_Topic.ipynb`
- Add clear markdown headers
- Document custom functions
- Export key results as CSV

## Resources

- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Scikit-Learn Guide](https://scikit-learn.org/stable/user_guide.html)
- [Plotly Python](https://plotly.com/python/)
- [Jupyter Notebooks](https://jupyter.org/documentation)

---

**Last Updated:** January 2026  
**Version:** 1.0  
**Maintainer:** Data Science Team
