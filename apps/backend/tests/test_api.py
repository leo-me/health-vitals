from fastapi import Depends
from fastapi.testclient import TestClient

from app.models.user import User, UserTypeEnum

from tests.conftest import override_get_db



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


def test_delete_user(client, admin_token):
  # create_admin = client.post("/api/v1/users",json={
  #   "email": "admin@163.com",
  #   "password": "adminpass"
  # })

  # assert create_admin.status_code == 200

  # create_user = client.post("/api/v1/users",json={
  #   "email": "user@163.com",
  #   "password": "1111"
  # })


  # login = client.post("api/v1/auth/login", data={
  #    "username": "admin@163.com",
  #    "password": "adminpass"
  # })

  # assert login.status_code == 200


  # token = login.json()["access_token"]


  # id = create_admin.json()["id"]
  # print("id", id)

  # update = client.patch(f"/api/v1/users/{id}", json={
  #     "user_type": UserTypeEnum.ADMIN
  # }, headers={"Authorization": f"Bearer {token}"})

  # assert update.status_code == 200

  # 2. directly edit the db, set user_type with admin
  # db = next(override_get_db())
  # admin_user = db.query(User).filter_by(email="admin@163.com").first()
  # admin_user.user_type = UserTypeEnum.ADMIN
  # db.commit()
  # db.close()
  # delete = client.delete(f"/api/v1/users/{user_id}", headers={"Authorization", f"Bearer {token}"})



  create_user = client.post("/api/v1/users",json={
    "email": "user@163.com",
    "password": "1111"
  })


  user_id = create_user.json()["id"]


  delete = client.delete(
          f"/api/v1/users/{user_id}",
          headers={"Authorization": f"Bearer {admin_token}"}
      )

  assert delete.status_code == 200

  assert delete.json()["message"] == "User deleted"



