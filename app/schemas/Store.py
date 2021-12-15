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
    articles: List[Any]

    @validator("articles")
    def validate_articles(cls, articles):
        for i in range(len(articles)):
            articles[i] = articles[i].id

        return articles

    class Config:
        orm_mode = True

        def schema_extra(schema: Dict[str, Any]) -> None:
            schema["properties"]["articles"] = {
                "title": "Articles",
                "type": "array",
                "items": {
                    "type": "integer"
                }
            }
