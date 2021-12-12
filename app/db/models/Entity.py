from __future__ import annotations
from typing import Any, List
from app.db import Base
from sqlalchemy import Table, Column, Integer, ForeignKey, String, Text, Boolean, Float, DateTime
from sqlalchemy.orm import Session, relationship, foreign
from datetime import datetime

import app.db.models as models

entity_hierarchy = Table(
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
    username: str = Column(String(32), ForeignKey("User.username", ondelete="CASCADE"), nullable=False)

    parents: List[Entity] = relationship(
        "Entity",
        secondary=lambda: entity_hierarchy,
        secondaryjoin=id == foreign(entity_hierarchy.c.parent_id),
        foreign_keys=entity_hierarchy.c.child_id,
        back_populates="children"
    )   #yapf: disable
    children: List[Entity] = relationship(
        "Entity",
        secondary=lambda: entity_hierarchy,
        secondaryjoin=id == foreign(entity_hierarchy.c.child_id),
        foreign_keys=entity_hierarchy.c.parent_id,
        back_populates="parents"
    )   #yapf: disable

    entity_type: models.EntityType = relationship("EntityType", back_populates="entities")

    user: models.User = relationship("User", back_populates="entities")
