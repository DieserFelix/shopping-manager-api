from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from app.db.models import Store, User
from app.lib import get_current_user, get_db, UserRoles
from app.lib.pagination import PaginationDefaults, StoreColumns
import app.schemas as schemas
from sqlalchemy.orm import Session

stores = APIRouter(
    prefix="/api/stores",
    responses={
        401: dict(description="Stores can only be accessed by logged in users.", model=schemas.HTTPError),
        500: dict(description="Internal server error.", model=schemas.HTTPError)
    },
    tags=["store"]
)   #yapf:disable

@stores.get(
    "/",
    response_model=List[schemas.Store],
    responses={
        200: dict(description="List of stores created by the current user, possibly filtered by name."),
        400: dict(description="Invalid name for filter.", model=schemas.HTTPError)
    }
)
def read_stores(
    name: str = None,
    sort_by: StoreColumns = StoreColumns.UPDATED_AT,
    page: int = PaginationDefaults.FIRST_PAGE,
    asc: int = PaginationDefaults.ASC,
    limit: int = PaginationDefaults.LIMIT,
    auth_user: User = Depends(get_current_user),
):
    try:
        if page < 1 or limit < 1:
            raise ValueError(f"Invalid pagination parameters")
        page -= 1

        stores: List[Store]
        if name:
            stores = Store.find(name, auth_user)
        else:
            stores = auth_user.stores

        stores = sorted(
            stores, key=lambda store: store.name.lower() if sort_by == StoreColumns.NAME else store.updated_at, reverse=asc != PaginationDefaults.ASC
        )

        if page * limit >= len(stores):
            stores = []
        else:
            stores = stores[page * limit:page * limit + limit]
        print([store.name for store in stores])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return stores


@stores.get(
    "/{store_id}",
    response_model=schemas.Store,
    responses={
        200: dict(description="Store <store_id>."),
        404: dict(description="Store <store_id> does not exist.", model=schemas.HTTPError)
    }
)
def read_store(store_id: int, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        store = Store.get(store_id, auth_user, db)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return store


@stores.post(
    "/",
    status_code=201,
    response_model=schemas.Store,
    responses={
        201: dict(description="Created store."),
        400: dict(description="Input validation failed.", model=schemas.HTTPError)
    }
)
def create_store(store: schemas.StoreCreate, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        current_store = Store()
        current_store.name = Store.process_name(store.name, auth_user)
        current_store.username = auth_user.username

        current_store.created_at = datetime.utcnow()
        current_store.updated_at = datetime.utcnow()

        db.add(current_store)
        db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return current_store


@stores.put(
    "/",
    response_model=schemas.Store,
    responses={
        200: dict(description="Updated store."),
        400: dict(description="Input validation failed.", model=schemas.HTTPError),
        404: dict(description="Store does not exist.", model=schemas.HTTPError)
    }
)
def update_store(store: schemas.StoreUpdate, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        current_store = Store.get(store.id, auth_user, db)
        if store.name is not None:
            current_store.name = Store.process_name(store.name, auth_user, current_store.name)

        current_store.updated_at = datetime.utcnow()

        db.commit()
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return current_store


@stores.delete(
    "/{store_id}",
    status_code=204,
    responses={
        204: dict(description="Deleted store."),
        404: dict(description="Store does not exist.", model=schemas.HTTPError)
    }
)
def delete_store(store_id: int, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        current_store = Store.get(store_id, auth_user, db)
        for store in current_store.articles:
            store.store = None

        db.delete(current_store)
        db.commit()
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return Response(status_code=204)
