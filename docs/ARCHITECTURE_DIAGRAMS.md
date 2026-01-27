# Architecture du Projet - Diagrammes

## Architecture Globale

```mermaid
graph TB
    subgraph "Sources de Données"
        A[data.gouv.fr<br/>CSV Files] --> B[Pipeline ETL]
    end
    
    subgraph "Pipeline ETL"
        B --> C[Download<br/>download_data.py]
        C --> D[Clean<br/>clean_data.py]
        D --> E[Load<br/>load_postgresql.py]
    end
    
    subgraph "Stockage"
        E --> F[(PostgreSQL<br/>8 tables)]
        F --> G[accidents]
        F --> H[usagers]
        F --> I[vehicules]
        F --> J[lieux]
    end
    
    subgraph "Couche Analyse"
        F --> K[Statistical Analysis]
        F --> L[Machine Learning]
        F --> M[Dimensionality Reduction]
        F --> N[Data Cleaning]
    end
    
    subgraph "API REST"
        K --> O[FastAPI<br/>25+ endpoints]
        L --> O
        M --> O
        N --> O
    end
    
    subgraph "Clients"
        O --> P[Swagger UI]
        O --> Q[Streamlit Dashboard]
        O --> R[Jupyter Notebooks]
        O --> S[HTTP Clients]
    end
    
    style A fill:#e1f5ff
    style F fill:#ffe1e1
    style O fill:#e1ffe1
    style P fill:#fff4e1
    style Q fill:#fff4e1
    style S fill:#fff4e1
```

## Pipeline ETL - Flux de Données

```mermaid
graph TD
    A[data.gouv.fr] -->|CSV 2016-2024| B[download_data.py]
    B -->|Verify checksums| C[data/raw/]
    
    C -->|Load CSV| D[clean_data.py]
    D -->|Remove missing values| E[Handle data types]
    E -->|Validate integrity| F[data/clean/]
    
    F -->|Read cleaned data| G[load_postgresql.py]
    G -->|CREATE SCHEMA| H[(PostgreSQL)]
    G -->|CREATE TABLES| H
    G -->|CREATE INDEXES| H
    G -->|BULK INSERT batches| H
    G -->|CREATE VIEWS| H
    G -->|ANALYZE| H
    
    H -->|8 tables| I[accidents]
    H -->|8 tables| J[usagers]
    H -->|8 tables| K[vehicules]
    H -->|8 tables| L[lieux]
    
    style A fill:#e1f5ff
    style C fill:#fff4e1
    style F fill:#ffe1e1
    style H fill:#ffe1e1
```

## Architecture API

```mermaid
graph LR
    subgraph "Client Layer"
        A[HTTP Client]
        B[Browser]
        C[Streamlit]
        D[Jupyter]
    end
    
    subgraph "FastAPI Application"
        E[main.py<br/>Configuration]
        F[routes.py<br/>25+ endpoints]
        G[models.py<br/>Pydantic schemas]
        H[analysis_endpoints.py<br/>Advanced analysis]
    end
    
    subgraph "Business Logic"
        I[statistical_analysis.py]
        J[machine_learning.py]
        K[data_cleaning.py]
        L[dimensionality_reduction.py]
    end
    
    subgraph "Data Access"
        M[database_utils.py<br/>Connection pool]
        N[(PostgreSQL)]
    end
    
    A --> E
    B --> E
    C --> E
    D --> E
    
    E --> F
    E --> H
    F --> G
    H --> G
    
    F --> I
    F --> J
    H --> K
    H --> L
    
    I --> M
    J --> M
    K --> M
    L --> M
    
    M --> N
    
    style E fill:#e1ffe1
    style N fill:#ffe1e1
```

## Schéma de Base de Données

```mermaid
erDiagram
    ACCIDENTS ||--o{ USAGERS : contains
    ACCIDENTS ||--o{ VEHICULES : involves
    ACCIDENTS ||--o| LIEUX : occurs_at
    VEHICULES ||--o{ USAGERS : transports
    
    ACCIDENTS {
        string Num_Acc PK
        int an
        int mois
        int jour
        string hrmn
        int lum
        int dep
        int com
        string adr
        float lat
        float long
    }
    
    USAGERS {
        string Num_Acc FK
        int num_veh
        int place
        int catu
        int grav
        int sexe
        int an_nais
        int trajet
        int secu
    }
    
    VEHICULES {
        string Num_Acc FK
        int num_veh
        int catv
        int occutc
        int obs
        int obsm
        int choc
        int manv
    }
    
    LIEUX {
        string Num_Acc FK
        int catr
        int voie
        string v1
        string v2
        int circ
        int nbv
        int pr
        int pr1
        int vosp
        int prof
        int plan
        int surf
        int infra
        int situ
    }
    
    CARACTERISTIQUES {
        string Num_Acc PK
        int an
        int mois
        int jour
        string hrmn
        int lum
        int dep
        int com
        int agg
        int int
        int atm
        int col
        string adr
        float lat
        float long
    }
```

## Flux d'Analyse ML

```mermaid
flowchart TD
    A[Raw Data] --> B{Data Quality Check}
    B -->|OK| C[Feature Engineering]
    B -->|Issues| D[Data Cleaning]
    D --> C
    
    C --> E[Train/Test Split<br/>80/20]
    
    E --> F[Training Set]
    E --> G[Test Set]
    
    F --> H[Random Forest<br/>Classifier]
    
    H --> I[Feature Importance<br/>Analysis]
    H --> J[Model Evaluation]
    
    G --> J
    
    J --> K{Accuracy > 78%?}
    K -->|Yes| L[Model Deployment<br/>Save with joblib]
    K -->|No| M[Hyperparameter<br/>Tuning]
    M --> H
    
    L --> N[Predictions<br/>API endpoint]
    
    style A fill:#e1f5ff
    style L fill:#e1ffe1
    style N fill:#fff4e1
```

## Workflow des Notebooks

```mermaid
graph TD
    A[Start Analysis] --> B[01_data_exploration.ipynb]
    
    B --> C[Load Data via API]
    B --> D[Descriptive Statistics]
    B --> E[Missing Values Analysis]
    B --> F[Distribution Plots]
    B --> G[Correlation Matrix]
    
    G --> H[02_statistical_analysis.ipynb]
    
    H --> I[Chi-Square Tests]
    H --> J[ANOVA]
    H --> K[Pearson Correlations]
    H --> L[Temporal Analysis]
    
    L --> M[03_ml_modeling.ipynb]
    
    M --> N[Data Preparation]
    M --> O[Random Forest Training]
    M --> P[Feature Importance]
    M --> Q[Confusion Matrix]
    M --> R[Model Persistence]
    
    R --> S[04_visualizations.ipynb]
    
    S --> T[Geographic Maps]
    S --> U[Time Series]
    S --> V[Heatmaps]
    S --> W[3D Scatter Plots]
    S --> X[Interactive Dashboards]
    
    style B fill:#e1f5ff
    style H fill:#ffe1e1
    style M fill:#e1ffe1
    style S fill:#fff4e1
```

## Déploiement Render.com

```mermaid
graph TB
    A[GitHub Repo<br/>main branch] -->|Push| B[GitHub Actions<br/>CI/CD]
    
    B --> C{Tests Pass?}
    C -->|No| D[Notify Failure]
    C -->|Yes| E[Render Webhook]
    
    E --> F[Render Build]
    
    F --> G[Install Dependencies<br/>pip install -r requirements.txt]
    G --> H[Build Docker Image]
    H --> I[Deploy Container]
    
    subgraph "Render Services"
        I --> J[Web Service<br/>FastAPI]
        I --> K[PostgreSQL<br/>Database]
    end
    
    K -->|Connection Pool| J
    
    J --> L[Health Checks<br/>/health endpoint]
    
    L -->|OK| M[Production<br/>accidents-api-prod.onrender.com]
    L -->|Fail| N[Auto Restart]
    
    N --> I
    
    style A fill:#e1f5ff
    style M fill:#e1ffe1
    style K fill:#ffe1e1
```

## Architecture Sécurité (Future)

```mermaid
graph LR
    subgraph "Client"
        A[User/App]
    end
    
    subgraph "API Gateway"
        B[Rate Limiting<br/>100 req/min]
        C[Authentication<br/>JWT Token]
        D[Authorization<br/>Role-based]
    end
    
    subgraph "FastAPI"
        E[Protected Endpoints]
        F[Public Endpoints]
    end
    
    subgraph "Database"
        G[(PostgreSQL<br/>Encrypted)]
    end
    
    A -->|Request + Token| B
    B --> C
    C -->|Valid| D
    C -->|Invalid| H[401 Unauthorized]
    D -->|Authorized| E
    D -->|Public| F
    
    E --> G
    F --> G
    
    style C fill:#ffe1e1
    style D fill:#ffe1e1
    style G fill:#ffe1e1
```

## Monitoring & Logging (Future)

```mermaid
graph TD
    A[FastAPI App] --> B[Logging<br/>loguru]
    A --> C[Metrics<br/>Prometheus]
    A --> D[Tracing<br/>OpenTelemetry]
    
    B --> E[Log Aggregation<br/>Loki/CloudWatch]
    C --> F[Metrics Dashboard<br/>Grafana]
    D --> G[Distributed Tracing<br/>Jaeger]
    
    E --> H[Alerting<br/>PagerDuty]
    F --> H
    G --> H
    
    H --> I[Dev Team<br/>Slack/Email]
    
    style A fill:#e1ffe1
    style H fill:#ffe1e1
```
