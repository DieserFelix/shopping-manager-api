from __future__ import annotations
from typing import Any, List

import bleach
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Boolean, Float, DateTime
from sqlalchemy.orm import Session, relationship
import app.db.models as models
from app.lib.UserRoles import UserRoles


class Store(Base):
    __tablename__ = "Store"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    name: str = Column(Text, nullable=False)

    username: str = Column(String(32), ForeignKey("User.username", ondelete="CASCADE"), nullable=False)

    product_entity_types: List[models.ProductEntityType] = relationship("ProductEntityType", back_populates="store")
    user: models.User = relationship("User", back_populates="stores")

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def get(store_id: Any, user: models.User, db: Session) -> Store:
        try:
            store_id = int(store_id)
        except:
            raise LookupError(f"Invalid store ID: {store_id}")

        store = db.query(Store).filter(Store.id == store_id).first()
        if store is None:
            raise LookupError(f"No such store: {store_id}")
        if user.role != UserRoles.ADMIN:
            if store not in user.stores:
                raise LookupError(f"No such store: {store_id}")

        return store

    @staticmethod
    def find(name: Any, user: models.User) -> List[Store]:
        if not isinstance(name, str) or not name:
            raise ValueError("Invalid name")

        name: str = bleach.clean(name.strip(), tags=[])

        stores: List[Store] = []
        for store in user.stores:
            if name.lower() in store.name.lower():
                stores.append(store)

        return stores

    @staticmethod
    def process_name(name: Any, user: models.User, current_name: str = None) -> str:
        if not isinstance(name, str) or not name:
            raise ValueError("Invalid name")

        name: str = bleach.clean(name.strip(), tags=[])

        names = [store.name.lower() for store in user.stores if store.name != current_name]
        if name.lower() in names:
            raise ValueError(f"Store {name} already exists")

        return name