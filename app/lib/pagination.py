from enum import Enum


class PaginationDefaults(int, Enum):
    FIRST_PAGE = 1
    LIMIT = 20
    ASC = 1


class ArticleColumns(str, Enum):
    NAME = "name"
    UPDATED_AT = "updated_at"


class StoreColumns(str, Enum):
    NAME = "name"
    UPDATED_AT = "updated_at"


class CategoryColumns(str, Enum):
    NAME = "name"
    UPDATED_AT = "updated_at"
