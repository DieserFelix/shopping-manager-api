from __future__ import annotations
from typing import Any, List

import bleach
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Boolean, Float, DateTime
from sqlalchemy.orm import Session, relationship
from datetime import datetime
import app.db.models as models
from app.lib.UserRoles import UserRoles


class Price(Base):
    __tablename__ = "Price"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    price: float = Column(Float, nullable=False)
    created_at: datetime = Column(DateTime)
    currency: str = Column(String(32), nullable=False)

    article_id: int = Column(Integer, ForeignKey("Article.id", ondelete="CASCADE"), nullable=False)
    username: str = Column(String(32), ForeignKey("User.username", ondelete="CASCADE"), nullable=False)

    article: models.Article = relationship("Article", back_populates="prices", uselist=False)
    user: models.User = relationship("User", back_populates="prices")

    def __str__(self) -> str:
        return str(self.price)

    @staticmethod
    def create(user: models.User) -> Price:
        price = Price()
        price.created_at = datetime.utcnow()
        price.user = user

        return price

    @staticmethod
    def get(price_id: Any, user: models.User, db: Session) -> Price:
        try:
            price_id = int(price_id)
        except:
            raise LookupError(f"Invalid price ID: {price_id}")

        price = db.query(Price).filter(Price.id == price_id).first()
        if price is None:
            raise LookupError(f"No such price: {price_id}")
        if user.role != UserRoles.ADMIN:
            if price not in user.prices:
                raise LookupError(f"No such price: {price_id}")

        return price

    @staticmethod
    def process_price(price: Any) -> str:
        try:
            price = float(price)
            if price <= 0:
                raise Exception()
        except:
            raise ValueError("Prices cannot be less than or equal to 0")

        return price

    @staticmethod
    def process_currency(currency: Any) -> str:
        if not isinstance(currency, str) or not currency:
            raise ValueError("Invalid currency")

        currency = bleach.clean(currency, tags=[])
        return currency