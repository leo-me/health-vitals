# requirements
install Uvicorn -> ASGI server (Asynchronous Server Gateway Interface)

```
pip install fastapi "uvicorn[standard]"

```

# update requirements.txt
pip freeze > requirements.txt



# how to start the server local 

# root folder 
cd apps/backend

source venv/bin/activate

ENV_FILE=.env.dev uvicorn app.main:app --reload



# postgresSQL 

pip install sqlalchemy psycopg2-binary




use models to create table

# create table with alembic
```sh
pip install alembic

alembic init alembic # create default alembic folder

```

# create table with postgres

1. postgres create a table: CREATE DATABASE health_db
2. update db info to alembic.ini
3. run script to generation file: alembic revision --autogenerate -m "create core tables"
4. create table script:  alembic upgrade head

# update table
1. generate version file:
    ```
    alembic revision --autogenerate -m "update users email and password"
    ```
2. update postgres table

   ```
   alembic upgrade head
   ```



# how to run test

```bash
   source venv/bin/activate
   pytest tests/test_api.py -v
```