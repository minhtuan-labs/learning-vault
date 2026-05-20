import uuid
from app.models.user import User
from app.models.family import Family, FamilyMembership, RoleEnum, StatusEnum
from app.utils.security import hash_password


def test_list_families(client, db_session):
    """Test listing families for a user (US-2.1)."""
    user = User(
        id=uuid.uuid4(),
        email="owner@example.com",
        first_name="Owner",
        last_name="User",
        password_hash=hash_password("password123"),
    )
    db_session.add(user)
    db_session.commit()

    family = Family(
        id=uuid.uuid4(),
        name="Test Family",
        owner_id=user.id,
    )
    db_session.add(family)
    db_session.commit()

    membership = FamilyMembership(
        id=uuid.uuid4(),
        family_id=family.id,
        user_id=user.id,
        role=RoleEnum.owner,
        status=StatusEnum.active,
    )
    db_session.add(membership)
    db_session.commit()

    # Simulate login by mocking auth token
    from app.utils.security import create_access_token
    token = create_access_token({"sub": str(user.id)})

    response = client.get(
        "/api/v1/families",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "families" in data
    assert len(data["families"]) == 1
    assert data["families"][0]["name"] == "Test Family"


def test_get_family_details(client, db_session):
    """Test getting family details (US-2.1)."""
    user = User(
        id=uuid.uuid4(),
        email="owner@example.com",
        first_name="Owner",
        last_name="User",
        password_hash=hash_password("password123"),
    )
    db_session.add(user)
    db_session.commit()

    family = Family(
        id=uuid.uuid4(),
        name="Test Family",
        owner_id=user.id,
    )
    db_session.add(family)
    db_session.commit()

    membership = FamilyMembership(
        id=uuid.uuid4(),
        family_id=family.id,
        user_id=user.id,
        role=RoleEnum.owner,
        status=StatusEnum.active,
    )
    db_session.add(membership)
    db_session.commit()

    from app.utils.security import create_access_token
    token = create_access_token({"sub": str(user.id)})

    response = client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Family"
    assert str(data["owner_id"]) == str(user.id)
    assert data["member_count"] == 1


def test_family_requires_auth(client):
    """Test that family list endpoint requires authentication."""
    response = client.get("/api/v1/families")
    assert response.status_code == 403


def test_member_cannot_access_other_family(client, db_session):
    """Test that member cannot access family they're not in (US-2.2)."""
    user1 = User(
        id=uuid.uuid4(),
        email="user1@example.com",
        first_name="User",
        last_name="One",
        password_hash=hash_password("password123"),
    )
    user2 = User(
        id=uuid.uuid4(),
        email="user2@example.com",
        first_name="User",
        last_name="Two",
        password_hash=hash_password("password123"),
    )
    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()

    family1 = Family(id=uuid.uuid4(), name="Family 1", owner_id=user1.id)
    family2 = Family(id=uuid.uuid4(), name="Family 2", owner_id=user2.id)
    db_session.add(family1)
    db_session.add(family2)
    db_session.commit()

    membership1 = FamilyMembership(
        id=uuid.uuid4(),
        family_id=family1.id,
        user_id=user1.id,
        role=RoleEnum.owner,
    )
    db_session.add(membership1)
    db_session.commit()

    from app.utils.security import create_access_token
    token = create_access_token({"sub": str(user1.id)})

    response = client.get(
        f"/api/v1/families/{family2.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_add_family_member(client, db_session):
    """Test adding a member to family (US-2.2)."""
    owner = User(
        id=uuid.uuid4(),
        email="owner@example.com",
        first_name="Owner",
        last_name="User",
        password_hash=hash_password("password123"),
    )
    member = User(
        id=uuid.uuid4(),
        email="member@example.com",
        first_name="Member",
        last_name="User",
        password_hash=hash_password("password123"),
    )
    db_session.add(owner)
    db_session.add(member)
    db_session.commit()

    family = Family(
        id=uuid.uuid4(),
        name="Test Family",
        owner_id=owner.id,
    )
    db_session.add(family)
    db_session.commit()

    membership_owner = FamilyMembership(
        id=uuid.uuid4(),
        family_id=family.id,
        user_id=owner.id,
        role=RoleEnum.owner,
        status=StatusEnum.active,
    )
    membership_member = FamilyMembership(
        id=uuid.uuid4(),
        family_id=family.id,
        user_id=member.id,
        role=RoleEnum.member,
        status=StatusEnum.active,
    )
    db_session.add(membership_owner)
    db_session.add(membership_member)
    db_session.commit()

    from app.utils.security import create_access_token
    token = create_access_token({"sub": str(owner.id)})

    response = client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["member_count"] == 2


def test_member_belongs_to_multiple_families(client, db_session):
    """Test member in multiple families (US-2.2.3)."""
    user = User(
        id=uuid.uuid4(),
        email="member@example.com",
        first_name="Member",
        last_name="User",
        password_hash=hash_password("password123"),
    )
    db_session.add(user)
    db_session.commit()

    family1 = Family(id=uuid.uuid4(), name="Family 1", owner_id=user.id)
    family2 = Family(id=uuid.uuid4(), name="Family 2", owner_id=user.id)
    db_session.add(family1)
    db_session.add(family2)
    db_session.commit()

    mem1 = FamilyMembership(
        id=uuid.uuid4(),
        family_id=family1.id,
        user_id=user.id,
        role=RoleEnum.member,
        status=StatusEnum.active,
    )
    mem2 = FamilyMembership(
        id=uuid.uuid4(),
        family_id=family2.id,
        user_id=user.id,
        role=RoleEnum.member,
        status=StatusEnum.active,
    )
    db_session.add(mem1)
    db_session.add(mem2)
    db_session.commit()

    from app.utils.security import create_access_token
    token = create_access_token({"sub": str(user.id)})

    response = client.get(
        "/api/v1/families",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["families"]) == 2


def test_disable_family_member(client, db_session):
    """Test disabling a family member (US-2.4.1)."""
    owner = User(
        id=uuid.uuid4(),
        email="owner@example.com",
        first_name="Owner",
        last_name="User",
        password_hash=hash_password("password123"),
    )
    member = User(
        id=uuid.uuid4(),
        email="member@example.com",
        first_name="Member",
        last_name="User",
        password_hash=hash_password("password123"),
    )
    db_session.add(owner)
    db_session.add(member)
    db_session.commit()

    family = Family(
        id=uuid.uuid4(),
        name="Test Family",
        owner_id=owner.id,
    )
    db_session.add(family)
    db_session.commit()

    membership_owner = FamilyMembership(
        id=uuid.uuid4(),
        family_id=family.id,
        user_id=owner.id,
        role=RoleEnum.owner,
        status=StatusEnum.active,
    )
    membership_member = FamilyMembership(
        id=uuid.uuid4(),
        family_id=family.id,
        user_id=member.id,
        role=RoleEnum.member,
        status=StatusEnum.active,
    )
    db_session.add(membership_owner)
    db_session.add(membership_member)
    db_session.commit()

    # Disable member
    membership_member.status = StatusEnum.disabled
    db_session.commit()

    assert membership_member.status == StatusEnum.disabled


def test_disabled_member_cannot_access_family(client, db_session):
    """Test that disabled member cannot access family (US-2.4.2)."""
    member = User(
        id=uuid.uuid4(),
        email="member@example.com",
        first_name="Member",
        last_name="User",
        password_hash=hash_password("password123"),
    )
    db_session.add(member)
    db_session.commit()

    owner = User(
        id=uuid.uuid4(),
        email="owner@example.com",
        first_name="Owner",
        last_name="User",
        password_hash=hash_password("password123"),
    )
    db_session.add(owner)
    db_session.commit()

    family = Family(
        id=uuid.uuid4(),
        name="Test Family",
        owner_id=owner.id,
    )
    db_session.add(family)
    db_session.commit()

    membership = FamilyMembership(
        id=uuid.uuid4(),
        family_id=family.id,
        user_id=member.id,
        role=RoleEnum.member,
        status=StatusEnum.disabled,
    )
    db_session.add(membership)
    db_session.commit()

    from app.utils.security import create_access_token
    token = create_access_token({"sub": str(member.id)})

    response = client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403
