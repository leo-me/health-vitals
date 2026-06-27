#  — Deployment Guide

This directory contains the Compose files for running health-vitals locally and in a cloud environment.

| File | Purpose |
|---|---|
| `docker-compose.yml` | Local development — uses local file storage for MLflow, builds images from source |
| `docker-compose.prod.yml` | Cloud deployment — uses S3 for MLflow artifacts, pulls pre-built images |

---

## How dependencies are installed

Dependency installation is handled inside each service's **Dockerfile**, not in the Compose files. Compose only orchestrates which containers run and in what order.

| Service | Dependency file | Install command (inside Dockerfile) |
|---|---|---|
| Backend | `apps/backend/requirements.txt` | `pip install -r requirements.txt` |
| CDL | `apps/consumer_delivery/requirements.txt` | `pip install -r requirements.txt` |
| Frontend | `apps/frontend/package.json` | `npm ci` |

**Local (`docker-compose.yml`)** — each app service has a `build:` block pointing to its directory. When you run `docker compose up --build`, Docker builds the image from the Dockerfile, which installs all dependencies. You never need to run `pip install` or `npm install` manually.

**Cloud (`docker-compose.prod.yml`)** — there is no `build:` block. The services pull pre-built images (`${BACKEND_IMAGE}` etc.) that already have dependencies baked in from an earlier CI build step. See [Building images](#step-3----build-and-push-images).

---

## Local Development

```bash
# 1. Create your env file
cp .env.example .env   # then fill in the values

# 2. Start all services (builds images and installs dependencies automatically)
docker compose up --build

# 3. Tear down (preserves the database volume)
docker compose down

# 4. Tear down and wipe all data
docker compose down -v
```

Services will be available at:

| Service | URL |
|---|---|
| Backend API | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8000/docs |
| CDL | http://localhost:8001 |
| MLflow UI | http://localhost:5004 |
| Frontend | http://localhost:3000 |

---

## Cloud Deployment

### Prerequisites

- Docker and Docker Compose v2 on the target host
- A managed PostgreSQL 16 instance (AWS RDS, GCP Cloud SQL, etc.)
- An S3 bucket (or S3-compatible store) for MLflow artifact storage
- Pre-built container images pushed to a registry (see [Building images](#building-images))

### Step 1 — Configure secrets and application config

Before starting any service, separate your configuration into two categories:

| Category | What goes here | How to store it |
|---|---|---|
| **Secrets** | Passwords, API keys, JWT secret | Kubernetes Secret / AWS Secrets Manager |
| **Config** | Non-sensitive settings (region, DB name, cache flags) | Kubernetes ConfigMap / AWS Parameter Store |

#### Option A — Kubernetes (recommended for cloud)

Create a Secret for sensitive values:

```bash
kubectl create secret generic health-vitals-secrets \
  --from-literal=POSTGRES_PASSWORD=<strong-password> \
  --from-literal=SECURITY_KEY=<random-256-bit-secret> \
  --from-literal=AWS_ACCESS_KEY_ID=<your-access-key> \
  --from-literal=AWS_SECRET_ACCESS_KEY=<your-secret-key>
```

Create a ConfigMap for non-sensitive settings:

```bash
kubectl create configmap health-vitals-config \
  --from-literal=POSTGRES_USER=health-vitals \
  --from-literal=POSTGRES_DB=health-vitals \
  --from-literal=ALGORITHM=HS256 \
  --from-literal=ACCESS_TOKEN_EXPIRE_MINUTES=60 \
  --from-literal=AWS_REGION=ap-southeast-2 \
  --from-literal=MLFLOW_S3_BUCKET=your-bucket-name \
  --from-literal=CACHE_ENABLED=true
```

Reference them in your pod spec via `envFrom`:

```yaml
envFrom:
  - secretRef:
      name: health-vitals-secrets
  - configMapRef:
      name: health-vitals-config
```

#### Option B — Docker Compose on a single VM (simple / prototype)

If you are running Docker Compose directly on a cloud VM rather than Kubernetes, create a local `.env.prod` file instead:

```env
# Secrets
POSTGRES_PASSWORD=<strong-password>
SECURITY_KEY=<random-256-bit-secret>
AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-key>

# Config
POSTGRES_USER=health-vitals
POSTGRES_DB=health-vitals
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
AWS_REGION=ap-southeast-2
MLFLOW_S3_BUCKET=your-bucket-name
CACHE_ENABLED=true

# Image tags
BACKEND_IMAGE=ghcr.io/your-org/health-vitals-backend:latest
CDL_IMAGE=ghcr.io/your-org/health-vitals-cdl:latest
FRONTEND_IMAGE=ghcr.io/your-org/health-vitals-frontend:latest
```

> `.env.prod` must never be committed to source control — add it to `.gitignore`. For anything beyond a prototype, prefer Option A or use a dedicated secrets manager (AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault) to avoid storing credentials in plaintext files on disk.

### Step 2 — Provision the S3 bucket

```bash
aws s3 mb s3://your-bucket-name --region ap-southeast-2
```

Grant the IAM user or role associated with `AWS_ACCESS_KEY_ID` these permissions on the bucket:
`s3:GetObject`, `s3:PutObject`, `s3:ListBucket`, `s3:DeleteObject`.

### Step 3 — Build and push images

```bash
# From the repository root
docker build -t ghcr.io/your-org/health-vitals-backend:latest apps/backend
docker build -t ghcr.io/your-org/health-vitals-cdl:latest     apps/consumer_delivery
docker build -t ghcr.io/your-org/health-vitals-frontend:latest apps/frontend

docker push ghcr.io/your-org/health-vitals-backend:latest
docker push ghcr.io/your-org/health-vitals-cdl:latest
docker push ghcr.io/your-org/health-vitals-frontend:latest
```

### Step 4 — Deploy

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

Compose enforces the correct startup order automatically via healthchecks:

```
PostgreSQL ──┐
             ├──▶ MLflow ──▶ Backend (runs migrations) ──▶ CDL ──▶ Frontend
Redis ───────┘
```

The CDL has no migration runner — it depends on the backend completing `alembic upgrade head` first. This dependency is declared in the Compose file and is enforced at startup.

### Step 5 — Verify

```bash
# Check all containers are running
docker compose -f docker-compose.prod.yml ps

# Backend health
curl http://localhost:8000/health

# CDL health
curl http://localhost:8001/health

# MLflow health
curl http://localhost:5004/health

# Confirm database tables were created
docker compose -f docker-compose.prod.yml exec backend \
  python -c "from app.db.session import engine; print(engine.table_names())"

# Check that MLflow is writing artifacts to S3 (after registering a model)
aws s3 ls s3://your-bucket-name/mlflow-artifacts/ --recursive
```

### Updating a service

```bash
# Pull the new image and recreate only that container
docker compose -f docker-compose.prod.yml --env-file .env.prod \
  pull backend && \
  docker compose -f docker-compose.prod.yml --env-file .env.prod \
  up -d --no-deps backend
```

---

## MLflow: Local vs. Cloud Storage

| | Local (`docker-compose.yml`) | Cloud (`docker-compose.prod.yml`) |
|---|---|---|
| Artifact store | `./mlruns` bind mount on disk | S3 bucket |
| Metadata store | SQLite file inside the container | Shared PostgreSQL instance |
| Survives restart | No — container filesystem is ephemeral | Yes |
| Multi-host safe | No | Yes |

**Migrating existing models from local to S3:**

```bash
# Copy local mlruns artifacts to S3
aws s3 sync ./mlruns s3://your-bucket-name/mlflow-artifacts/mlruns/
```

After copying, re-register or update any model versions whose artifact URIs still point to local paths.

---

## Environment Variable Reference

| Variable | Used by | Description |
|---|---|---|
| `POSTGRES_USER` | db, backend, CDL, MLflow | Database username |
| `POSTGRES_PASSWORD` | db, backend, CDL, MLflow | Database password |
| `POSTGRES_DB` | db, backend, CDL, MLflow | Database name |
| `SECURITY_KEY` | backend | JWT signing secret |
| `ALGORITHM` | backend | JWT algorithm (e.g. `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | backend | Token lifetime |
| `AWS_ACCESS_KEY_ID` | MLflow | S3 credentials |
| `AWS_SECRET_ACCESS_KEY` | MLflow | S3 credentials |
| `AWS_REGION` | MLflow | S3 region |
| `MLFLOW_S3_BUCKET` | MLflow | S3 bucket name for artifacts |
| `CACHE_ENABLED` | CDL | Enable Redis caching (`true`/`false`) |
| `BACKEND_IMAGE` | backend | Registry image tag |
| `CDL_IMAGE` | consumer_delivery | Registry image tag |
| `FRONTEND_IMAGE` | frontend | Registry image tag |

---

## Known Limitations

- **Single host only** — this Compose setup runs all services on one machine. For true horizontal scaling, migrate to Kubernetes or a managed container platform (ECS, Cloud Run).
- **No TLS** — add a reverse proxy (nginx, Caddy, Traefik) in front of all public-facing services for HTTPS.
- **Redis has no persistence** — cached state is lost on restart. Configure AOF or RDB snapshots if cache durability matters.
- **MLflow UI is unauthenticated** — restrict port 5004 to internal network or add an auth proxy if the MLflow UI is accessible externally.
