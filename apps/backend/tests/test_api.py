from fastapi.testclient import TestClient


def test_register_success(client):
  response = client.post("/api/v1/users/", json={
    "email": "test@gmail.com",
    "password": "123456"
  })

  assert response.status_code == 200
  assert response.json()['email'] == "test@gmail.com"



def test_login_success(client):
  create = client.post("/api/v1/users/", json={
    "email": "test@gmail.com",
    "password": "123456"
  })

  assert create.status_code == 200

  response = client.post('/api/v1/auth/login', data={
    "username": 'test@gmail.com',
    "password": "123456"
  })

  assert response.status_code == 200

  assert response.json()['access_token'] is not None


def test_register_duplicate_email(client):
  create = client.post("/api/v1/users/", json={
    "email": "test@gmail.com",
    "password": "123456"
  })

  assert create.status_code == 200

  duplicate = client.post("/api/v1/users/", json={
    "email": "test@gmail.com",
    "password": "123456"
  })


  assert duplicate.status_code == 409

  assert duplicate.json()['detail'] == "Email already registered"


