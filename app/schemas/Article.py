from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from pydantic.class_validators import validator


class Price(BaseModel):
    price: float
    currency: str
    valid_at: datetime
    article_id: int

    class Config:
        orm_mode = True


class ArticleCreate(BaseModel):
    name: str
    detail: Optional[str]
    category_id: int
    store_id: int
    price: Price


class ArticleUpdate(BaseModel):
    id: int
    name: Optional[str]
    detail: Optional[str]
    store_id: Optional[int]
    category_id: Optional[int]
    price: Optional[Price]


class Article(BaseModel):
    id: int
    name: str
    detail: str
    store_id: int
    category_id: int
    price: Any

    @validator("price")
    def validate_price(cls, price):
        return price()

    class Config:
        orm_mode = True

        def schema_extra(schema: Dict[str, Any]) -> None:
            schema["properties"]["price"] = {
                "title": "Price",
                "type": "object",
                "properties": {
                    "price": {
                        "title": "Price",
                        "type": "number"
                    },
                    "currency": {
                        "title": "Currency",
                        "type": "string"
                    }
                }
            }