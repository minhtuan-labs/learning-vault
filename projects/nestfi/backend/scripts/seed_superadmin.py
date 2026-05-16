#!/usr/bin/env python3
"""
Seed script to create initial superadmin account.
Run after database migrations: python scripts/seed_superadmin.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import SessionLocal
from app.models import User
from app.utils.security import hash_password

def seed_superadmin():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.role == "superadmin").first()
        if existing:
            print(f"Superadmin already exists: {existing.email}")
            return

        superadmin = User(
            email="admin@nestfi.local",
            password_hash=hash_password("changeme123"),
            full_name="System Administrator",
            role="superadmin",
            is_active=True
        )
        db.add(superadmin)
        db.commit()
        print(f"✓ Superadmin created: {superadmin.email}")
        print("  Default password: changeme123")
        print("  IMPORTANT: Change this password immediately in production!")

    except Exception as e:
        print(f"✗ Error creating superadmin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_superadmin()
