from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from app.db.models import User, Brand
from app.lib import get_current_user, get_db, UserRoles
from app.lib.pagination import ArticleColumns, BrandColumns, CategoryColumns, PaginationDefaults
import app.schemas as schemas
from sqlalchemy.orm import Session

brands = APIRouter(
    prefix="/api/brands",
    responses={
        401: dict(description="Brands can only be accessed by logged in users.", model=schemas.HTTPError),
        500: dict(description="Internal server error.", model=schemas.HTTPError)
    },
    tags=["brand"]
)   #yapf:disable

@brands.get(
    "/",
    response_model=List[schemas.Brand],
    responses={
        200: dict(description="List of brands created by the current user, possibly filtered by name."),
        400: dict(description="Invalid name for filter.", model=schemas.HTTPError)
    }
)
def read_brands(
    name: str = None,
    sort_by: CategoryColumns = CategoryColumns.UPDATED_AT,
    page: int = PaginationDefaults.FIRST_PAGE,
    asc: int = PaginationDefaults.ASC,
    limit: int = PaginationDefaults.LIMIT,
    auth_user: User = Depends(get_current_user),
):
    try:
        if page < 1 or limit < 1:
            raise ValueError(f"Invalid pagination parameters")
        page -= 1

        brands: List[Brand]
        if name:
            brands = Brand.find(name, auth_user)
        else:
            brands = auth_user.brands

        brands = sorted(
            brands,
            key=lambda brand: brand.name.casefold() if sort_by == BrandColumns.NAME else brand.updated_at,
            reverse=asc != PaginationDefaults.ASC
        )

        if page * limit >= len(brands):
            []

        brands = brands[page * limit:page * limit + limit]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return brands


@brands.get(
    "/{category_id}",
    response_model=schemas.Brand,
    responses={
        200: dict(description="Brand <brand_id>."),
        404: dict(description="Brand <brand_id> does not exist.", model=schemas.HTTPError)
    }
)
def read_brand(brand_id: int, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        brand = Brand.get(brand_id, auth_user, db)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return brand