from __future__ import annotations
from typing import Any, List
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, func
from sqlalchemy.orm import Session, relationship
from datetime import datetime
import bleach
import app.lib as lib
import app.db.models as models


class Category(Base):
    __tablename__ = "Category"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    name: str = Column(Text, nullable=False)
    created_at: datetime = Column(DateTime)
    updated_at: datetime = Column(DateTime)

    username: str = Column(String(32), ForeignKey("User.username", ondelete="CASCADE"), nullable=False)

    lists: List[models.ShoppingList] = relationship("ShoppingList", back_populates="category")
    costs: List[models.ShoppingListCost] = relationship("ShoppingListCost", back_populates="category", cascade="all, delete")
    articles: List[models.Article] = relationship("Article", back_populates="category")
    user: models.User = relationship("User", back_populates="categories")

    def __str__(self) -> str:
        return self.name

    def set_name(self, name: Any) -> None:
        name = Category.process_name(name, self.user, self.name)
        if name != self.name:
            self.name = name
            self.updated_at = datetime.utcnow()

    @staticmethod
    def get(category_id: Any, user: models.User, db: Session) -> Category:
        try:
            category_id = int(category_id)
        except:
            raise LookupError(f"Invalid store ID: {category_id}")

        category = db.query(Category).filter(Category.id == category_id).first()
        if category is None:
            raise LookupError(f"No such category: {category_id}")
        if user.role != lib.UserRoles.ADMIN:
            if category not in user.categories:
                raise LookupError(f"No such category: {category_id}")

        return category

    @staticmethod
    def byName(category_name: str, user: models.User, db: Session) -> Category:
        if not isinstance(category_name, str) or not category_name:
            raise LookupError(f"No such category: {category_name}")

        category_name = bleach.clean(category_name.strip(), tags=[])

        category = db.query(Category).filter(func.lower(Category.name) == func.lower(category_name)).first()
        if category is None:
            raise LookupError(f"No such category: {category_name}")
        if user.role != lib.UserRoles.ADMIN:
            if category not in user.categories:
                raise LookupError(f"No such category: {category_name}")

        return category

    @staticmethod
    def find(name: Any, user: models.User) -> List[Category]:
        if not isinstance(name, str) or not name:
            raise ValueError("Invalid name")

        name: str = bleach.clean(name.strip(), tags=[])

        categories: List[Category] = []
        for category in user.categories:
            if name.casefold() in category.name.casefold():
                categories.append(category)

        return categories

    @staticmethod
    def process_name(name: Any, user: models.User, current_name: str = None) -> str:
        if not isinstance(name, str) or not name:
            raise LookupError("Invalid name")

        name: str = bleach.clean(name.strip(), tags=[])

        names = [category.name.casefold() for category in user.categories if category.name != current_name]
        if name.casefold() in names:
            raise LookupError(f"Category {name} already exists")

        return name