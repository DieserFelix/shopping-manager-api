from __future__ import annotations
from datetime import datetime
from typing import Any, List
import bleach
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Boolean, Float, DateTime
from sqlalchemy.orm import Session, relationship
import app.db.models as models
from app.lib.UserRoles import UserRoles


class ProductEntityType(Base):
    __tablename__ = "ProductEntityType"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    name: str = Column(Text, nullable=False)
    detail: str = Column(Text, nullable=True)

    store_id: int = Column(Integer, ForeignKey("Store.id"), nullable=True)
    category_id: int = Column(Integer, ForeignKey("Category.id"), nullable=True)

    username: str = Column(String(32), ForeignKey("User.username", ondelete="CASCADE"), nullable=False)

    category: models.Category = relationship("Category", back_populates="product_entity_types", uselist=False)
    store: models.Store = relationship("Store", back_populates="product_entity_types", uselist=False)
    prices: List[models.Price] = relationship("Price", back_populates="product", cascade="all, delete")
    entity_type: models.EntityType = relationship("EntityType", back_populates="product_entity_type", uselist=False)
    user: models.User = relationship("User", back_populates="product_entity_types")

    def __str__(self) -> str:
        return self.name

    def price(self, at: datetime = None) -> models.Price:
        prices = sorted(self.prices, key=lambda price: price.valid_at, reverse=True)
        if at:
            for price in prices:
                if price.valid_at <= at:
                    return price
                return prices[-1]
        return prices[0]

    @staticmethod
    def get(product_entity_type_id: Any, user: models.User, db: Session) -> ProductEntityType:
        try:
            product_entity_type_id = int(product_entity_type_id)
        except:
            raise LookupError(f"Invalid product ID: {product_entity_type_id}")

        product_entity_type = db.query(ProductEntityType).filter(ProductEntityType.id == product_entity_type_id).first()
        if product_entity_type is None:
            raise LookupError(f"No such product: {product_entity_type_id}")
        if user.role != UserRoles.ADMIN:
            if product_entity_type not in user.product_entity_types:
                raise LookupError(f"No such product: {product_entity_type_id}")

        return product_entity_type

    @staticmethod
    def find(name: Any, user: models.User) -> List[ProductEntityType]:
        if not isinstance(name, str) or not name:
            raise ValueError("Invalid name")

        name: str = bleach.clean(name.strip(), tags=[])

        product_entity_types: List[ProductEntityType] = []
        for product_entity_type in user.product_entity_types:
            if name.lower() in product_entity_type.name.lower():
                product_entity_types.append(product_entity_type)

        return product_entity_types

    @staticmethod
    def process_name(name: Any, user: models.User, current_name: str = None) -> str:
        if not isinstance(name, str) or not name:
            raise ValueError("Invalid name")

        name: str = bleach.clean(name.strip(), tags=[])

        names = [product_entity_type.name.lower() for product_entity_type in user.product_entity_types if product_entity_type.name != current_name]
        if name.lower() in names:
            raise ValueError(f"Product {name} already exists")

        return name

    @staticmethod
    def process_detail(detail: Any) -> str:
        if not isinstance(detail, str):
            raise ValueError("Invalid product detail")

        detail = bleach.clean(detail, tags=[])

        return detail