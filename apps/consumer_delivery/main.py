from fastapi import FastAPI

from api.v1.stress import router as data_router
from api.v1.inference import router as inference_router
from api.v1.overview import router as overview_router

app = FastAPI(title='consumer delivery layer', version='0.0.1')

app.include_router(data_router, prefix="/api/v1/data", tags=["data"])
app.include_router(inference_router, prefix="/api/v1/inference", tags=["inference"])
app.include_router(overview_router, prefix="/api/v1/overview", tags=["overview"])


@app.get('/ping')
def check():
    return 'pong'
