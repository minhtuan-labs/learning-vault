import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.models import User, Family, FamilyMember, Category, Transaction
from app.utils.security import hash_password
from datetime import datetime, date

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

def test_create_transaction(client: TestClient, db: Session):
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

    category = Category(
        family_id=family.id,
        type="expense",
        name="Groceries",
        color="#FF9800",
        is_default=True,
        is_active=True
    )
    db.add(category)
    db.commit()

    token = get_token(client, db, "user@example.com")
    response = client.post(
        f"/families/{family.id}/transactions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "category_id": category.id,
            "type": "expense",
            "amount": 50.00,
            "description": "Groceries",
            "transaction_date": "2026-05-16"
        }
    )

    assert response.status_code == 201
    assert response.json()["amount"] == 50.0
    assert response.json()["type"] == "expense"

def test_list_transactions(client: TestClient, db: Session):
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

    category = Category(
        family_id=family.id,
        type="expense",
        name="Groceries",
        is_default=True,
        is_active=True
    )
    db.add(category)
    db.flush()

    txn = Transaction(
        family_id=family.id,
        user_id=user.id,
        category_id=category.id,
        type="expense",
        amount=50.00,
        transaction_date=date.today()
    )
    db.add(txn)
    db.commit()

    token = get_token(client, db, "user@example.com")
    response = client.get(
        f"/families/{family.id}/transactions",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert len(response.json()["transactions"]) == 1
    assert response.json()["total"] == 1

def test_soft_delete_transaction(client: TestClient, db: Session):
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

    category = Category(
        family_id=family.id,
        type="expense",
        name="Groceries",
        is_default=True,
        is_active=True
    )
    db.add(category)
    db.flush()

    txn = Transaction(
        family_id=family.id,
        user_id=user.id,
        category_id=category.id,
        type="expense",
        amount=50.00,
        transaction_date=date.today()
    )
    db.add(txn)
    db.commit()

    token = get_token(client, db, "user@example.com")
    response = client.delete(
        f"/families/{family.id}/transactions/{txn.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 204

    # Verify deleted
    response = client.get(
        f"/families/{family.id}/transactions",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert len(response.json()["transactions"]) == 0

def test_update_transaction(client: TestClient, db: Session):
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

    category = Category(
        family_id=family.id,
        type="expense",
        name="Groceries",
        is_default=True,
        is_active=True
    )
    db.add(category)
    db.flush()

    txn = Transaction(
        family_id=family.id,
        user_id=user.id,
        category_id=category.id,
        type="expense",
        amount=50.00,
        transaction_date=date.today()
    )
    db.add(txn)
    db.commit()

    token = get_token(client, db, "user@example.com")
    response = client.put(
        f"/families/{family.id}/transactions/{txn.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"amount": 75.00}
    )

    assert response.status_code == 200
    assert response.json()["amount"] == 75.0

def test_transaction_pagination(client: TestClient, db: Session):
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

    category = Category(
        family_id=family.id,
        type="expense",
        name="Groceries",
        is_default=True,
        is_active=True
    )
    db.add(category)
    db.flush()

    # Create 50 transactions
    for i in range(50):
        txn = Transaction(
            family_id=family.id,
            user_id=user.id,
            category_id=category.id,
            type="expense",
            amount=10.0 + i,
            transaction_date=date.today()
        )
        db.add(txn)
    db.commit()

    token = get_token(client, db, "user@example.com")
    response = client.get(
        f"/families/{family.id}/transactions?skip=0&limit=30",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert len(response.json()["transactions"]) == 30
    assert response.json()["total"] == 50

    response = client.get(
        f"/families/{family.id}/transactions?skip=30&limit=30",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert len(response.json()["transactions"]) == 20
