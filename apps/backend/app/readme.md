# requirements
install Uvicorn -> ASGI server (Asynchronous Server Gateway Interface)

```
pip install fastapi "uvicorn[standard]"

```


# how to start the server

cd backend

source venv/bin/activate 

uvicorn app.main:app --reload

