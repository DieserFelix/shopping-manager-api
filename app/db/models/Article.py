from __future__ import annotations
from datetime import datetime
from typing import Any, List
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, func
from sqlalchemy.orm import Session, relationship
import bleach
import app.lib as lib
import app.db.models as models


class Article(Base):
    __tablename__ = "Article"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    name: str = Column(Text, nullable=False)
    detail: str = Column(Text, nullable=True)

    created_at: datetime = Column(DateTime)
    updated_at: datetime = Column(DateTime)

    store_id: int = Column(Integer, ForeignKey("Store.id"), nullable=True)
    category_id: int = Column(Integer, ForeignKey("Category.id"), nullable=True)

    username: str = Column(String(32), ForeignKey("User.username", ondelete="CASCADE"), nullable=False)

    category: models.Category = relationship("Category", back_populates="articles", uselist=False)
    store: models.Store = relationship("Store", back_populates="articles", uselist=False)
    prices: List[models.Price] = relationship("Price", back_populates="article", cascade="all, delete")
    user: models.User = relationship("User", back_populates="articles")

    instances: List[models.ShoppingListItem] = relationship("ShoppingListItem", back_populates="article", cascade="all, delete")

    def __str__(self) -> str:
        return self.name

    def price(self, at: datetime = None) -> models.Price:
        prices = sorted(self.prices, key=lambda price: price.created_at, reverse=True)
        if at:
            for price in prices:
                if price.created_at <= at:
                    return price
        return prices[0]

    def set_name(self, name: Any, store: models.Store = None) -> None:
        name = Article.process_name(name, self.user, self.name, store)
        if name != self.name:
            self.name = name
            self.updated_at = datetime.utcnow()

    def set_detail(self, detail: Any) -> None:
        detail = Article.process_detail(detail)
        if detail != self.detail:
            self.detail = detail
            self.updated_at = datetime.utcnow()

    def set_store(self, store: models.Store) -> None:
        if store != self.store:
            self.store = store
            self.updated_at = datetime.utcnow()

    def set_category(self, category: models.Category) -> None:
        if category != self.category:
            self.category = category
            self.updated_at = datetime.utcnow()

    @staticmethod
    def get(article_id: Any, user: models.User, db: Session) -> Article:
        try:
            article_id = int(article_id)
        except:
            raise LookupError(f"Invalid article ID: {article_id}")

        article = db.query(Article).filter(Article.id == article_id).first()
        if article is None:
            raise LookupError(f"No such article: {article_id}")
        if user.role != lib.UserRoles.ADMIN:
            if article not in user.articles:
                raise LookupError(f"No such article: {article_id}")

        return article

    @staticmethod
    def byName(article_name: str, user: models.User, db: Session) -> Article:
        if not isinstance(article_name, str) or not article_name:
            raise LookupError(f"No such article: {article_name}")

        article_name = bleach.clean(article_name.strip(), tags=[])

        article = db.query(Article).filter(func.lower(Article.name) == func.lower(article_name)).first()
        if article is None:
            raise LookupError(f"No such article: {article_name}")
        if user.role != lib.UserRoles.ADMIN:
            if article not in user.categories:
                raise LookupError(f"No such article: {article_name}")

        return article

    @staticmethod
    def find(name: Any, user: models.User) -> List[Article]:
        if not isinstance(name, str) or not name:
            raise ValueError("Invalid name")

        name: str = bleach.clean(name.strip(), tags=[])

        products: List[Article] = []
        for product in user.articles:
            if name.casefold() in product.name.casefold():
                products.append(product)

        return products

    @staticmethod
    def process_name(name: Any, user: models.User, current_name: str = None, store: models.Store = None) -> str:
        if not isinstance(name, str) or not name:
            raise ValueError("Invalid name")

        name: str = bleach.clean(name.strip(), tags=[])

        names = [article.name.casefold() for article in user.articles if article.name != current_name and article.store == store]

        if name.casefold() in names:
            raise ValueError(f"Article {name} already exists")

        return name

    @staticmethod
    def process_detail(detail: Any) -> str:
        if not isinstance(detail, str):
            raise ValueError("Invalid article detail")

        detail = bleach.clean(detail, tags=[])

        return detail