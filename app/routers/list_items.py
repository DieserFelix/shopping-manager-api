from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from app.db.models import User, ShoppingList, ShoppingListItem, Article
from app.lib import get_current_user, get_db, UserRoles
import app.schemas as schemas
from sqlalchemy.orm import Session

list_items = APIRouter(
    prefix="/api/lists/{list_id}/items",
    responses={
        401: dict(description="List items can only be accessed by logged in users.", model=schemas.HTTPError),
        500: dict(description="Internal server error.", model=schemas.HTTPError)
    },
    tags=["list item"]
)   #yapf:disable

@list_items.get(
    "/",
    response_model=List[schemas.ListItem],
    responses={
        200: dict(description="Items of shopping list <list_id>."),
        404: dict(description="Shopping list <list_id> does not exist.", model=schemas.HTTPError)
    }
)
def read_items(list_id: int, sort_by: str = None, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        current_list = ShoppingList.get(list_id, auth_user, db)
        items = current_list.items
        if sort_by == "name":
            items = sorted(items, key=lambda item: item.article.name)
        elif sort_by == "category":
            items = sorted(items, key=lambda item: item.article.category.name)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return items


@list_items.get(
    "/{item_id}",
    response_model=schemas.ListItem,
    responses={
        200: dict(description="Item <item_id> of shopping list <list_id>."),
        404: dict(description="Shopping list <list_id> or item <item_id> does not exist.", model=schemas.HTTPError)
    }
)
def read_items(list_id: int, item_id: int, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        current_list = ShoppingList.get(list_id, auth_user, db)
        current_item = ShoppingListItem.get(item_id, auth_user, db)
        if current_item not in current_list.items:
            raise LookupError(f"Item {item_id} is not an item of shopping list {list_id}.")
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return current_item


@list_items.post(
    "/",
    response_model=schemas.ListItem,
    status_code=201,
    responses={
        201: dict(description="Created shopping list item."),
        400: dict(description="Input validation failed.", model=schemas.HTTPError),
        404: dict(description="Shopping list <list_id> or article does not exist.", model=schemas.HTTPError)
    }
)
def create_item(list_id: int, item: schemas.ListItemCreate, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        list = ShoppingList.get(list_id, auth_user, db)
        if list.finalized:
            raise ValueError(f"Item cannot be added to finalized list {list_id}.")
        article = Article.get(item.article_id, auth_user, db)
        if list.hasArticle(article):
            raise ValueError(f"Shopping list {list.id} already contains article {article.name}")
        current_item = ShoppingListItem()
        current_item.created_at = datetime.utcnow()
        current_item.user = auth_user
        current_item.set_list(list)
        current_item.set_article(article)
        current_item.set_amount(item.amount)

        list.updated_at = datetime.utcnow()
        db.add(current_item)
        db.commit()
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return current_item


@list_items.put(
    "/",
    response_model=schemas.ListItem,
    responses={
        200: dict(description="Updated shopping list item."),
        400: dict(description="Input validation failed.", model=schemas.HTTPError),
        404: dict(description="Shopping list <list_id>, item or article does not exist.", model=schemas.HTTPError)
    }
)
def update_item(list_id: int, item: schemas.ListItemUpdate, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        list = ShoppingList.get(list_id, auth_user, db)
        if list.finalized:
            raise ValueError(f"Items of finalized list {list_id} cannot be updated.")
        current_item = ShoppingListItem.get(item.id, auth_user, db)
        if item.article_id is not None:
            article = Article.get(item.article_id, auth_user, db)
            if list.hasArticle(article):
                raise ValueError(f"Shopping list {list.id} already contains article {article.name}")
            current_item.set_article(article)
        if item.amount is not None:
            current_item.set_amount(item.amount)

        db.commit()
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return current_item


@list_items.delete(
    "/{item_id}",
    status_code=204,
    responses={
        204: dict(description="Deleted shopping list item."),
        404: dict(description="Shopping list <list_id> or item <item_id> does not exist.", model=schemas.HTTPError)
    }
)
def delete_item(list_id: int, item_id: int, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        list = ShoppingList.get(list_id, auth_user, db)
        if list.finalized:
            raise ValueError(f"Items of finalized list {list_id} cannot be deleted. Delete list instead.")
        current_item = ShoppingListItem.get(item_id, auth_user, db)
        current_item.parent.updated_at = datetime.utcnow()

        db.delete(current_item)
        db.commit()
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return Response(status_code=204)
