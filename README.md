# Sensors2Care

A wearable health data platform for stress monitoring and prediction in patients with dementia or persistent physical symptoms. The platform ingests sensor readings from wearable devices, stores and processes them, and delivers health insights to heterogeneous consumers — smartwatch, web dashboard, researcher tools, and ML pipelines — through a dedicated **Consumer Delivery Layer (CDL)**.

Sample data from [Campanella et al., 2024](https://data.mendeley.com/datasets/kb42z77m2g/2), licensed under CC BY 4.0.

---

## Architecture

```
Wearable / Mobile App
        │
        ▼
  ┌─────────────┐     ┌─────────────┐
  │   Backend   │────▶│   MLflow    │  model registry
  │  (FastAPI)  │     │  (sidecar)  │
  └─────┬───────┘     └─────────────┘
        │ shared PostgreSQL
        ▼
  ┌─────────────┐     ┌─────────────┐
  │     CDL     │────▶│    Redis    │  cache / broker
  │  (FastAPI)  │     └─────────────┘
  └─────┬───────┘
        │ Adapter pattern
   ┌────┴────────────────────┐
   ▼         ▼         ▼     ▼
 Watch   Dashboard  Researcher  ML Pipeline
```

| Service | Role |
|---|---|
| **Backend** | Core API. Handles sensor ingestion, user management, alerts, RBAC. Runs Alembic migrations on startup and loads registered ML models from MLflow at runtime. |
| **MLflow** | ML model registry (sidecar). Backend connects to it at `http://mlflow:5000`. Currently uses local file storage; see [cloud deployment guide](infra/docker-compose.prod.yml) to migrate to S3. |
| **CDL** | Consumer Delivery Layer. Formats and routes health insights to each consumer type via the Adapter pattern. Shares the PostgreSQL instance with the backend — depends on backend running migrations first. |
| **PostgreSQL** | Shared relational database. Schema managed by Alembic (backend-owned). |
| **Redis** | Cache and message broker used by the CDL. |
| **Frontend** | Next.js web dashboard for clinicians and caregivers. |

---

## Tech Stack

**Backend ｜ Consumer layer**

| Layer | Technology |
|---|---|
| Backend API | FastAPI |
| CDL | FastAPI + Adapter pattern |
| Frontend | Next.js (React), Tailwind CSS, Zustand |
| Database | PostgreSQL 16 + SQLAlchemy + Alembic |
| Cache / Broker | Redis 7 |
| ML Registry | MLflow |
| Auth | JWT (HS256) |
| Containerization | Docker + Docker Compose |
| CI | GitHub Actions |

**Frontend***

| Layer | Technology |
|---|---|
| Framework | Next.ts (React) |
| Styling | Tailwind CSS |
| State Management | Zustand |
| HTTP Client | Axios |

---

## Quick Start (local)

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose v2](https://docs.docker.com/compose/)
- Copy `.env.example` to `.env` and fill in the values (see below)

### Environment variables

Create `infra/.env`:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme
POSTGRES_DB=sensors2care
SECURITY_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CACHE_ENABLED=true
```

### Run

```bash
cd infra
docker compose up --build
```

Service startup order is enforced automatically:

1. PostgreSQL + Redis start first
2. MLflow starts
3. Backend starts — runs `alembic upgrade head`, then launches API
4. CDL starts — depends on backend having applied migrations
5. Frontend starts

| Service | Local URL |
|---|---|
| Backend API | http://localhost:8000 |
| Backend docs | http://localhost:8000/docs |
| CDL | http://localhost:8001 |
| MLflow UI | http://localhost:5004 |
| Frontend | http://localhost:3000 |

---

## Project Structure

```
health-vitals/
├── apps/
│   ├── backend/                    # Core FastAPI service
│   │   ├── app/
│   │   │   ├── api/v1/endpoints/   # sensor_recording, users, alerts, device, analytics
│   │   │   ├── crud/               # Generic CRUD base + domain CRUDs
│   │   │   ├── models/             # SQLAlchemy ORM models
│   │   │   ├── schemas/            # Pydantic schemas
│   │   │   ├── services/           # Business logic + S3 service
│   │   │   ├── core/               # Config, security, constants, exceptions
│   │   │   ├── db/                 # Session, base, init_db
│   │   │   └── middleware/         # Logging, CORS
│   │   ├── migrations/             # Alembic versions
│   │   └── Dockerfile
│   ├── consumer_delivery/          # CDL (Adapter pattern)
│   │   ├── api/v1/stress.py        # Consumer endpoints
│   │   ├── services/delivery.py    # Adapter dispatch
│   │   ├── schemas/output.py       # Consumer-facing schemas
│   │   └── Dockerfile
│   └── frontend/                   # Next.js dashboard
│       ├── app/                    # login, dashboard, analytics, settings
│       ├── components/
│       ├── hooks/
│       └── Dockerfile
├── infra/
│   ├── docker-compose.yml          # Local development
│   └── docker-compose.prod.yml     # Cloud deployment (S3 + managed DB)
├── experiments/                    # Research notebooks and results
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── DATABASE.md
└── .github/workflows/              # CI/CD
```

---

## API Examples

### Login

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=admin@example.com&password=secret
```

```json
{ "access_token": "eyJ...", "token_type": "bearer" }
```

### Submit a sensor recording

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

### Trigger an alert

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

## Cloud Deployment

See [`infra/docker-compose.prod.yml`](infra/docker-compose.prod.yml) for the production Compose file, which configures:

- MLflow backed by S3 (artifact store) and a managed PostgreSQL database (metadata store)
- Environment variables sourced from a secrets manager or `.env.prod`
- No bind-mounted local volumes

Key deployment rule: **backend must start and complete migrations before CDL starts.** The CDL has no migration runner of its own.

For full infrastructure guidance — prerequisite checklist, service startup order, MLflow local-vs-cloud differences, and known limitations — see the deployment document in [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

---

## License

Sample data: CC BY 4.0 ([Campanella et al., 2024](https://data.mendeley.com/datasets/kb42z77m2g/2))
