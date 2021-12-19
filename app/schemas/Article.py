from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from pydantic.class_validators import validator


class Price(BaseModel):
    price: float
    currency: str
    created_at: datetime
    article_id: int

    class Config:
        orm_mode = True


class PriceCreate(BaseModel):
    price: float
    currency: str


class ArticleCreate(BaseModel):
    name: str
    detail: Optional[str]
    category: str
    store: str
    price: PriceCreate


class ArticleUpdate(BaseModel):
    id: int
    name: Optional[str]
    detail: Optional[str]
    store: Optional[str]
    category: Optional[str]
    price: Optional[PriceCreate]


class Article(BaseModel):
    id: int
    name: str
    detail: str
    store: Any
    category: Any
    price: Any
    created_at: datetime
    updated_at: datetime

    @validator("price")
    def validate_price(cls, price):
        return price()

    @validator("store")
    def validate_store(cls, store):
        if store:
            return store.name
        return ""

    @validator("category")
    def validate_category(cls, category):
        if category:
            return category.name
        return ""

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
            schema["properties"]["store"] = {
                "title": "Store",
                "type": "string"
            }
            schema["properties"]["category"] = {
                "title": "Category",
                "type": "string"
            }