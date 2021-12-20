from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from app.db.models import Category, User
from app.lib import get_current_user, get_db, UserRoles
from app.lib.pagination import ArticleColumns, CategoryColumns, PaginationDefaults
import app.schemas as schemas
from sqlalchemy.orm import Session

categories = APIRouter(
    prefix="/api/categories",
    responses={
        401: dict(description="Categories can only be accessed by logged in users.", model=schemas.HTTPError),
        500: dict(description="Internal server error.", model=schemas.HTTPError)
    },
    tags=["category"]
)   #yapf:disable

@categories.get(
    "/",
    response_model=List[schemas.Category],
    responses={
        200: dict(description="List of categories created by the current user, possibly filtered by name."),
        400: dict(description="Invalid name for filter.", model=schemas.HTTPError)
    }
)
def read_categories(
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

        categories: List[Category]
        if name:
            categories = Category.find(name, auth_user)
        else:
            categories = auth_user.categories

        categories = sorted(
            categories,
            key=lambda category: category.name.lower() if sort_by == CategoryColumns.NAME else category.updated_at,
            reverse=asc != PaginationDefaults.ASC
        )

        if page * limit >= len(categories):
            raise LookupError(f"Requested page does not exist")

        categories = categories[page * limit:page * limit + limit]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return categories


@categories.get(
    "/{category_id}",
    response_model=schemas.Category,
    responses={
        200: dict(description="Category <category_id>."),
        404: dict(description="Category <category_id> does not exist.", model=schemas.HTTPError)
    }
)
def read_category(category_id: int, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        category = Category.get(category_id, auth_user, db)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return category


# @categories.post(
#     "/",
#     status_code=201,
#     response_model=schemas.Category,
#     responses={
#         201: dict(description="Created category."),
#         400: dict(description="Input validation failed.", model=schemas.HTTPError)
#     }
# )
# def create_category(category: schemas.CategoryCreate, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     try:
#         current_category = Category.create(auth_user)
#         current_category.set_name(category.name)

#         db.add(current_category)
#         db.commit()
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=str(e))
#     else:
#         return current_category

# @categories.put(
#     "/",
#     response_model=schemas.Category,
#     responses={
#         200: dict(description="Updated category."),
#         400: dict(description="Input validation failed.", model=schemas.HTTPError),
#         404: dict(description="Category does not exist.", model=schemas.HTTPError)
#     }
# )
# def update_category(category: schemas.CategoryUpdate, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     try:
#         current_category = Category.get(category.id, auth_user, db)
#         if category.name is not None:
#             current_category.set_name(category.name)

#         db.commit()
#     except LookupError as e:
#         raise HTTPException(status_code=404, detail=str(e))
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=str(e))
#     else:
#         return current_category

# @categories.delete(
#     "/{category_id}",
#     status_code=204,
#     responses={
#         204: dict(description="Deleted cagory."),
#         404: dict(description="Category does not exist.", model=schemas.HTTPError)
#     }
# )
# def delete_category(category_id: int, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     try:
#         current_category = Category.get(category_id, auth_user, db)
#         for lists in current_category.lists:
#             lists.category = None
#         for articles in current_category.articles:
#             articles.category = None

#         db.delete(current_category)
#         db.commit()
#     except LookupError as e:
#         raise HTTPException(status_code=404, detail=str(e))
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=str(e))
#     else:
#         return Response(status_code=204)
