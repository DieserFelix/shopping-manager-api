from typing import Optional
from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    detail: Optional[str]
    category_id: int
    store_id: int
    price: float


class ProductUpdate(BaseModel):
    id: int
    name: Optional[str]
    detail: Optional[str]
    store_id: Optional[int]
    category_id: Optional[int]
    price: Optional[float]


class Product(BaseModel):
    id: int
    name: str
    detail: str
    store_id: int

    class Config:
        orm_mode = True


class Price(BaseModel):
    price: float
    currency: str

    class Config:
        orm_mode = True
