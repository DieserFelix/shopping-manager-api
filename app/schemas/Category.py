from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from pydantic.class_validators import validator


class CategoryCreate(BaseModel):
    name: str


class CategoryUpdate(BaseModel):
    id: int
    name: Optional[str]


class Category(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
