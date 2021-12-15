from __future__ import annotations
from typing import Any, List
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text
from sqlalchemy.orm import Session, relationship
import bleach
import app.lib as lib
import app.db.models as models


class Category(Base):
    __tablename__ = "Category"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    name: str = Column(Text, nullable=False)

    username: str = Column(String(32), ForeignKey("User.username", ondelete="CASCADE"), nullable=False)

    lists: List[models.ShoppingList] = relationship("ShoppingList", back_populates="category")
    costs: List[models.ShoppingListCost] = relationship("ShoppingListCost", back_populates="category", cascade="all, delete")
    articles: List[models.Article] = relationship("Article", back_populates="category")
    user: models.User = relationship("User", back_populates="categories")

    def __str__(self) -> str:
        return self.name

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
    def find(name: Any, user: models.User) -> List[Category]:
        if not isinstance(name, str) or not name:
            raise ValueError("Invalid name")

        name: str = bleach.clean(name.strip(), tags=[])

        categories: List[Category] = []
        for category in user.categories:
            if name.lower() in category.name.lower():
                categories.append(category)

        return categories

    @staticmethod
    def process_name(name: Any, user: models.User, current_name: str = None) -> str:
        if not isinstance(name, str) or not name:
            raise LookupError("Invalid name")

        name: str = bleach.clean(name.strip(), tags=[])

        names = [category.name.lower() for category in user.categories if category.name != current_name]
        if name.lower() in names:
            raise LookupError(f"Category {name} already exists")

        return name