 # health_vitals
Health_vitals design for a healthcare project. It handles sensor data ingestion, user management, alert triggering, and role-based access control — built with **FastAPI** + **PostgreSQL**, containerized with Docker, and designed for integration with wearable devices and downstream ML prediction services.


# background
 This wearable-based platform for stress monitoring and prediction in patients with dementia or persistent physical symptoms.

The healthcare project has completed its initial research cycle, validating design requirements through prototype development and early-stage evaluation. This backend service supports the next phase of that work: reliable data ingestion from wearable sensors, structured storage, and delivery of stress-related health signals to clinical consumers.


## Tech Stack

**Backend**

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Auth | JWT (HS256) |
| Testing | pytest |
| Containerization | Docker + Docker Compose |
| CI | GitHub Actions |

**Frontend** *(planned — not yet implemented)*

| Layer | Technology |
|---|---|
| Framework | Next.js (React) |
| Styling | Tailwind CSS |
| State Management | Zustand |
| HTTP Client | Axios |

---

## System Architecture

The diagram below shows the full Sensors2Care platform architecture. The `health_vitals` service functions as the core backend, receiving data from sensors via the mobile app and EventHub, persisting recordings and alerts, and exposing APIs to the web dashboard and third-party consumers.

> ⚠️ Architecture diagram is a work in progress and will be updated as the project evolves.

![System Architecture](./docs/architecture/workflow.drawio.svg)

---


# file architecture

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
│   │   │   │       ├── sensor_recording.py   # sensor data API
│   │   │   │       ├── users.py    # users API
│   │   │   │       ├── alerts.py   # alert API
│   │   │   │       ├── device.py   # device API
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
│   ├── .env                        # env
│   ├── requirements.txt            # Python dependency
│   ├── dependencies.py             # dependency injection
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── pytest.ini
│   ├── .gitignore
│   └── README.md
├── consumer_delivery/
│   ├── main.py              #  FastAPI entry
│   ├── api/
│   │   └── v1/
│   │       └── stress.py    # consumer endpoint
│   ├── services/
│   │   └── delivery.py      # get data from backend, format data
│   ├── schemas/
│   │   └── output.py        # Consumer-facing's response schema (Decoupled from backend)
│   ├── core/
│   │   └── config.py
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── layout.jsx              # Root layout
│   │   ├── page.jsx                # Home / redirect to login
│   │   ├── login/
│   │   │   └── page.jsx
│   │   ├── dashboard/
│   │   │   └── page.jsx
│   │   ├── analytics/
│   │   │   └── page.jsx
│   │   └── settings/
│   │       └── page.jsx
│   ├── components/
│   │   ├── Dashboard.jsx
│   │   ├── DataTable.jsx
│   │   ├── ChartWidget.jsx
│   │   └── UserMenu.jsx
│   ├── hooks/
│   │   ├── useAuth.js
│   │   └── useHealthData.js
│   ├── services/
│   │   └── api.js
│   ├── store/
│   │   └── store.js
│   ├── styles/
│   │   └── globals.css
│   ├── public/
│   ├── .env.example
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── Dockerfile
│   └── README.md
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




# backend


## About

A backend REST API service for the Sensors2Care platform, handling sensor data ingestion, user management, alert triggering, and role-based access control.

Built with **FastAPI** + **PostgreSQL**, containerized with Docker, and designed for integration with wearable health monitoring devices.

---

# Consumer Delivery Layer

The Consumer Delivery Layer is a lightweight FastAPI service responsible for exposing processed health insights to end users. It sits at the outermost edge of the health vitals platform, consuming inference results produced by the backend pipeline and serving them through a clean, versioned REST API.

---

# frontend

A web dashboard  designed for clinician or caregiver to manage the health vitals of the patients, Which provides patient management, trends, and alert records.



## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)

### Run Locally

```bash
git clone https://github.com/your-username/health_vitals.git
cd health_vitals
docker-compose up --build
```

This will:
1. Start a PostgreSQL 16 database
2. Run Alembic migrations automatically
3. Launch the FastAPI app at **http://localhost:8000**

API docs available at: **http://localhost:8000/docs**

---

## API Examples

### 1. Login

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=admin@example.com&password=secret
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 2. Create a Sensor Recording

```http
POST /sensor-recordings/
Authorization: Bearer <token>
Content-Type: application/json

{
  "device_id": 1,
  "heart_rate": 95,
  "spo2": 97.5,
  "recorded_at": "2026-04-10T10:00:00"
}
```

---

### 3. Trigger an Alert (auto or manual)

```http
POST /alerts/
Authorization: Bearer <token>
Content-Type: application/json

{
  "patient_id": 3,
  "alert_type": "high_heart_rate",
  "severity": "warning",
  "message": "Heart rate exceeded threshold: 95 bpm"
}
```

---

## Role-Based Access Control

| Role | Permissions |
|---|---|
| `admin` | Full access |
| `doctor` | Read/write patient data and alerts |
| `patient` | Read own data only |

---





# API Document
