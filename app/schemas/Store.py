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
    product_entity_types: List[Any]

    @validator("product_entity_types")
    def validate_products(cls, products):
        for i in range(len(products)):
            products[i] = products[i].id

        return products

    class Config:
        orm_mode = True

        def schema_extra(schema: Dict[str, Any]) -> None:
            schema["properties"]["product_entity_types"] = {
                "title": "Product Entity Types",
                "type": "array",
                "items": {
                    "type": "integer"
                }
            }
