from __future__ import annotations
from typing import Any, List
from app.db import Base
from sqlalchemy import Table, Column, Integer, ForeignKey, String, Text, Boolean, Float, DateTime
from sqlalchemy.orm import Session, relationship, foreign
from datetime import datetime
from app.lib import UserRoles
import app.db.models as models
import bleach

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

    def __str__(self) -> str:
        if self.isList():
            return self.title
        return f"{self.amount} {self.entity_type.product_entity_type.name}"

    def isList(self) -> bool:
        if self.title:
            return True
        return False

    def hasItem(self, entity: Entity) -> bool:
        if self.isList():
            for child in self.children:
                if child.entity_type_id == entity.entity_type_id:
                    return True
        return False

    @staticmethod
    def get(entity_id: Any, user: models.User, db: Session) -> Entity:
        try:
            entity_id = int(entity_id)
        except:
            raise LookupError(f"Invalid entity ID: {entity_id}")

        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if entity is None:
            raise LookupError(f"No such entity: {entity_id}")
        if user.role != UserRoles.ADMIN:
            if entity not in user.entities:
                raise LookupError(f"No such entity: {entity_id}")

        return entity

    @staticmethod
    def process_title(title: Any) -> str:
        if not isinstance(title, str) or not title:
            raise ValueError("Shopping list titles cannot be null")

        title = bleach.clean(str(title), tags=[])
        return title

    @staticmethod
    def process_amount(amount: Any) -> str:
        try:
            amount = float(amount)
            if amount <= 0:
                raise Exception()
        except:
            raise ValueError("Shopping lists cannot contain items less than or equal to 0 times")

        return amount
