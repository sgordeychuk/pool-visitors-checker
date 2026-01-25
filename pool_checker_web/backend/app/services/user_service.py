from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        return self.db.query(User).filter(User.username == username).first()

    def create(self, user_in: UserCreate) -> User:
        """Create a new user."""
        user = User(
            email=user_in.email,
            username=user_in.username,
            hashed_password=get_password_hash(user_in.password),
            is_active=True,
            is_superuser=False
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_superuser(self, email: str, username: str, password: str) -> User:
        """Create a superuser."""
        user = User(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=True
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User, user_in: UserUpdate) -> User:
        """Update a user."""
        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username or email and password."""
        # Try to find by username first, then by email
        user = self.get_by_username(username)
        if not user:
            user = self.get_by_email(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def delete(self, user: User) -> None:
        """Delete a user."""
        self.db.delete(user)
        self.db.commit()
