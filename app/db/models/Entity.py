from __future__ import annotations
from typing import Any
from app.db import Base
from sqlalchemy import Table, Column, Integer, ForeignKey, String, Text, Boolean, Float, DateTime
from sqlalchemy.orm import Session
from datetime import datetime

entity_entity_map = Table(
    "EntityHierarchy", Base.metadata,
    Column("parent_id", Integer, ForeignKey("Entity.id", ondelete="CASCADE")),
    Column("child_id", Integer, ForeignKey("Entity.id", ondelete="CASCADE"))
)   #yapf: disable

class Entity(Base):
    __tablename__ = "Entity"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    # attributes for shopping list items
    amount: float = Column(Float)

    # attributes for shopping lists
    title: str = Column(Text)
    updated_at: datetime = Column(DateTime)
    finalized: bool = Column(Boolean)

    entity_type_id: int = Column(Integer, ForeignKey("EntityType.id", ondelete="CASCADE"), nullable=False)
    username: str = Column(String(32), ForeignKey("User", ondelete="CASCADE"), nullable=False)
