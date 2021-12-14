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
    list_entity_types: List[Any]
    product_entity_types: List[Any]

    @validator("list_entity_types")
    def validate_lists(cls, lists):
        for i in range(len(lists)):
            lists[i] = lists[i].id

        return lists

    @validator("product_entity_types")
    def validate_products(cls, products):
        for i in range(len(products)):
            products[i] = products[i].id

        return products

    class Config:
        orm_mode = True

        def schema_extra(schema: Dict[str, Any]) -> None:
            schema["properties"]["list_entity_types"] = {
                "title": "List Entity Types",
                "type": "array",
                "items": {
                    "type": "integer"
                }
            }
            schema["properties"]["product_entity_types"] = {
                "title": "Product Entity Types",
                "type": "array",
                "items": {
                    "type": "integer"
                }
            }
