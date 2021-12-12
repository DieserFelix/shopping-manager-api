from __future__ import annotations
from typing import Any, List
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Boolean, Float, DateTime
from sqlalchemy.orm import Session, relationship
import app.db.models as models


class Store(Base):
    __tablename__ = "Store"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    name: str = Column(Text, nullable=False)

    username: str = Column(String(32), ForeignKey("User.username", ondelete="CASCADE"), nullable=False)

    product_entity_types: List[models.ProductEntityType] = relationship("ProductEntityType", back_populates="store")
    user: models.User = relationship("User", back_populates="stores")