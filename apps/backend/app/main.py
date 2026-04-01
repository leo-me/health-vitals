from fastapi import FastAPI

app = FastAPI(title = 'health vitals', version = '0.0.1')

@app.get('/health')
def check():
  return {'status': 'ok'}