from __future__ import annotations
from datetime import datetime
from typing import Any, List
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, func
from sqlalchemy.orm import Session, relationship
import bleach
import app.lib as lib
import app.db.models as models


class Store(Base):
    __tablename__ = "Store"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    name: str = Column(Text, nullable=False)

    created_at: datetime = Column(DateTime)
    updated_at: datetime = Column(DateTime)

    username: str = Column(String(32), ForeignKey("User.username", ondelete="CASCADE"), nullable=False)

    articles: List[models.Article] = relationship("Article", back_populates="store")
    user: models.User = relationship("User", back_populates="stores")

    def __str__(self) -> str:
        return self.name

    def set_name(self, name: Any) -> None:
        name = Store.process_name(name, self.user, self)
        if name != self.name:
            self.name = name
            self.updated_at = datetime.utcnow()

    @staticmethod
    def create(user: models.User) -> Store:
        store = Store()
        store.created_at = datetime.utcnow()
        store.user = user

        return store

    @staticmethod
    def get(store_id: Any, user: models.User, db: Session) -> Store:
        try:
            store_id = int(store_id)
        except:
            raise LookupError(f"Invalid store ID: {store_id}")

        store = db.query(Store).filter(Store.id == store_id).first()
        if store is None:
            raise LookupError(f"No such store: {store_id}")
        if user.role != lib.UserRoles.ADMIN:
            if store not in user.stores:
                raise LookupError(f"No such store: {store_id}")

        return store

    @staticmethod
    def byName(store_name: str, user: models.User, db: Session) -> Store:
        if not isinstance(store_name, str) or not store_name:
            raise LookupError(f"No such store: {store_name}")

        store_name = bleach.clean(store_name.strip(), tags=[])

        store = db.query(Store).filter(func.lower(Store.name) == func.lower(store_name)).first()
        if store is None:
            raise LookupError(f"No such store: {store_name}")
        if user.role != lib.UserRoles.ADMIN:
            if store not in user.stores:
                raise LookupError(f"No such store: {store_name}")

        return store

    @staticmethod
    def find(name: Any, user: models.User) -> List[Store]:
        if not isinstance(name, str) or not name:
            raise ValueError("Invalid name")

        name: str = bleach.clean(name.strip(), tags=[])

        stores: List[Store] = []
        for store in user.stores:
            if name.casefold() in store.name.casefold():
                stores.append(store)

        return stores

    @staticmethod
    def process_name(name: Any, user: models.User, reference: Store) -> str:
        if not isinstance(name, str) or not name:
            raise ValueError("Invalid name")

        name: str = bleach.clean(name.strip(), tags=[])

        names = [store.name.casefold() for store in user.stores if reference != store]
        if name.lower() in names:
            raise ValueError(f"Store {name} already exists")

        return name