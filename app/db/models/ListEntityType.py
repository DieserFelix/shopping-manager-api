from __future__ import annotations
from typing import Any
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Boolean, Float, DateTime
from sqlalchemy.orm import Session, relationship
import app.db.models as models


class ListEntityType(Base):
    __tablename__ = "ListEntityType"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    category_id: int = Column(Integer, ForeignKey("Category.id"), nullable=True)

    username: str = Column(String(32), ForeignKey("User.username", ondelete="CASCADE"), nullable=False)

    category: models.Category = relationship("Category", back_populates="list_entity_types", uselist=False)

    entity_type: models.EntityType = relationship("EntityType", back_populates="list_entity_type", uselist=False)
    user: models.User = relationship("User", back_populates="list_entity_types")