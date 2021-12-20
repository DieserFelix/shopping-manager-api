from __future__ import annotations
from datetime import datetime
from typing import Any
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Float, DateTime
from sqlalchemy.orm import Session, relationship
from app.lib import UserRoles
import app.db.models as models


class ShoppingListItem(Base):
    __tablename__ = "ShoppingListItem"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    article_id: int = Column(Integer, ForeignKey("Article.id", ondelete="CASCADE"), nullable=False)
    amount: float = Column(Float)

    created_at: datetime = Column(DateTime)
    updated_at: datetime = Column(DateTime)

    list_id: int = Column(Integer, ForeignKey("ShoppingList.id", ondelete="CASCADE"), nullable=False)
    username: str = Column(String(32), ForeignKey("User.username", ondelete="CASCADE"), nullable=False)

    article: models.Article = relationship("Article", back_populates="instances")
    user: models.User = relationship("User", back_populates="list_items")

    parent: models.ShoppingList = relationship("ShoppingList", back_populates="items")

    def __str__(self) -> str:
        return f"{self.amount}x{self.article.name}"

    def price(self) -> models.Price:
        return self.article.price(self.parent.updated_at)

    def set_article(self, article: models.Article) -> None:
        if article == self.article:
            self.article = article
            self.updated_at = datetime.utcnow()
            self.parent.updated_at = self.updated_at

    def set_amount(self, amount: Any) -> None:
        amount = ShoppingListItem.process_amount(amount)
        if amount != self.amount:
            self.amount = amount
            self.updated_at = datetime.utcnow()
            self.parent.updated_at = self.updated_at

    def set_list(self, list: models.ShoppingList):
        if list != self.parent:
            self.parent = list
            self.updated_at = datetime.utcnow()
            self.parent.updated_at = self.updated_at

    @staticmethod
    def create(user: models.User) -> ShoppingListItem:
        item = ShoppingListItem()
        item.created_at = datetime.utcnow()
        item.user = user

        return item

    @staticmethod
    def get(item_id: Any, user: models.User, db: Session) -> ShoppingListItem:
        try:
            item_id = int(item_id)
        except:
            raise LookupError(f"Invalid list item ID: {item_id}")

        list_item = db.query(ShoppingListItem).filter(ShoppingListItem.id == item_id).first()
        if list_item is None:
            raise LookupError(f"No list item: {item_id}")
        if user.role != UserRoles.ADMIN:
            if list_item not in user.list_items:
                raise LookupError(f"No such list item: {item_id}")

        return list_item

    @staticmethod
    def process_amount(amount: Any) -> str:
        try:
            amount = float(amount)
            if amount <= 0:
                raise Exception()
        except:
            raise ValueError("Shopping lists cannot contain items less than or equal to 0 times")

        return amount
