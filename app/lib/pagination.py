from enum import Enum


class PaginationDefaults(int, Enum):
    FIRST_PAGE = 1
    LIMIT = 20
    ASC = 1


class ArticleColumns(str, Enum):
    NAME = "name"
    PRICE = "price"
    UPDATED_AT = "updated_at"
    STORE = "store"
    CATEGORY = "category"
    BRAND = "brand"


class StoreColumns(str, Enum):
    NAME = "name"
    UPDATED_AT = "updated_at"


class CategoryColumns(str, Enum):
    NAME = "name"
    UPDATED_AT = "updated_at"


class BrandColumns(str, Enum):
    NAME = "name"
    UPDATED_AT = "updated_at"


class ListColumns(str, Enum):
    TITLE = "title",
    UPDATED_AT = "updated_at"
    FINALIZED = "finalized"
    COST = "cost"
    CATEGORY = "category"


class ListItemColumns(str, Enum):
    NAME = "name",
    UPDATED_AT = "updated_at",
    COST = "cost",
    AMOUNT = "amount"
    STORE = "store"
    CATEGORY = "category"
    BRAND = "brand"
