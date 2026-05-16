import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.models import User
from app.utils.security import hash_password
from app.main import app

def test_login_success(client: TestClient, db: Session):
    user = User(
        email="test@example.com",
        password_hash=hash_password("password123"),
        full_name="Test User",
        role="member"
    )
    db.add(user)
    db.commit()

    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    assert response.json()["user"]["email"] == "test@example.com"

def test_login_invalid_password(client: TestClient, db: Session):
    user = User(
        email="test@example.com",
        password_hash=hash_password("password123"),
        full_name="Test User",
        role="member"
    )
    db.add(user)
    db.commit()

    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_login_user_not_found(client: TestClient):
    response = client.post("/auth/login", json={
        "email": "notfound@example.com",
        "password": "password123"
    })
    assert response.status_code == 401

def test_get_current_user(client: TestClient, db: Session):
    user = User(
        email="test@example.com",
        password_hash=hash_password("password123"),
        full_name="Test User",
        role="member"
    )
    db.add(user)
    db.commit()

    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_get_current_user_no_token(client: TestClient):
    response = client.get("/auth/me")
    assert response.status_code == 401

def test_change_password(client: TestClient, db: Session):
    user = User(
        email="test@example.com",
        password_hash=hash_password("oldpassword"),
        full_name="Test User",
        role="member"
    )
    db.add(user)
    db.commit()

    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "oldpassword"
    })
    token = login_response.json()["access_token"]

    response = client.post(
        "/users/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": "oldpassword",
            "new_password": "newpassword"
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_change_password_wrong_current(client: TestClient, db: Session):
    user = User(
        email="test@example.com",
        password_hash=hash_password("oldpassword"),
        full_name="Test User",
        role="member"
    )
    db.add(user)
    db.commit()

    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "oldpassword"
    })
    token = login_response.json()["access_token"]

    response = client.post(
        "/users/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": "wrongpassword",
            "new_password": "newpassword"
        }
    )
    assert response.status_code == 400
