from __future__ import annotations
from typing import Any
from app.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Boolean, Float, DateTime
from sqlalchemy.orm import Session


class Category(Base):
    __tablename__ = "Category"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    name: str = Column(Text, nullable=False)

    username: str = Column(String(32), ForeignKey("User.username", ondelete="CASCADE"), nullable=False)