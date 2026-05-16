from fastapi import FastAPI

from api.v1.stress import router as data_router

app = FastAPI(title='consumer delivery layer', version='0.0.1')

app.include_router(data_router, prefix="/api/v1/data", tags=["data"])


@app.get('/ping')
def check():
    return 'pong'
