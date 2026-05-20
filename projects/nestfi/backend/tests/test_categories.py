import uuid
from app.models.user import User
from app.models.family import Family, FamilyMembership, RoleEnum, StatusEnum
from app.models.category import Category, CategoryTypeEnum
from app.utils.security import hash_password


def test_default_categories_pre_populated(client, db_session):
    """Test default categories are pre-populated on family creation (US-4.1.1)."""
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

    # Seed default categories
    default_categories = [
        ("Salary", CategoryTypeEnum.income, True),
        ("Bonus", CategoryTypeEnum.income, True),
        ("Investment Return", CategoryTypeEnum.income, True),
        ("Other Income", CategoryTypeEnum.income, True),
        ("Groceries", CategoryTypeEnum.expense, True),
        ("Utilities", CategoryTypeEnum.expense, True),
        ("Entertainment", CategoryTypeEnum.expense, True),
        ("Transportation", CategoryTypeEnum.expense, True),
        ("Healthcare", CategoryTypeEnum.expense, True),
        ("Cash Withdrawal", CategoryTypeEnum.expense, True),
        ("Other Expense", CategoryTypeEnum.expense, True),
        ("Stocks", CategoryTypeEnum.investment, True),
        ("Bonds", CategoryTypeEnum.investment, True),
        ("Real Estate", CategoryTypeEnum.investment, True),
        ("Other Investment", CategoryTypeEnum.investment, True),
    ]

    for name, cat_type, is_default in default_categories:
        cat = Category(
            id=uuid.uuid4(),
            family_id=family.id,
            name=name,
            type=cat_type,
            is_default=is_default,
        )
        db_session.add(cat)
    db_session.commit()

    categories = db_session.query(Category).filter(
        Category.family_id == family.id,
        Category.is_default == True
    ).all()

    assert len(categories) == 15


def test_all_members_can_view_categories(client, db_session):
    """Test all members can view categories (US-4.1.2)."""
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

    category = Category(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Salary",
        type=CategoryTypeEnum.income,
        is_default=True,
    )
    db_session.add(category)
    db_session.commit()

    # Both owner and member should see the category
    categories = db_session.query(Category).filter(
        Category.family_id == family.id
    ).all()

    assert len(categories) == 1
    assert categories[0].name == "Salary"


def test_create_custom_category(client, db_session):
    """Test owner creates custom category (US-4.2.1)."""
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

    mem_owner = FamilyMembership(
        id=uuid.uuid4(),
        family_id=family.id,
        user_id=owner.id,
        role=RoleEnum.owner,
        status=StatusEnum.active,
    )
    db_session.add(mem_owner)
    db_session.commit()

    # Owner creates custom category
    custom_category = Category(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Pet Care",
        type=CategoryTypeEnum.expense,
        is_default=False,
    )
    db_session.add(custom_category)
    db_session.commit()

    categories = db_session.query(Category).filter(
        Category.family_id == family.id,
        Category.name == "Pet Care"
    ).all()

    assert len(categories) == 1
    assert categories[0].is_default is False


def test_default_categories_cannot_be_deleted(client, db_session):
    """Test default categories cannot be deleted (US-4.2.3)."""
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

    default_cat = Category(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Salary",
        type=CategoryTypeEnum.income,
        is_default=True,
    )
    db_session.add(default_cat)
    db_session.commit()

    # Default category should not be deletable
    assert default_cat.is_default is True


def test_custom_categories_can_be_deleted(client, db_session):
    """Test custom categories can be deleted."""
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

    custom_cat = Category(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Custom Category",
        type=CategoryTypeEnum.expense,
        is_default=False,
    )
    db_session.add(custom_cat)
    db_session.commit()

    # Custom category should be deletable
    db_session.delete(custom_cat)
    db_session.commit()

    categories = db_session.query(Category).filter(
        Category.id == custom_cat.id
    ).all()

    assert len(categories) == 0


def test_categories_scoped_to_family(client, db_session):
    """Test categories are scoped to family."""
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

    cat1 = Category(
        id=uuid.uuid4(),
        family_id=family1.id,
        name="Salary",
        type=CategoryTypeEnum.income,
        is_default=True,
    )
    cat2 = Category(
        id=uuid.uuid4(),
        family_id=family2.id,
        name="Bonus",
        type=CategoryTypeEnum.income,
        is_default=True,
    )
    db_session.add(cat1)
    db_session.add(cat2)
    db_session.commit()

    fam1_cats = db_session.query(Category).filter(Category.family_id == family1.id).all()
    fam2_cats = db_session.query(Category).filter(Category.family_id == family2.id).all()

    assert len(fam1_cats) == 1
    assert len(fam2_cats) == 1
    assert fam1_cats[0].name == "Salary"
    assert fam2_cats[0].name == "Bonus"


def test_category_types(client, db_session):
    """Test different category types."""
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
        name="Groceries",
        type=CategoryTypeEnum.expense,
        is_default=True,
    )
    investment_cat = Category(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Stocks",
        type=CategoryTypeEnum.investment,
        is_default=True,
    )
    db_session.add(income_cat)
    db_session.add(expense_cat)
    db_session.add(investment_cat)
    db_session.commit()

    categories = db_session.query(Category).filter(Category.family_id == family.id).all()

    assert len(categories) == 3
    assert income_cat.type == CategoryTypeEnum.income
    assert expense_cat.type == CategoryTypeEnum.expense
    assert investment_cat.type == CategoryTypeEnum.investment


def test_cash_withdrawal_is_expense_category(client, db_session):
    """Test cash withdrawal is standard expense category (US-5.2.3)."""
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

    withdrawal_cat = Category(
        id=uuid.uuid4(),
        family_id=family.id,
        name="Cash Withdrawal",
        type=CategoryTypeEnum.expense,
        is_default=True,
    )
    db_session.add(withdrawal_cat)
    db_session.commit()

    assert withdrawal_cat.type == CategoryTypeEnum.expense
