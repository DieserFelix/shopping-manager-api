from typing import Any, Dict, Optional
from pydantic import BaseModel
from datetime import datetime

from pydantic.class_validators import validator


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
    cost: Any

    @validator("cost")
    def validate_cost(cls, cost):
        return {
            "price": cost()["total"],
            "currency": "EUR"
        }

    class Config:
        orm_mode = True

        def schema_extra(schema: Dict[str, Any]) -> None:
            schema["properties"]["cost"] = {
                "title": "Cost",
                "type": "number"
            }
