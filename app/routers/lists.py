from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from app.db.models import User, Category, ShoppingList, ShoppingListCost
from app.lib import get_current_user, get_db, UserRoles
import app.schemas as schemas
from sqlalchemy.orm import Session

lists = APIRouter(
    prefix="/api/lists",
    responses={
        401: dict(description="Lists can only be accessed by logged in users.", model=schemas.HTTPError),
        500: dict(description="Internal server error.", model=schemas.HTTPError)
    },
    tags=["list"]
)   #yapf:disable

@lists.get(
    "/",
    response_model=List[schemas.List],
    responses={200: dict(description="List of shopping lists created by the current user, possibly filtered by date.")}
)
def read_lists(from_date: datetime = None, to_date: datetime = None, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        if not from_date:
            from_date = datetime.min
        if not to_date:
            to_date = datetime.max
        lists = [list for list in auth_user.lists if list.updated_at >= from_date and list.updated_at <= to_date]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return lists


@lists.get(
    "/{list_id}",
    response_model=schemas.List,
    responses={
        200: dict(description="Shopping list <list_id>."),
        404: dict(description="Shopping list <list_id> does not exist.", model=schemas.HTTPError)
    }
)
def read_list(list_id: int, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        list = ShoppingList.get(list_id, auth_user, db)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return list


@lists.get(
    "/{list_id}/costs",
    responses={
        200: dict(description="Costs of shopping list <list_id>. Total and by category."),
        404: dict(description="Shopping list <list_id> does not exist.", model=schemas.HTTPError)
    }
)
def read_list_costs(list_id: int, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        list = ShoppingList.get(list_id, auth_user, db)
        if list.areCostsUpToDate():
            costs = dict()
            for cost in list.costs:
                if cost.category:
                    costs[cost.category.id] = cost.cost
                else:
                    costs["total"] = cost.cost
        else:
            for cost in list.costs:
                db.delete(cost)
            costs = list.cost()
            for category_id, cost in costs.items():
                if category_id == "total":
                    category_id = None
                current_cost = ShoppingListCost.create(list)
                current_cost.cost = cost
                current_cost.category_id = category_id
                db.add(current_cost)
            db.commit()

    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return costs


@lists.post(
    "/",
    response_model=schemas.List,
    status_code=201,
    responses={
        201: dict(description="Shopping list <list_id>."),
        400: dict(description="Input validation failed.", model=schemas.HTTPError),
        404: dict(description="Shopping list <list_id> does not exist.", model=schemas.HTTPError)
    }
)
def create_list(list: schemas.ListCreate, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        current_list = ShoppingList.create(auth_user)
        current_list.set_title(list.title)
        if list.category_id is not None:
            category = Category.get(list.category_id, auth_user, db)
            current_list.set_category(category)
        current_list.finalized = False

        db.add(current_list)
        db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return current_list


@lists.put(
    "/",
    response_model=schemas.List,
    responses={
        200: dict(description="Shopping list <list_id>."),
        400: dict(description="Input validation failed.", model=schemas.HTTPError),
        404: dict(description="Shopping list <list_id> does not exist.", model=schemas.HTTPError)
    }
)
def update_list(list: schemas.ListUpdate, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        current_list = ShoppingList.get(list.id, auth_user, db)
        if list.title is not None:
            current_list.set_title(list.title)
        if list.category_id is not None:
            category = Category.get(list.category_id, auth_user, db)
            current_list.set_category(category)
        if list.finalized is not None:
            current_list.finalized = list.finalized
            current_list.updated_at = datetime.utcnow()

        db.commit()
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return current_list


@lists.delete(
    "/{list_id}",
    status_code=204,
    responses={
        204: dict(description="Deleted shopping list <list_id>."),
        404: dict(description="Shopping list <list_id> does not exist.", model=schemas.HTTPError)
    }
)
def delete_list(list_id: int, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        current_list = ShoppingList.get(list_id, auth_user, db)

        db.delete(current_list)
        db.commit()
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return Response(status_code=204)