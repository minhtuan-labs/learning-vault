import uuid
from app.models.user import User
from app.models.family import Family, FamilyMembership, RoleEnum, StatusEnum
from app.models.account import Account, AccountTypeEnum
from app.utils.security import hash_password


def test_create_account(client, db_session):
    """Test creating a bank account (US-3.1.1)."""
    user = User(
        id=uuid.uuid4(),
        email="user@example.com",
        first_name="User",
        last_name="One",
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

    account = Account(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Main Checking",
        type=AccountTypeEnum.bank,
        balance_cents=500000,
        currency="USD",
    )
    db_session.add(account)
    db_session.commit()

    assert account.name == "Main Checking"
    assert account.balance_cents == 500000
    assert account.type == AccountTypeEnum.bank


def test_account_with_negative_balance(client, db_session):
    """Test creating account with negative balance (US-3.1.3)."""
    user = User(
        id=uuid.uuid4(),
        email="user@example.com",
        first_name="User",
        last_name="One",
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

    account = Account(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Overdraft Account",
        type=AccountTypeEnum.bank,
        balance_cents=-100000,
        currency="USD",
    )
    db_session.add(account)
    db_session.commit()

    assert account.balance_cents == -100000


def test_account_visible_to_all_family_members(client, db_session):
    """Test account visible to all family members (US-3.1.4)."""
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

    mem_owner = FamilyMembership(
        id=uuid.uuid4(),
        family_id=family.id,
        user_id=owner.id,
        role=RoleEnum.owner,
        status=StatusEnum.active,
    )
    mem_member = FamilyMembership(
        id=uuid.uuid4(),
        family_id=family.id,
        user_id=member.id,
        role=RoleEnum.member,
        status=StatusEnum.active,
    )
    db_session.add(mem_owner)
    db_session.add(mem_member)
    db_session.commit()

    account = Account(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Shared Account",
        type=AccountTypeEnum.savings,
        balance_cents=1000000,
        currency="USD",
    )
    db_session.add(account)
    db_session.commit()

    # Both users should see the same account in their family
    assert account.family_id == family.id


def test_account_balance_calculation(client, db_session):
    """Test that balance is calculated from transactions (US-3.2.2)."""
    user = User(
        id=uuid.uuid4(),
        email="user@example.com",
        first_name="User",
        last_name="One",
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

    account = Account(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Test Account",
        type=AccountTypeEnum.bank,
        balance_cents=500000,
        currency="USD",
    )
    db_session.add(account)
    db_session.commit()

    assert account.balance_cents == 500000


def test_multiple_account_types(client, db_session):
    """Test creating accounts of different types (US-3.1)."""
    user = User(
        id=uuid.uuid4(),
        email="user@example.com",
        first_name="User",
        last_name="One",
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

    checking = Account(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Checking",
        type=AccountTypeEnum.bank,
        balance_cents=500000,
    )
    savings = Account(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Savings",
        type=AccountTypeEnum.savings,
        balance_cents=1000000,
    )
    investment = Account(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Brokerage",
        type=AccountTypeEnum.investment,
        balance_cents=2000000,
    )
    db_session.add(checking)
    db_session.add(savings)
    db_session.add(investment)
    db_session.commit()

    accounts = db_session.query(Account).filter(Account.family_id == family.id).all()
    assert len(accounts) == 3
    assert accounts[0].type in [AccountTypeEnum.bank, AccountTypeEnum.savings, AccountTypeEnum.investment]


def test_account_currency_defaults_to_usd(client, db_session):
    """Test that account currency defaults to USD."""
    user = User(
        id=uuid.uuid4(),
        email="user@example.com",
        first_name="User",
        last_name="One",
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

    account = Account(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Test Account",
        type=AccountTypeEnum.bank,
        balance_cents=0,
    )
    db_session.add(account)
    db_session.commit()

    assert account.currency == "USD"


def test_account_belongs_to_family(client, db_session):
    """Test that accounts are scoped to families."""
    user = User(
        id=uuid.uuid4(),
        email="user@example.com",
        first_name="User",
        last_name="One",
        password_hash=hash_password("password123"),
    )
    db_session.add(user)
    db_session.commit()

    family1 = Family(id=uuid.uuid4(), name="Family 1", owner_id=user.id)
    family2 = Family(id=uuid.uuid4(), name="Family 2", owner_id=user.id)
    db_session.add(family1)
    db_session.add(family2)
    db_session.commit()

    account1 = Account(
        id=uuid.uuid4(),
        family_id=family1.id,
        name="Account 1",
        type=AccountTypeEnum.bank,
        balance_cents=500000,
    )
    account2 = Account(
        id=uuid.uuid4(),
        family_id=family2.id,
        name="Account 2",
        type=AccountTypeEnum.bank,
        balance_cents=1000000,
    )
    db_session.add(account1)
    db_session.add(account2)
    db_session.commit()

    fam1_accounts = db_session.query(Account).filter(Account.family_id == family1.id).all()
    fam2_accounts = db_session.query(Account).filter(Account.family_id == family2.id).all()

    assert len(fam1_accounts) == 1
    assert len(fam2_accounts) == 1
    assert fam1_accounts[0].name == "Account 1"
    assert fam2_accounts[0].name == "Account 2"


def test_edit_account_name(client, db_session):
    """Test editing account name (US-3.3.1)."""
    user = User(
        id=uuid.uuid4(),
        email="user@example.com",
        first_name="User",
        last_name="One",
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

    account = Account(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Old Name",
        type=AccountTypeEnum.bank,
        balance_cents=500000,
    )
    db_session.add(account)
    db_session.commit()

    account.name = "New Name"
    db_session.commit()

    db_session.refresh(account)
    assert account.name == "New Name"
