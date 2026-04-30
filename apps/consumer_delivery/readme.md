# Consumer Delivery Layer

The Consumer Delivery Layer is a lightweight FastAPI service responsible for exposing processed health insights to end users. It sits at the outermost edge of the health vitals platform, consuming inference results produced by the backend pipeline and serving them through a clean, versioned REST API.

## Responsibilities

- Retrieve and format stress detection results for consumer-facing endpoints
- Decouple the presentation contract from the internal data pipeline
- Absorb model redeployment changes at the schema boundary, without propagating them upstream

## Architecture Role

This service is a dedicated container in the health vitals architecture. It communicates with the backend via HTTP, maintaining an explicit interface boundary that isolates consumer-facing concerns from core pipeline logic. This separation is the primary mechanism enabling maintainability under model evolution scenarios (ATAM scenarios S1–S10).

## Tech Stack

- **Runtime**: Python 3.11+
- **Framework**: FastAPI
- **Server**: Uvicorn (containerized via Docker)



# use venv 
python -m venv .venv

# activate（Mac/Linux）
source .venv/bin/activate

# activate and add dependency
pip install fastapi uvicorn

pip freeze > requirements.txt

# run app
uvicorn main:app --reload --port 8001



