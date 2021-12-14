from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from app.db.models import ProductEntityType, Store, User
from app.db.models.Category import Category
from app.db.models.EntityType import EntityType
from app.db.models.Price import Price
from app.lib import get_current_user, get_db, UserRoles
import app.schemas as schemas
from sqlalchemy.orm import Session

products = APIRouter(
    prefix="/api/products",
    responses={
        401: dict(description="Products can only be accessed by logged in users.", model=schemas.HTTPError),
        500: dict(description="Internal server error.", model=schemas.HTTPError)
    },
    tags=["product"]
)   #yapf:disable

@products.get(
    "/",
    response_model=List[schemas.Product],
    responses={200: dict(description="List of products created by the current user, possibly filtered by name.")}
)
def read_products(filter: str = None, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        products = auth_user.product_entity_types
        if filter:
            products = ProductEntityType.find(filter, auth_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return products


@products.get(
    "/{product_id}",
    response_model=schemas.Product,
    responses={
        200: dict(description="Product <product_id>."),
        404: dict(description="Product <product_id> does not exist.", model=schemas.HTTPError)
    }
)
def read_product(product_id: int, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        product = ProductEntityType.get(product_id, auth_user, db)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return product


@products.get(
    "/{product_id}/price",
    response_model=schemas.Price,
    responses={
        200: dict(description="Price of product <product_id> valid at <at>."),
        404: dict(description="Product <product_id> does not exist.", model=schemas.HTTPError)
    }
)
def read_product_price(product_id: int, at: datetime = None, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        product = ProductEntityType.get(product_id, auth_user, db)
        price = product.price(at)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return price


@products.post(
    "/",
    status_code=201,
    response_model=schemas.Product,
    responses={
        201: dict(description="Created product."),
        400: dict(description="Input validation failed.", model=schemas.HTTPError)
    }
)
def create_product(product: schemas.ProductCreate, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        current_product = ProductEntityType()
        current_product.name = ProductEntityType.process_name(product.name, auth_user)
        if product.detail is not None:
            current_product.detail = ProductEntityType.process_detail(product.detail)
        store = Store.get(product.store_id, auth_user, db)
        current_product.store_id = store.id
        category = Category.get(product.category_id, auth_user, db)
        current_product.category_id = category.id
        current_product.username = auth_user.username

        current_price = Price()
        current_price.price = product.price
        current_price.valid_at = datetime.utcnow()
        current_price.currency = "EUR"
        current_price.product = current_product
        current_price.username = auth_user.username

        current_entity_type = EntityType()
        current_entity_type.product_entity_type = current_product
        current_entity_type.username = auth_user.username

        db.add(current_product)
        db.add(current_price)
        db.add(current_entity_type)
        db.commit()
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return current_product


@products.put(
    "/",
    response_model=schemas.Product,
    responses={
        200: dict(description="Updated product."),
        400: dict(description="Input validation failed.", model=schemas.HTTPError)
    }
)
def update_product(product: schemas.ProductUpdate, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        current_product = ProductEntityType.get(product.id, auth_user, db)
        if product.name is not None:
            current_product.name = ProductEntityType.process_name(product.name, auth_user, current_product.name)
        if product.detail is not None:
            current_product.detail = ProductEntityType.process_detail(product.detail)
        if product.store_id is not None:
            store = Store.get(product.store_id, auth_user, db)
            current_product.store_id = store.id
        if product.category_id is not None:
            category = Category.get(product.category_id, auth_user, db)
            current_product.category_id = category.id
        if product.price is not None:
            if current_product.price().price != product.price:
                current_price = Price()
                current_price.price = product.price
                current_price.valid_at = datetime.utcnow()
                current_price.currency = "EUR"
                current_price.product = current_product
                current_price.username = auth_user.username
                db.add(current_price)

        db.commit()
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return current_product


@products.delete(
    "/{product_id}",
    status_code=204,
    responses={
        204: dict(description="Deleted product."),
        404: dict(description="Product does not exist.", model=schemas.HTTPError)
    }
)
def delete_product(product_id: int, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        current_product = ProductEntityType.get(product_id, auth_user, db)
        if len(current_product.entity_type.entities) > 0:
            raise ValueError("There are shopping lists containing this product")

        db.delete(current_product.entity_type)
        db.delete(current_product)
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