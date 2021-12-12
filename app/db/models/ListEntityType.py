from __future__ import annotations
from typing import Any
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Boolean, Float, DateTime
from sqlalchemy.orm import Session


class ListEntityType(Base):
    __tablename__ = "ListEntityType"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    category_id: int = Column(Integer, ForeignKey("Category.id"), nullable=True)

    username: str = Column(String(32), ForeignKey("User.username", ondelete="CASCADE"), nullable=False)