from __future__ import annotations
from typing import Any, List

import bleach
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Boolean, Float, DateTime
from sqlalchemy.orm import Session, relationship
import app.db.models as models
from app.lib.UserRoles import UserRoles


class Category(Base):
    __tablename__ = "Category"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    name: str = Column(Text, nullable=False)

    username: str = Column(String(32), ForeignKey("User.username", ondelete="CASCADE"), nullable=False)

    list_entity_types: List[models.ListEntityType] = relationship("ListEntityType", back_populates="category")
    product_entity_types: List[models.ProductEntityType] = relationship("ProductEntityType", back_populates="category")
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
        if user.role != UserRoles.ADMIN:
            if category not in user.stores:
                raise LookupError(f"No such category: {category_id}")

        return category

    @staticmethod
    def find(name: Any, user: models.User) -> List[Category]:
        if not isinstance(name, str) or not name:
            raise LookupError("Invalid name")

        name = bleach.clean(name, tags=[])

        categories: List[Category] = []
        for category in user.categories:
            if name in category.name:
                categories.append(category)

        return categories

    @staticmethod
    def process_name(name: Any, user: models.User, current_name: str = None) -> str:
        if not isinstance(name, str) or not name:
            raise LookupError("Invalid name")

        name = bleach.clean(name.strip(), tags=[])

        names = [category.name.lower() for category in user.categories if category.name != current_name]
        if name in names:
            raise LookupError(f"Category {name} already exists")

        return name