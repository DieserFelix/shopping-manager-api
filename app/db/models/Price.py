from __future__ import annotations
from typing import Any
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Boolean, Float, DateTime
from sqlalchemy.orm import Session
from datetime import datetime


class Price(Base):
    __tablename__ = "Price"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    price: float = Column(Float, nullable=False)
    valid_at: datetime = Column(DateTime)
    currency: str = Column(String(32), nullable=False)

    product_id: int = Column(Integer, ForeignKey("ProductEntityType.id", ondelete="CASCADE"), nullable=False)
    username: str = Column(String(32), ForeignKey("User.username", ondelete="CASCADE"), nullable=False)