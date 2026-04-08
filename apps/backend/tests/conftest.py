import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import get_db
from app.db.base import Base

TEST_DATABASE_URL = "postgresql://postgres:0000@localhost:5432/health_db_test"


test_engine = create_engine(TEST_DATABASE_URL)

TestSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


def override_get_db():
  db = TestSessionLocal()
  try:
    yield db
  finally:
    db.close()




@pytest.fixture()
def client():
  # 1. create table
  Base.metadata.create_all(bind=test_engine)

  # 2. override get_db
  app.dependency_overrides[get_db] = override_get_db

  # 3. yield client
  with TestClient(app) as c:
    yield c

  # 4. delete table  and clear dependency_override when test finished
  Base.metadata.drop_all(bind=test_engine)
  app.dependency_overrides.clear()
