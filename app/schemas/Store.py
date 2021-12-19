from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from pydantic.class_validators import validator


class StoreCreate(BaseModel):
    name: str


class StoreUpdate(BaseModel):
    id: int
    name: Optional[str]


class Store(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
