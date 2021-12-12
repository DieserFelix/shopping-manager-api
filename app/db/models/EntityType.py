from __future__ import annotations
from typing import Any, List
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Boolean, Float, DateTime
from sqlalchemy.orm import Session, relationship
import app.db.models as models


class EntityType(Base):
    __tablename__ = "EntityType"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    list_entity_type_id: int = Column(Integer, ForeignKey("ListEntityType.id", ondelete="CASCADE"), nullable=True)
    product_entity_type_id: int = Column(Integer, ForeignKey("ProductEntityType.id", ondelete="CASCADE"), nullable=True)

    username: str = Column(String(32), ForeignKey("User.username", ondelete="CASCADE"), nullable=False)

    list_entity_type: models.ListEntityType = relationship(
        "ListEntityType", foreign_keys=[list_entity_type_id], back_populates="entity_type", cascade="all, delete"
    )
    product_entity_type: models.ProductEntityType = relationship(
        "ProductEntityType", foreign_keys=[product_entity_type_id], back_populates="entity_type", cascade="all, delete"
    )

    entities: List[models.Entity] = relationship("Entity", back_populates="entity_type", cascade="all, delete")

    user: models.User = relationship("User", back_populates="entity_types")