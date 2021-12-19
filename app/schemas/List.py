from typing import Any, Dict, Optional
from pydantic import BaseModel
from datetime import datetime


class ListCreate(BaseModel):
    title: str
    category_id: Optional[int]


class ListUpdate(BaseModel):
    id: int
    title: Optional[str]
    category_id: Optional[int]
    finalized: Optional[bool]


class List(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    finalized: bool

    class Config:
        orm_mode = True
