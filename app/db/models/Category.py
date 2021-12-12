from __future__ import annotations
from typing import Any, List
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Boolean, Float, DateTime
from sqlalchemy.orm import Session, relationship
import app.db.models as models


class Category(Base):
    __tablename__ = "Category"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    name: str = Column(Text, nullable=False)

    username: str = Column(String(32), ForeignKey("User.username", ondelete="CASCADE"), nullable=False)

    list_entity_types: List[models.ListEntityType] = relationship("ListEntityType", back_populates="category")
    product_entity_types: List[models.ProductEntityType] = relationship("ProductEntityType", back_populates="category")
    user: models.User = relationship("User", back_populates="categories")