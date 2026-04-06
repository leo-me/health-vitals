## About this project





## file architecture

```
health-data-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # entry
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── api.py          # route summary
│   │   │   │   └── endpoints/  # handle http requests
│   │   │   │       ├── __init__.py
│   │   │   │       ├── health.py   # health data API
│   │   │   │       ├── users.py    # users API
│   │   │   │       ├── alerts.py   # alert API
│   │   │   │       └── analytics.py # analysis API
│   │   │   └── deps.py             # dependency injection
│   │   ├── crud/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # basic CRUD Generic approach
│   │   │   ├── crud_user.py
│   │   │   ├── crud_health_data.py
│   │   │   └── crud_alert.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # 
│   │   │   ├── user.py             # User ORM model
│   │   │   ├── health.py           # HealthData ORM model
│   │   │   └── alert.py            # Alert ORM model
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py             # User Pydantic model
│   │   │   ├── health.py           # HealthData Pydantic model
│   │   │   └── alert.py            # Alert Pydantic model
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── health_service.py   # health data processing logic
│   │   │   ├── alert_service.py    # alert rule logic
│   │   │   └── s3_service.py       # AWS S3 file upload
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py           # configuration management
│   │   │   ├── security.py         # JWT + password processing
│   │   │   ├── constants.py        # Constant
│   │   │   └── exceptions.py       # Custom Exception
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Base class
│   │   │   ├── session.py          # define database connection
│   │   │   └── init_db.py          # create table and insert initial data
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── logging.py          # log middleware
│   │   │   └── cors.py             # CORS configuration
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py           # log tools
│   │       └── validators.py       # data validation tools
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py             # Pytest configuration
│   │   ├── test_api.py.            # endpoint tests
│   │   └── test_services.py.       # service logic tests
│   ├── migrations/                 # Alembic database version control
│   │   ├── alembic.ini             # configuration
│   │   ├── env.py                  # connect to models
│   │   └── versions/
│   ├── .env.example                # env example
│   ├── requirements.txt            # Python dependency
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── pytest.ini
│   ├── .gitignore
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── DataTable.jsx
│   │   │   ├── ChartWidget.jsx
│   │   │   └── UserMenu.jsx
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── AnalyticsPage.jsx
│   │   │   └── SettingsPage.jsx
│   │   ├── hooks/
│   │   │   ├── useAuth.js
│   │   │   └── useHealthData.js
│   │   ├── services/
│   │   │   └── api.js              # Axios
│   │   ├── store/
│   │   │   └── store.js            # Zustand store
│   │   ├── styles/
│   │   │   └── tailwind.css
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── public/
│   ├── .env.example
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── Dockerfile
│   └── README.md
│
├── infra/
│   ├── docker-compose.yml          # local dev env
│   ├── docker-compose.prod.yml     # production env
│   ├── aws/
│   │   ├── terraform/              # IaC configuration
│   │   └── README.md
│   └── README.md
│
├── docs/
│   ├── ARCHITECTURE.md             # architecture design document
│   ├── API.md                      # API document
│   ├── DEPLOYMENT.md               # infrastructure guideline
│   ├── DATABASE.md                 # database design
│   └── CONTRIBUTING.md             # contribution guideline
│
├── .github/
│   └── workflows/
│       ├── backend-ci.yml          # backend CI/CD
│       └── frontend-ci.yml         # frontend CI/CD
│
├── .gitignore
├── README.md                       # Project Overview
└── LICENSE
```

