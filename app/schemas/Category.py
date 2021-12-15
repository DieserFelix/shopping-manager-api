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
    lists: List[Any]
    articles: List[Any]

    @validator("lists")
    def validate_lists(cls, lists):
        for i in range(len(lists)):
            lists[i] = lists[i].id

        return lists

    @validator("articles")
    def validate_products(cls, articles):
        for i in range(len(articles)):
            articles[i] = articles[i].id

        return articles

    class Config:
        orm_mode = True

        def schema_extra(schema: Dict[str, Any]) -> None:
            schema["properties"]["lists"] = {
                "title": "Shopping Lists",
                "type": "array",
                "items": {
                    "type": "integer"
                }
            }
            schema["properties"]["Articles"] = {
                "title": "Articles",
                "type": "array",
                "items": {
                    "type": "integer"
                }
            }
