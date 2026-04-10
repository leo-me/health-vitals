import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

from app.main import app
from app.db.session import get_db
from app.db.base import Base
from app.models.user import User, UserTypeEnum
from app.core.security import hash_password


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

@pytest.fixture
def db(client):
    session = TestSessionLocal()
    yield session
    session.close()

@pytest.fixture
def admin_user(db):
    user = User(
        email="admin@163.com",
        password=hash_password("adminpass"),
        user_type=UserTypeEnum.ADMIN
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.delete(user)
    db.commit()

@pytest.fixture
def admin_token(client, admin_user):
    res = client.post("/api/v1/auth/login", data={
        "username": admin_user.email,
        "password": "adminpass"
    })
    return res.json()["access_token"]

@pytest.fixture
def recording_ids():
  return {
    "id": str(uuid.uuid4()),
    "device_id": str(uuid.uuid4()),
    "user_id": str(uuid.uuid4())
  }
