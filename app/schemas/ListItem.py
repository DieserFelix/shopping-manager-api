from typing import Any, Dict, Optional
from pydantic import BaseModel, validator
from datetime import datetime


class ListItemCreate(BaseModel):
    article_id: int
    amount: float


class ListItemUpdate(BaseModel):
    id: int
    article_id: Optional[int]
    amount: Optional[float]


class ListItem(BaseModel):
    id: int
    list_id: int
    article_id: int
    amount: float
    price: Any
    created_at: datetime
    updated_at: datetime

    @validator("price")
    def validate_price(cls, price):
        price = price()
        return dict(price=price.price, currency=price.currency)

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