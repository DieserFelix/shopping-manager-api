from __future__ import annotations
from typing import Any
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Boolean, Float, DateTime
from sqlalchemy.orm import Session


class EntityType(Base):
    __tablename__ = "EntityType"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    list_entity_type_id: int = Column(Integer, ForeignKey("ListEntityType", ondelete="CASCADE"), nullable=True)
    product_entity_type_id: int = Column(Integer, ForeignKey("ProductEntityType.id", ondelete="CASCADE"), nullable=True)

    username: str = Column(String(32), ForeignKey("User.username", ondelete="CASCADE"), nullable=False)