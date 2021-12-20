from __future__ import annotations
from datetime import datetime
from typing import Any, List
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, func
from sqlalchemy.orm import Session, relationship
import bleach
import app.lib as lib
import app.db.models as models


class Brand(Base):
    __tablename__ = "Brand"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    name: str = Column(Text, nullable=False)

    created_at: datetime = Column(DateTime)
    updated_at: datetime = Column(DateTime)

    username: str = Column(String(32), ForeignKey("User.username", ondelete="CASCADE"), nullable=False)

    articles: List[models.Article] = relationship("Article", back_populates="brand")
    user: models.User = relationship("User", back_populates="brands")

    def __str__(self) -> str:
        return self.name

    def set_name(self, name: Any) -> None:
        name = Brand.process_name(name, self.user, self)
        if name != self.name:
            self.name = name
            self.updated_at = datetime.utcnow()

    @staticmethod
    def create(user: models.User) -> Brand:
        store = Brand()
        store.created_at = datetime.utcnow()
        store.user = user

        return store

    @staticmethod
    def get(brand_id: Any, user: models.User, db: Session) -> Brand:
        try:
            brand_id = int(brand_id)
        except:
            raise LookupError(f"Invalid brand ID: {brand_id}")

        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if brand is None:
            raise LookupError(f"No such brand: {brand_id}")
        if user.role != lib.UserRoles.ADMIN:
            if brand not in user.brands:
                raise LookupError(f"No such brand: {brand_id}")

        return brand

    @staticmethod
    def byName(brand_name: str, user: models.User, db: Session) -> Brand:
        if not isinstance(brand_name, str) or not brand_name:
            raise LookupError(f"No such brand: {brand_name}")

        brand_name = bleach.clean(brand_name.strip(), tags=[])

        brand = db.query(Brand).filter(func.lower(Brand.name) == func.lower(brand_name)).first()
        if brand is None:
            raise LookupError(f"No such brand: {brand_name}")
        if user.role != lib.UserRoles.ADMIN:
            if brand not in user.brands:
                raise LookupError(f"No such brand: {brand_name}")

        return brand

    @staticmethod
    def find(name: Any, user: models.User) -> List[Brand]:
        if not isinstance(name, str) or not name:
            raise ValueError("Invalid name")

        name: str = bleach.clean(name.strip(), tags=[])

        brands: List[Brand] = []
        for brand in user.brands:
            if name.casefold() in brand.name.casefold():
                brands.append(brand)

        return brands

    @staticmethod
    def process_name(name: Any, user: models.User, reference: Brand) -> str:
        if not isinstance(name, str) or not name:
            raise ValueError("Invalid name")

        name: str = bleach.clean(name.strip(), tags=[])

        names = [brand.name.casefold() for brand in user.brands if reference != brand]
        if name.lower() in names:
            raise ValueError(f"Brand {name} already exists")

        return name