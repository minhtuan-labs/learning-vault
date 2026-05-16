import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.models import User, Family, FamilyMember, Invitation
from app.utils.security import hash_password
from datetime import datetime, timedelta
import uuid

def create_test_user(db: Session, email: str, role: str = "member"):
    user = User(
        email=email,
        password_hash=hash_password("password123"),
        full_name="Test User",
        role=role
    )
    db.add(user)
    db.commit()
    return user

def get_token(client: TestClient, db: Session, email: str):
    login_response = client.post("/auth/login", json={
        "email": email,
        "password": "password123"
    })
    return login_response.json()["access_token"]

def test_list_families(client: TestClient, db: Session):
    user = create_test_user(db, "user@example.com")
    family = Family(
        name="Test Family",
        description="A test family",
        created_by_user_id=user.id
    )
    db.add(family)
    db.flush()

    member = FamilyMember(
        family_id=family.id,
        user_id=user.id,
        role="owner",
        status="active",
        joined_at=datetime.utcnow()
    )
    db.add(member)
    db.commit()

    token = get_token(client, db, "user@example.com")
    response = client.get(
        "/families",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert len(response.json()["families"]) == 1
    assert response.json()["families"][0]["name"] == "Test Family"

def test_get_family_not_member(client: TestClient, db: Session):
    user = create_test_user(db, "user@example.com")
    other_user = create_test_user(db, "other@example.com")

    family = Family(
        name="Test Family",
        created_by_user_id=user.id
    )
    db.add(family)
    db.commit()

    token = get_token(client, db, "other@example.com")
    response = client.get(
        f"/families/{family.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403

def test_invite_member(client: TestClient, db: Session):
    user = create_test_user(db, "user@example.com")
    family = Family(
        name="Test Family",
        created_by_user_id=user.id
    )
    db.add(family)
    db.flush()

    member = FamilyMember(
        family_id=family.id,
        user_id=user.id,
        role="owner",
        status="active",
        joined_at=datetime.utcnow()
    )
    db.add(member)
    db.commit()

    token = get_token(client, db, "user@example.com")
    response = client.post(
        f"/families/{family.id}/members",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "newmember@example.com", "role": "member"}
    )

    assert response.status_code == 201
    assert response.json()["email"] == "newmember@example.com"
    assert response.json()["status"] == "pending"

def test_invite_member_not_owner(client: TestClient, db: Session):
    user = create_test_user(db, "user@example.com")
    other_user = create_test_user(db, "other@example.com")

    family = Family(
        name="Test Family",
        created_by_user_id=user.id
    )
    db.add(family)
    db.flush()

    member = FamilyMember(
        family_id=family.id,
        user_id=other_user.id,
        role="member",
        status="active",
        joined_at=datetime.utcnow()
    )
    db.add(member)
    db.commit()

    token = get_token(client, db, "other@example.com")
    response = client.post(
        f"/families/{family.id}/members",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "newmember@example.com", "role": "member"}
    )

    assert response.status_code == 403

def test_accept_invitation_new_user(client: TestClient, db: Session):
    user = create_test_user(db, "user@example.com")
    family = Family(
        name="Test Family",
        created_by_user_id=user.id
    )
    db.add(family)
    db.flush()

    token_uuid = uuid.uuid4()
    invitation = Invitation(
        email="newuser@example.com",
        family_id=family.id,
        token=token_uuid,
        invited_by_user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.add(invitation)
    db.commit()

    response = client.post(
        f"/invitations/{token_uuid}/accept",
        json={
            "full_name": "New User",
            "password": "newpassword123"
        }
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "access_token" in response.json()

def test_accept_expired_invitation(client: TestClient, db: Session):
    user = create_test_user(db, "user@example.com")
    family = Family(
        name="Test Family",
        created_by_user_id=user.id
    )
    db.add(family)
    db.flush()

    token_uuid = uuid.uuid4()
    invitation = Invitation(
        email="newuser@example.com",
        family_id=family.id,
        token=token_uuid,
        invited_by_user_id=user.id,
        expires_at=datetime.utcnow() - timedelta(days=1)
    )
    db.add(invitation)
    db.commit()

    response = client.post(
        f"/invitations/{token_uuid}/accept",
        json={
            "full_name": "New User",
            "password": "newpassword123"
        }
    )

    assert response.status_code == 409
