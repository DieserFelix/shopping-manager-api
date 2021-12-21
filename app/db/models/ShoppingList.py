from __future__ import annotations
from datetime import datetime
from typing import Any, List
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Boolean, DateTime
from sqlalchemy.orm import Session, relationship
import bleach
import app.lib as lib
import app.db.models as models


class ShoppingList(Base):
    __tablename__ = "ShoppingList"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    title: str = Column(Text)
    created_at: datetime = Column(DateTime)
    updated_at: datetime = Column(DateTime)
    finalized: bool = Column(Boolean)

    category_id: int = Column(Integer, ForeignKey("Category.id"), nullable=True)
    category: models.Category = relationship("Category", back_populates="lists")
    username: str = Column(String(32), ForeignKey("User.username", ondelete="CASCADE"), nullable=False)
    user: models.User = relationship("User", back_populates="lists")

    items: List[models.ShoppingListItem] = relationship("ShoppingListItem", back_populates="parent", cascade="all, delete")

    def __str__(self) -> str:
        return self.title

    def filter_items(self, name: str) -> List[models.ShoppingListItem]:
        if not isinstance(name, str) or not name:
            raise ValueError("Invalid name")

        name: str = bleach.clean(name.strip(), tags=[])

        list_items: List[models.ShoppingListItem] = []
        for item in self.items:
            if name.casefold() in item.article.name.casefold():
                list_items.append(item)

        return list_items

    def set_title(self, title: Any) -> None:
        title = ShoppingList.process_title(title)
        if title != self.title:
            self.title = title
            self.updated_at = datetime.utcnow()

    def set_category(self, category: models.Category) -> None:
        if category != self.category:
            self.category = category
            self.updated_at = datetime.utcnow()

    def hasArticle(self, article: models.Article) -> bool:
        for item in self.items:
            if item.article.id == article.id:
                return True
        return False

    def areCostsUpToDate(self) -> bool:
        if not self.costs:
            return False
        for cost in self.costs:
            if cost.created_at != self.updated_at:
                return False
        return True

    def cost(self):
        cost = dict()
        uncategorized_cost: float = 0
        for item in self.items:
            item_cost = item.amount * item.price().price
            if item.article.category:
                if item.article.category.name not in cost.keys():
                    cost[item.article.category.name] = 0
                cost[item.article.category.name] += item_cost
            else:
                uncategorized_cost += item_cost

        cost["uncategorized"] = uncategorized_cost
        cost["total"] = sum([cost[category] for category in cost.keys()])
        return cost

    @staticmethod
    def create(user: models.User) -> ShoppingList:
        shopping_list = ShoppingList()
        shopping_list.created_at = datetime.utcnow()
        shopping_list.user = user

        return shopping_list

    @staticmethod
    def get(list_id: Any, user: models.User, db: Session) -> ShoppingList:
        try:
            list_id = int(list_id)
        except:
            raise LookupError(f"Invalid list ID: {list_id}")

        shopping_list = db.query(ShoppingList).filter(ShoppingList.id == list_id).first()
        if shopping_list is None:
            raise LookupError(f"No such list: {list_id}")
        if user.role != lib.UserRoles.ADMIN:
            if shopping_list not in user.lists:
                raise LookupError(f"No such list: {list_id}")

        return shopping_list

    @staticmethod
    def find(title: Any, user: models.User) -> List[ShoppingList]:
        if not isinstance(title, str) or not title:
            raise ValueError("Invalid name")

        title: str = bleach.clean(title.strip(), tags=[])

        lists: List[ShoppingList] = []
        for list in user.lists:
            if title.casefold() in list.title.casefold():
                lists.append(list)

        return lists

    @staticmethod
    def process_title(title: Any) -> str:
        if not isinstance(title, str) or not title:
            raise ValueError("Shopping list titles cannot be null")

        title = bleach.clean(str(title.strip()), tags=[])
        return title