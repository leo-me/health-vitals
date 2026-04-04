from fastapi import FastAPI

from app.api.v1.endpoints.users import router as user_router

app = FastAPI(title = 'health vitals', version = '0.0.1')

app.include_router(user_router, prefix="/api/v1")

@app.get('/health')
def check():
  return {'status': 'ok'}