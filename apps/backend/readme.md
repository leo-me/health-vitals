# requirements
install Uvicorn -> ASGI server (Asynchronous Server Gateway Interface)

```
pip install fastapi "uvicorn[standard]"

```

# update requirements.txt
pip freeze > requirements.txt



# how to start the server local 

# root folder 
```sh
cd apps/backend

source venv/bin/activate

ENV_FILE=.env.dev uvicorn app.main:app --reload

docker compose up --build 

```

# postgresSQL 

pip install sqlalchemy psycopg2-binary


use models to create table

# create table with alembic
```sh
pip install alembic

alembic init alembic # create default alembic folder

```

# use alembic to create database

1. postgres create a database: CREATE DATABASE health_db
2. update db info to alembic.ini
3. run script to generation file: alembic revision --autogenerate -m "create core tables"

# use alembic to create  new table (local development)
1. update models/base.py add new table
2. update migrations/env.py, add new table
3. run script
   ```sh
   ENV_FILE=.env.dev alembic revision --autogenerate -m "create info"

   ENV_FILE=.env.dev alembic upgrade head

   ```

# update table
1. generate version file:
    ```sh
    ENV_FILE=.env.dev alembic revision --autogenerate -m "update users email and password"
    ```
2. update postgres table

   ```
   ENV_FILE=.env.dev alembic upgrade head
   ```


# how to run test

```bash
   source venv/bin/activate
   pytest tests/test_api.py -v
```