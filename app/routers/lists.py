from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from app.db.models import User, Category
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
        lists = [entity for entity in auth_user.entities if entity.isList() and entity.updated_at >= from_date and entity.updated_at <= to_date]
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
        entity = Entity.get(list_id, auth_user, db)
        if not entity.isList():
            raise LookupError(f"No such entity: {list_id}")
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return entity


def create_list(list: schemas.ListCreate, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:

        current_list = Entity()
        current_list.title = Entity.process_title(list.title)
        current_list.updated_at = datetime.utcnow()

        current_entity_type = EntityType()
        current_list_entity_type = ListEntityType()
        current_list_entity_type.entity_type = current_entity_type

        if list.category_id is not None:
            category = Category.get(list.category_id, auth_user, db)
            current_list_entity_type.category = category

        db.add(current_entity_type)
        db.add(current_list_entity_type)
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


def update_list(list: schemas.ListUpdate, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        current_list = Entity.get(list.id, auth_user, db)
        if not current_list.isList():
            raise LookupError(f"No such entity: {list.id}")

        if list.title is not None:
            current_list.title = Entity.process_title(list.title)
        if list.category_id is not None:
            category = Category.get(list.category_id, auth_user, db)
            current_list.entity_type.list_entity_type.category = category
        if list.finalized is not None:
            current_list.finalized = list.finalized

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


# def delete_list(list_id: int, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     try:
#         current_list = Entity.get(list_id, auth_user, db)
#         if not current_list.isList():
#             raise LookupError(f"No such entity: {list_id}")

#         for child in current_list.children:
#             db.delete(child)

#         db.delete(current_list.entity_type)
#         db.delete(current_list)