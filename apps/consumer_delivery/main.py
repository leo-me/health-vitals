from fastapi import FastAPI



app = FastAPI(title = 'consumer delivery layer', version = '0.0.1')


@app.get('/ping')
def check():
  return 'pong'