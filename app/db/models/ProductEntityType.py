from __future__ import annotations
from typing import Any, List
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Boolean, Float, DateTime
from sqlalchemy.orm import Session, relationship
import app.db.models as models


class ProductEntityType(Base):
    __tablename__ = "ProductEntityType"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    name: str = Column(Text, nullable=False)
    detail: str = Column(Text, nullable=True)

    store_id: int = Column(Integer, ForeignKey("Store.id"), nullable=True)
    category_id: int = Column(Integer, ForeignKey("Category.id"), nullable=True)

    username: str = Column(String(32), ForeignKey("User.username", ondelete="CASCADE"), nullable=False)

    category: models.Category = relationship("Category", back_populates="product_entity_types", uselist=False)
    store: models.Store = relationship("Store", back_populates="product_entity_types", uselist=False)
    prices: List[models.Price] = relationship("Price", back_populates="product", cascade="all, delete")
    entity_type: models.EntityType = relationship("EntityType", back_populates="product_entity_type", uselist=False)
    user: models.User = relationship("User", back_populates="product_entity_types")