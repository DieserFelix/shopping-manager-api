from __future__ import annotations
from typing import Any
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Boolean, Float, DateTime
from sqlalchemy.orm import Session, relationship
import app.db.models as models
from app.lib.UserRoles import UserRoles


class ListEntityType(Base):
    __tablename__ = "ListEntityType"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    category_id: int = Column(Integer, ForeignKey("Category.id"), nullable=True)

    username: str = Column(String(32), ForeignKey("User.username", ondelete="CASCADE"), nullable=False)

    category: models.Category = relationship("Category", back_populates="list_entity_types", uselist=False)

    entity_type: models.EntityType = relationship("EntityType", back_populates="list_entity_type", uselist=False)
    user: models.User = relationship("User", back_populates="list_entity_types")

    @staticmethod
    def get(list_entity_type_id: Any, user: models.User, db: Session) -> ListEntityType:
        try:
            list_entity_type_id = int(list_entity_type_id)
        except:
            raise LookupError(f"Invalid list entity type ID: {list_entity_type_id}")

        list_entity_type = db.query(ListEntityType).filter(ListEntityType.id == list_entity_type_id).first()
        if list_entity_type is None:
            raise LookupError(f"No such list entity type: {list_entity_type_id}")
        if user.role != UserRoles.ADMIN:
            if list_entity_type not in user.list_entity_types:
                raise LookupError(f"No such list entity type: {list_entity_type_id}")

        return list_entity_type