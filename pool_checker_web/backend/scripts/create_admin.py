#!/usr/bin/env python3
"""Script to create an admin user."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.services.user_service import UserService
from app.config import settings


def create_admin():
    """Create an admin user if it doesn't exist."""
    db = SessionLocal()
    try:
        service = UserService(db)

        # Check if admin already exists
        existing_user = service.get_by_email(settings.ADMIN_EMAIL)
        if existing_user:
            print(f"Admin user with email {settings.ADMIN_EMAIL} already exists")
            return

        existing_username = service.get_by_username(settings.ADMIN_USERNAME)
        if existing_username:
            print(f"User with username {settings.ADMIN_USERNAME} already exists")
            return

        # Create the admin user
        admin = service.create_superuser(
            email=settings.ADMIN_EMAIL,
            username=settings.ADMIN_USERNAME,
            password=settings.ADMIN_PASSWORD
        )

        print(f"Admin user created successfully:")
        print(f"  Email: {admin.email}")
        print(f"  Username: {admin.username}")
        print(f"  ID: {admin.id}")

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
