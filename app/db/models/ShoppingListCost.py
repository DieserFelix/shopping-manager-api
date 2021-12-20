from __future__ import annotations
from datetime import datetime
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
import app.db.models as models


class ShoppingListCost(Base):
    __tablename__ = "ShoppingListCost"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    cost: float = Column(Float)
    category_id: int = Column(Integer, ForeignKey("Category.id", ondelete="CASCADE"), nullable=True)
    list_id: int = Column(Integer, ForeignKey("ShoppingList.id", ondelete="CASCADE"), nullable=False)
    created_at: datetime = Column(DateTime)

    category: models.Category = relationship("Category", back_populates="costs")
    list: models.ShoppingList = relationship("ShoppingList", back_populates="costs")

    @staticmethod
    def create(list: models.ShoppingList) -> ShoppingListCost:
        cost = ShoppingListCost()
        cost.created_at = datetime.utcnow()
        cost.list = list

        return cost