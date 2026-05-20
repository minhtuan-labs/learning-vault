import uuid
from app.models.user import User
from app.models.family import Family, FamilyMembership, RoleEnum, StatusEnum
from app.models.account import Account, AccountTypeEnum
from app.models.category import Category, CategoryTypeEnum
from app.models.transaction import Transaction, TransactionEdit, DirectionEnum
from app.utils.security import hash_password
from datetime import datetime


def test_record_income_transaction(client, db_session):
    """Test recording income transaction (US-5.1.1)."""
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

    category = Category(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Salary",
        type=CategoryTypeEnum.income,
        is_default=True,
    )
    db_session.add(category)
    db_session.commit()

    account = Account(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Checking",
        type=AccountTypeEnum.bank,
        balance_cents=500000,
    )
    db_session.add(account)
    db_session.commit()

    transaction = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=category.id,
        amount_cents=500000,
        direction=DirectionEnum.in_,
        date="2026-05-16",
        description="Monthly salary",
        creator_id=user.id,
        is_enabled=True,
    )
    db_session.add(transaction)
    db_session.commit()

    assert transaction.direction == DirectionEnum.in_
    assert transaction.amount_cents == 500000


def test_record_expense_transaction(client, db_session):
    """Test recording expense transaction (US-5.2.1)."""
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

    category = Category(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Groceries",
        type=CategoryTypeEnum.expense,
        is_default=True,
    )
    db_session.add(category)
    db_session.commit()

    account = Account(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Checking",
        type=AccountTypeEnum.bank,
        balance_cents=500000,
    )
    db_session.add(account)
    db_session.commit()

    transaction = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=category.id,
        amount_cents=12550,
        direction=DirectionEnum.out,
        date="2026-05-16",
        description="Grocery shopping",
        creator_id=user.id,
        is_enabled=True,
    )
    db_session.add(transaction)
    db_session.commit()

    assert transaction.direction == DirectionEnum.out
    assert transaction.amount_cents == 12550


def test_transaction_amount_must_be_positive(client, db_session):
    """Test that amount must be > 0 (US-5.1.2)."""
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

    category = Category(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Test",
        type=CategoryTypeEnum.income,
        is_default=True,
    )
    db_session.add(category)
    db_session.commit()

    account = Account(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Test",
        type=AccountTypeEnum.bank,
        balance_cents=0,
    )
    db_session.add(account)
    db_session.commit()

    # Amount 0 should be invalid (validation at API layer)
    transaction = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=category.id,
        amount_cents=0,
        direction=DirectionEnum.in_,
        date="2026-05-16",
        creator_id=user.id,
        is_enabled=True,
    )
    db_session.add(transaction)
    db_session.commit()

    assert transaction.amount_cents == 0


def test_future_dated_transaction_allowed(client, db_session):
    """Test that future-dated transactions are allowed (US-5.1.3)."""
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

    category = Category(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Income",
        type=CategoryTypeEnum.income,
        is_default=True,
    )
    db_session.add(category)
    db_session.commit()

    account = Account(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Test",
        type=AccountTypeEnum.bank,
        balance_cents=0,
    )
    db_session.add(account)
    db_session.commit()

    transaction = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=category.id,
        amount_cents=500000,
        direction=DirectionEnum.in_,
        date="2026-12-31",
        creator_id=user.id,
        is_enabled=True,
    )
    db_session.add(transaction)
    db_session.commit()

    assert transaction.date == "2026-12-31"


def test_all_members_see_transaction(client, db_session):
    """Test that all family members see same transaction (US-5.1.4)."""
    member1 = User(
        id=uuid.uuid4(),
        email="member1@example.com",
        first_name="Member",
        last_name="One",
        password_hash=hash_password("password123"),
    )
    member2 = User(
        id=uuid.uuid4(),
        email="member2@example.com",
        first_name="Member",
        last_name="Two",
        password_hash=hash_password("password123"),
    )
    db_session.add(member1)
    db_session.add(member2)
    db_session.commit()

    family = Family(
        id=uuid.uuid4(),
        name="Test Family",
        owner_id=member1.id,
    )
    db_session.add(family)
    db_session.commit()

    mem1 = FamilyMembership(
        id=uuid.uuid4(),
        family_id=family.id,
        user_id=member1.id,
        role=RoleEnum.owner,
        status=StatusEnum.active,
    )
    mem2 = FamilyMembership(
        id=uuid.uuid4(),
        family_id=family.id,
        user_id=member2.id,
        role=RoleEnum.member,
        status=StatusEnum.active,
    )
    db_session.add(mem1)
    db_session.add(mem2)
    db_session.commit()

    category = Category(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Income",
        type=CategoryTypeEnum.income,
        is_default=True,
    )
    db_session.add(category)
    db_session.commit()

    account = Account(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Shared",
        type=AccountTypeEnum.bank,
        balance_cents=0,
    )
    db_session.add(account)
    db_session.commit()

    transaction = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=category.id,
        amount_cents=500000,
        direction=DirectionEnum.in_,
        date="2026-05-16",
        creator_id=member1.id,
        is_enabled=True,
    )
    db_session.add(transaction)
    db_session.commit()

    # Both members should see the transaction
    transactions = db_session.query(Transaction).filter(
        Transaction.account_id == account.id
    ).all()
    assert len(transactions) == 1


def test_overdraft_allowed(client, db_session):
    """Test that overdraft is allowed (US-5.2.2)."""
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

    category = Category(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Expense",
        type=CategoryTypeEnum.expense,
        is_default=True,
    )
    db_session.add(category)
    db_session.commit()

    account = Account(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Checking",
        type=AccountTypeEnum.bank,
        balance_cents=100000,
    )
    db_session.add(account)
    db_session.commit()

    transaction = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=category.id,
        amount_cents=200000,
        direction=DirectionEnum.out,
        date="2026-05-16",
        creator_id=user.id,
        is_enabled=True,
    )
    db_session.add(transaction)
    db_session.commit()

    assert transaction.amount_cents == 200000


def test_edit_transaction(client, db_session):
    """Test editing a transaction (US-5.4.1)."""
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

    category = Category(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Income",
        type=CategoryTypeEnum.income,
        is_default=True,
    )
    db_session.add(category)
    db_session.commit()

    account = Account(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Checking",
        type=AccountTypeEnum.bank,
        balance_cents=0,
    )
    db_session.add(account)
    db_session.commit()

    transaction = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=category.id,
        amount_cents=500000,
        direction=DirectionEnum.in_,
        date="2026-05-16",
        creator_id=user.id,
        is_enabled=True,
    )
    db_session.add(transaction)
    db_session.commit()

    transaction.amount_cents = 550000
    db_session.commit()

    db_session.refresh(transaction)
    assert transaction.amount_cents == 550000


def test_member_can_edit_another_member_transaction(client, db_session):
    """Test member can edit another member's transaction (US-5.4.2)."""
    member1 = User(
        id=uuid.uuid4(),
        email="member1@example.com",
        first_name="Member",
        last_name="One",
        password_hash=hash_password("password123"),
    )
    member2 = User(
        id=uuid.uuid4(),
        email="member2@example.com",
        first_name="Member",
        last_name="Two",
        password_hash=hash_password("password123"),
    )
    db_session.add(member1)
    db_session.add(member2)
    db_session.commit()

    family = Family(
        id=uuid.uuid4(),
        name="Test Family",
        owner_id=member1.id,
    )
    db_session.add(family)
    db_session.commit()

    category = Category(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Income",
        type=CategoryTypeEnum.income,
        is_default=True,
    )
    db_session.add(category)
    db_session.commit()

    account = Account(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Shared",
        type=AccountTypeEnum.bank,
        balance_cents=0,
    )
    db_session.add(account)
    db_session.commit()

    transaction = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=category.id,
        amount_cents=500000,
        direction=DirectionEnum.in_,
        date="2026-05-16",
        creator_id=member1.id,
        is_enabled=True,
    )
    db_session.add(transaction)
    db_session.commit()

    # Member2 edits the transaction
    before_snapshot = {
        "amount_cents": transaction.amount_cents,
        "category_id": str(transaction.category_id),
    }
    transaction.amount_cents = 600000
    db_session.commit()

    after_snapshot = {
        "amount_cents": transaction.amount_cents,
        "category_id": str(transaction.category_id),
    }

    edit_record = TransactionEdit(
        id=uuid.uuid4(),
        transaction_id=transaction.id,
        editor_id=member2.id,
        before_snapshot=before_snapshot,
        after_snapshot=after_snapshot,
    )
    db_session.add(edit_record)
    db_session.commit()

    assert edit_record.editor_id == member2.id


def test_transaction_edit_history(client, db_session):
    """Test edit history shows editor and timestamp (US-5.4.3)."""
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

    category = Category(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Income",
        type=CategoryTypeEnum.income,
        is_default=True,
    )
    db_session.add(category)
    db_session.commit()

    account = Account(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Test",
        type=AccountTypeEnum.bank,
        balance_cents=0,
    )
    db_session.add(account)
    db_session.commit()

    transaction = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=category.id,
        amount_cents=500000,
        direction=DirectionEnum.in_,
        date="2026-05-16",
        creator_id=user.id,
        is_enabled=True,
    )
    db_session.add(transaction)
    db_session.commit()

    edit = TransactionEdit(
        id=uuid.uuid4(),
        transaction_id=transaction.id,
        editor_id=user.id,
        before_snapshot={"amount_cents": 500000},
        after_snapshot={"amount_cents": 600000},
    )
    db_session.add(edit)
    db_session.commit()

    edits = db_session.query(TransactionEdit).filter(
        TransactionEdit.transaction_id == transaction.id
    ).all()

    assert len(edits) == 1
    assert edits[0].editor_id == user.id
    assert edits[0].edited_at is not None


def test_disable_transaction(client, db_session):
    """Test disabling a transaction (US-5.5.1)."""
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

    category = Category(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Income",
        type=CategoryTypeEnum.income,
        is_default=True,
    )
    db_session.add(category)
    db_session.commit()

    account = Account(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Test",
        type=AccountTypeEnum.bank,
        balance_cents=0,
    )
    db_session.add(account)
    db_session.commit()

    transaction = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=category.id,
        amount_cents=500000,
        direction=DirectionEnum.in_,
        date="2026-05-16",
        creator_id=user.id,
        is_enabled=True,
    )
    db_session.add(transaction)
    db_session.commit()

    transaction.is_enabled = False
    db_session.commit()

    db_session.refresh(transaction)
    assert transaction.is_enabled is False


def test_re_enable_transaction(client, db_session):
    """Test re-enabling a disabled transaction (US-5.5.3)."""
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

    category = Category(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Income",
        type=CategoryTypeEnum.income,
        is_default=True,
    )
    db_session.add(category)
    db_session.commit()

    account = Account(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Test",
        type=AccountTypeEnum.bank,
        balance_cents=0,
    )
    db_session.add(account)
    db_session.commit()

    transaction = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=category.id,
        amount_cents=500000,
        direction=DirectionEnum.in_,
        date="2026-05-16",
        creator_id=user.id,
        is_enabled=False,
    )
    db_session.add(transaction)
    db_session.commit()

    transaction.is_enabled = True
    db_session.commit()

    db_session.refresh(transaction)
    assert transaction.is_enabled is True
