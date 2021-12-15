from __future__ import annotations
from typing import Any, List
from app.db import Base
from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import Session, relationship
import bleach, re, hashlib
import app.db.models as models
import app.lib.environment as env


class User(Base):
    __tablename__ = "User"

    username: str = Column(String(32), primary_key=True, nullable=False)
    first_name: str = Column(String(64))
    last_name: str = Column(String(64))
    pw_hash: str = Column(Text, nullable=False)
    role: str = Column(Text, nullable=False)
    logged_in: bool = Column(Boolean, default=False)

    lists: List[models.ShoppingList] = relationship("ShoppingList", back_populates="user", cascade="all, delete, delete-orphan")
    list_items: List[models.ShoppingListItem] = relationship("ShoppingListItem", back_populates="user", cascade="all, delete, delete-orphan")
    articles: List[models.Article] = relationship("Article", back_populates="user", cascade="all, delete, delete-orphan")
    categories: List[models.Category] = relationship("Category", back_populates="user", cascade="all, delete, delete-orphan")
    stores: List[models.Store] = relationship("Store", back_populates="user", cascade="all, delete, delete-orphan")
    prices: List[models.Price] = relationship("Price", back_populates="user", cascade="all, delete, delete-orphan")

    @staticmethod
    def get(username: Any, db: Session) -> User:
        if not isinstance(username, str) or not username:
            raise ValueError(f"Invalid user name")

        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise LookupError(f"Could not find user {username}")

        return user

    @staticmethod
    def process_username(username: Any, db: Session) -> str:
        if not isinstance(username, str) or not username:
            raise ValueError(f"Invalid user name")

        usernames = [u.username for u in db.query(User).all()]
        if username in usernames:
            raise ValueError(f"User name {username} is already used")

        if re.match("^[a-zA-Z0-9_]*$", username) is None or len(username) > 32:
            raise ValueError(f"User name must be a string of at most 32 alphanumeric characters")

        return username

    @staticmethod
    def process_first_name(name: Any) -> str:
        if not isinstance(name, str) or not name:
            raise ValueError(f"Invalid first name")

        name = bleach.clean(name, tags=[])
        if len(name) > 64:
            raise ValueError(f"First name cannot be longer than 64 characters")

        return name

    @staticmethod
    def process_last_name(name: Any) -> str:
        if not isinstance(name, str) or not name:
            raise ValueError(f"Invalid last name")

        name = bleach.clean(name, tags=[])
        if len(name) > 64:
            raise ValueError(f"Last name cannot be longer than 64 characters")

        return name

    @staticmethod
    def process_password(password: Any) -> str:
        if not isinstance(password, str) or not password:
            raise ValueError(f"Invalid password")

        hash = hashlib.sha512((password + env.SALT).encode("UTF-8")).hexdigest()

        return hash
