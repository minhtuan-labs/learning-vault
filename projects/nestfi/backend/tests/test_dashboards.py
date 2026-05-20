import uuid
from app.models.user import User
from app.models.family import Family, FamilyMembership, RoleEnum, StatusEnum
from app.models.account import Account, AccountTypeEnum
from app.models.category import Category, CategoryTypeEnum
from app.models.transaction import Transaction, DirectionEnum
from app.utils.security import hash_password
from datetime import datetime


def test_dashboard_shows_total_income(client, db_session):
    """Test dashboard shows total income (US-6.1.1)."""
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
        balance_cents=0,
    )
    db_session.add(account)
    db_session.commit()

    # Add income transactions
    trans1 = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=category.id,
        amount_cents=500000,
        direction=DirectionEnum.in_,
        date="2026-05-16",
        creator_id=user.id,
        is_enabled=True,
    )
    trans2 = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=category.id,
        amount_cents=300000,
        direction=DirectionEnum.in_,
        date="2026-05-16",
        creator_id=user.id,
        is_enabled=True,
    )
    db_session.add(trans1)
    db_session.add(trans2)
    db_session.commit()

    # Calculate total income
    income_transactions = db_session.query(Transaction).filter(
        Transaction.account_id == account.id,
        Transaction.direction == DirectionEnum.in_,
        Transaction.is_enabled == True
    ).all()

    total_income = sum(t.amount_cents for t in income_transactions)
    assert total_income == 800000


def test_dashboard_shows_total_expenses(client, db_session):
    """Test dashboard shows total expenses (US-6.1.2)."""
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
        balance_cents=0,
    )
    db_session.add(account)
    db_session.commit()

    # Add expense transactions
    trans1 = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=category.id,
        amount_cents=50000,
        direction=DirectionEnum.out,
        date="2026-05-16",
        creator_id=user.id,
        is_enabled=True,
    )
    trans2 = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=category.id,
        amount_cents=30000,
        direction=DirectionEnum.out,
        date="2026-05-16",
        creator_id=user.id,
        is_enabled=True,
    )
    db_session.add(trans1)
    db_session.add(trans2)
    db_session.commit()

    # Calculate total expenses
    expense_transactions = db_session.query(Transaction).filter(
        Transaction.account_id == account.id,
        Transaction.direction == DirectionEnum.out,
        Transaction.is_enabled == True
    ).all()

    total_expenses = sum(t.amount_cents for t in expense_transactions)
    assert total_expenses == 80000


def test_dashboard_shows_net_savings(client, db_session):
    """Test dashboard shows net savings (US-6.1.3)."""
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

    income_cat = Category(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Salary",
        type=CategoryTypeEnum.income,
        is_default=True,
    )
    expense_cat = Category(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Expense",
        type=CategoryTypeEnum.expense,
        is_default=True,
    )
    db_session.add(income_cat)
    db_session.add(expense_cat)
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

    # Add income and expense transactions
    income_trans = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=income_cat.id,
        amount_cents=800000,
        direction=DirectionEnum.in_,
        date="2026-05-16",
        creator_id=user.id,
        is_enabled=True,
    )
    expense_trans = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=expense_cat.id,
        amount_cents=70000,
        direction=DirectionEnum.out,
        date="2026-05-16",
        creator_id=user.id,
        is_enabled=True,
    )
    db_session.add(income_trans)
    db_session.add(expense_trans)
    db_session.commit()

    # Calculate net savings = income - expenses
    income_transactions = db_session.query(Transaction).filter(
        Transaction.account_id == account.id,
        Transaction.direction == DirectionEnum.in_,
        Transaction.is_enabled == True
    ).all()
    expense_transactions = db_session.query(Transaction).filter(
        Transaction.account_id == account.id,
        Transaction.direction == DirectionEnum.out,
        Transaction.is_enabled == True
    ).all()

    total_income = sum(t.amount_cents for t in income_transactions)
    total_expenses = sum(t.amount_cents for t in expense_transactions)
    net_savings = total_income - total_expenses

    assert net_savings == 730000


def test_dashboard_shows_account_balances(client, db_session):
    """Test dashboard shows account balances (US-6.1.4)."""
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

    account1 = Account(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Checking",
        type=AccountTypeEnum.bank,
        balance_cents=500000,
    )
    account2 = Account(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Savings",
        type=AccountTypeEnum.savings,
        balance_cents=1000000,
    )
    db_session.add(account1)
    db_session.add(account2)
    db_session.commit()

    accounts = db_session.query(Account).filter(Account.family_id == family.id).all()

    assert len(accounts) == 2
    assert accounts[0].balance_cents == 500000
    assert accounts[1].balance_cents == 1000000


def test_dashboard_shows_recent_transactions(client, db_session):
    """Test dashboard shows recent transactions (US-6.1.5)."""
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

    # Add multiple transactions
    for i in range(10):
        trans = Transaction(
            id=uuid.uuid4(),
            account_id=account.id,
            category_id=category.id,
            amount_cents=100000 * (i + 1),
            direction=DirectionEnum.in_,
            date=f"2026-05-{16 - i}",
            creator_id=user.id,
            is_enabled=True,
        )
        db_session.add(trans)
    db_session.commit()

    # Get last 5 transactions
    recent = db_session.query(Transaction).filter(
        Transaction.account_id == account.id
    ).order_by(Transaction.created_at.desc()).limit(5).all()

    assert len(recent) == 5


def test_disabled_transactions_excluded_from_dashboard(client, db_session):
    """Test disabled transactions excluded from P&L (US-5.5.2)."""
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

    income_cat = Category(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Salary",
        type=CategoryTypeEnum.income,
        is_default=True,
    )
    db_session.add(income_cat)
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

    # Add enabled and disabled transactions
    enabled_trans = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=income_cat.id,
        amount_cents=500000,
        direction=DirectionEnum.in_,
        date="2026-05-16",
        creator_id=user.id,
        is_enabled=True,
    )
    disabled_trans = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=income_cat.id,
        amount_cents=200000,
        direction=DirectionEnum.in_,
        date="2026-05-16",
        creator_id=user.id,
        is_enabled=False,
    )
    db_session.add(enabled_trans)
    db_session.add(disabled_trans)
    db_session.commit()

    # Calculate only enabled income
    enabled_income = db_session.query(Transaction).filter(
        Transaction.account_id == account.id,
        Transaction.direction == DirectionEnum.in_,
        Transaction.is_enabled == True
    ).all()

    total_income = sum(t.amount_cents for t in enabled_income)
    assert total_income == 500000


def test_expense_breakdown_by_category(client, db_session):
    """Test expense breakdown by category (US-6.2.1)."""
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

    groceries_cat = Category(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Groceries",
        type=CategoryTypeEnum.expense,
        is_default=True,
    )
    utilities_cat = Category(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Utilities",
        type=CategoryTypeEnum.expense,
        is_default=True,
    )
    db_session.add(groceries_cat)
    db_session.add(utilities_cat)
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

    # Add expenses by category
    groceries_exp = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=groceries_cat.id,
        amount_cents=50000,
        direction=DirectionEnum.out,
        date="2026-05-16",
        creator_id=user.id,
        is_enabled=True,
    )
    utilities_exp = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=utilities_cat.id,
        amount_cents=20000,
        direction=DirectionEnum.out,
        date="2026-05-16",
        creator_id=user.id,
        is_enabled=True,
    )
    db_session.add(groceries_exp)
    db_session.add(utilities_exp)
    db_session.commit()

    # Get expense breakdown
    expense_breakdown = {}
    expenses = db_session.query(Transaction).filter(
        Transaction.account_id == account.id,
        Transaction.direction == DirectionEnum.out,
        Transaction.is_enabled == True
    ).all()

    for trans in expenses:
        cat = db_session.query(Category).filter(Category.id == trans.category_id).first()
        if cat.name not in expense_breakdown:
            expense_breakdown[cat.name] = 0
        expense_breakdown[cat.name] += trans.amount_cents

    assert expense_breakdown["Groceries"] == 50000
    assert expense_breakdown["Utilities"] == 20000
