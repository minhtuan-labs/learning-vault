"""Seed script to populate initial data: superadmin, default categories, test families."""
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.config import settings
from app.models.user import User
from app.models.family import Family, FamilyMembership, RoleEnum
from app.models.category import Category, CategoryTypeEnum
from app.models.account import Account, AccountTypeEnum
from app.utils.security import hash_password


def seed_database():
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Check if data already exists
        existing_users = session.query(User).count()
        if existing_users > 0:
            print("Database already seeded. Skipping...")
            return

        # Create superadmin user
        superadmin = User(
            id=uuid.uuid4(),
            email="superadmin@nestfi.local",
            first_name="Super",
            last_name="Admin",
            password_hash=hash_password("admin123"),
            is_active=True,
            is_superadmin=True,
        )
        session.add(superadmin)
        session.flush()

        # Create test users
        user1 = User(
            id=uuid.uuid4(),
            email="alice@example.com",
            first_name="Alice",
            last_name="Smith",
            password_hash=hash_password("password123"),
            is_active=True,
        )
        user2 = User(
            id=uuid.uuid4(),
            email="bob@example.com",
            first_name="Bob",
            last_name="Johnson",
            password_hash=hash_password("password123"),
            is_active=True,
        )
        session.add(user1)
        session.add(user2)
        session.flush()

        # Create test family
        family = Family(
            id=uuid.uuid4(),
            name="Smith Household",
            owner_id=user1.id,
        )
        session.add(family)
        session.flush()

        # Add family members
        membership1 = FamilyMembership(
            id=uuid.uuid4(),
            family_id=family.id,
            user_id=user1.id,
            role=RoleEnum.owner,
        )
        membership2 = FamilyMembership(
            id=uuid.uuid4(),
            family_id=family.id,
            user_id=user2.id,
            role=RoleEnum.member,
        )
        session.add(membership1)
        session.add(membership2)
        session.flush()

        # Create accounts
        checking = Account(
            id=uuid.uuid4(),
            family_id=family.id,
            name="Checking",
            type=AccountTypeEnum.bank,
            balance_cents=50000,
            currency="USD",
        )
        savings = Account(
            id=uuid.uuid4(),
            family_id=family.id,
            name="Savings",
            type=AccountTypeEnum.savings,
            balance_cents=100000,
            currency="USD",
        )
        session.add(checking)
        session.add(savings)
        session.flush()

        # Create default categories
        default_categories = [
            ("Groceries", CategoryTypeEnum.expense),
            ("Utilities", CategoryTypeEnum.expense),
            ("Rent", CategoryTypeEnum.expense),
            ("Salary", CategoryTypeEnum.income),
            ("Bonus", CategoryTypeEnum.income),
            ("Investments", CategoryTypeEnum.investment),
        ]

        for cat_name, cat_type in default_categories:
            category = Category(
                id=uuid.uuid4(),
                family_id=family.id,
                name=cat_name,
                type=cat_type,
                is_default=True,
            )
            session.add(category)

        session.commit()
        print("✅ Database seeded successfully!")
        print(f"  - Superadmin: superadmin@nestfi.local / admin123")
        print(f"  - Test user 1: alice@example.com / password123")
        print(f"  - Test user 2: bob@example.com / password123")
        print(f"  - Test family: {family.name}")
        print(f"  - Default categories: {len(default_categories)}")

    except Exception as e:
        session.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
