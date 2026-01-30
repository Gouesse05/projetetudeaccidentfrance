# Jupyter Notebook - API Data Access

## Overview

This directory contains a Jupyter Notebook for accessing the Accidents database through the REST API.

**For alternative access methods:**
- Raw SQL queries: See `../queries/` directory  
- Direct PostgreSQL Python module: See `../sql_queries.py`

---

## Notebook

### `03_API_Data_Access.ipynb`

**REST API-based Data Access (Recommended)**

**When to use:**
- Working remotely (no direct DB access)
- Data scientist without database credentials
- Production environment where API is the gateway
- Sharing notebooks with team (no sensitive DB credentials)
- You want analytics without SQL knowledge

**Topics covered:**
- Making HTTP requests to FastAPI
- Fetching data as Pandas DataFrames
- Working with API endpoints
- No database credentials needed
- Exploratory Data Analysis (EDA)
- PCA, Factor Analysis, K-Means clustering
- Interactive visualizations with Plotly
- Exporting results

**Key Code Example:**
```python
import requests
import pandas as pd

API_BASE_URL = 'http://localhost:8000'
BASE_ENDPOINT = f'{API_BASE_URL}/api/v1'

def api_request(endpoint: str, params: Dict = None):
    response = requests.get(f'{BASE_ENDPOINT}{endpoint}', params=params)
    return response.json()

# Usage example
data = api_request('/accidents', params={'annee': 2022, 'limit': 1000})
df = pd.DataFrame(data)

# Danger scores
danger_data = api_request('/danger-scores')
df_danger = pd.DataFrame(danger_data)
```

**Advantages:**
✅ No database credentials exposed  
✅ Works with remote servers  
✅ Built-in data validation  
✅ Easy to share with team members  
✅ Consistent data format  
✅ Microservices-aligned architecture  

---

## Installation & Setup

### 1. Install Jupyter

```bash
pip install jupyter jupyterlab
```

### 2. Install required Python packages

```bash
pip install requests pandas numpy matplotlib seaborn scikit-learn plotly
```

### 3. Start Jupyter

```bash
cd /path/to/projetetudeapi
jupyter lab
```

Then open `notebooks/03_API_Data_Access.ipynb`

---

## Available API Endpoints

The notebook uses these endpoints from the FastAPI server:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Check API status |
| `/api/v1/accidents` | GET | Get accident records |
| `/api/v1/danger-scores` | GET | Get danger ranking by commune |
| `/api/v1/stats/communes` | GET | Statistics by commune |
| `/api/v1/stats/usagers` | GET | Demographics analysis |
| `/api/v1/stats/departements` | GET | Statistics by department |
| `/api/v1/heatmap` | GET | Geospatial data |

### Example API Calls

```python
# Check server status
response = requests.get('http://localhost:8000/health')

# Get accidents for 2022
response = requests.get('http://localhost:8000/api/v1/accidents', 
                       params={'annee': 2022, 'limit': 1000})

# Get danger scores
response = requests.get('http://localhost:8000/api/v1/danger-scores',
                       params={'limit': 50})

# Get commune stats
response = requests.get('http://localhost:8000/api/v1/stats/communes')
```

---

## Running the API Server

The notebook expects the FastAPI server to be running:

```bash
# From project root
python main.py

# Or using uvicorn directly
uvicorn main:app --host localhost --port 8000
```

---

## Common Workflow

1. **Start the API server** in one terminal
2. **Launch Jupyter Lab** in another terminal
3. **Open the notebook** and run cells sequentially
4. **Analyze data** using Pandas, NumPy, Scikit-learn
5. **Visualize results** with Plotly and Matplotlib
6. **Export findings** as CSV or JSON

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| ConnectionRefusedError | Ensure FastAPI server is running on localhost:8000 |
| ModuleNotFoundError | Install missing packages with `pip install` |
| Empty DataFrames | Check API response status and query parameters |
| Slow queries | Reduce limit parameter or add filters |

---

**Last Updated:** January 2026  
**Python Version:** 3.12+  
**Tested with:** FastAPI 0.104.1, Pandas 1.5.3, Plotly 5.18.0

