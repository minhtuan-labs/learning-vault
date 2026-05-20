import uuid
from app.models.user import User
from app.utils.security import hash_password


def test_login_success(client, db_session):
    """Test successful login."""
    # Create test user
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        first_name="Test",
        last_name="User",
        password_hash=hash_password("password123"),
    )
    db_session.add(user)
    db_session.commit()

    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"


def test_login_invalid_credentials(client, db_session):
    """Test login with invalid credentials."""
    # Create test user
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        first_name="Test",
        last_name="User",
        password_hash=hash_password("password123"),
    )
    db_session.add(user)
    db_session.commit()

    # Try login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"}
    )

    assert response.status_code == 401
