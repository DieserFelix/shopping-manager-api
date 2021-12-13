from __future__ import annotations
from typing import Any, List
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Boolean, Float, DateTime
from sqlalchemy.orm import Session, relationship
import app.db.models as models
from app.lib.UserRoles import UserRoles


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

    def isListType(self) -> bool:
        if self.list_entity_type is not None:
            return True
        return False

    @staticmethod
    def get(entity_type_id: Any, user: models.User, db: Session) -> EntityType:
        try:
            entity_type_id = int(entity_type_id)
        except:
            raise LookupError(f"Invalid entity type ID: {entity_type_id}")

        entity_type = db.query(EntityType).filter(EntityType.id == entity_type_id).first()
        if entity_type is None:
            raise LookupError(f"No such entity type: {entity_type_id}")
        if user.role != UserRoles.ADMIN:
            if entity_type not in user.entity_types:
                raise LookupError(f"No such entity type: {entity_type_id}")

        return entity_type