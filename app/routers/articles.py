from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from app.db.models import Article, Store, Category, Price, User
from app.lib import get_current_user, get_db
import app.schemas as schemas
from sqlalchemy.orm import Session

articles = APIRouter(
    prefix="/api/articles",
    responses={
        401: dict(description="Articles can only be accessed by logged in users.", model=schemas.HTTPError),
        500: dict(description="Internal server error.", model=schemas.HTTPError)
    },
    tags=["article"]
)   #yapf:disable

@articles.get(
    "/",
    response_model=List[schemas.Article],
    responses={200: dict(description="List of articles created by the current user, possibly filtered by name.")}
)
def read_articles(filter: str = None, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        if filter:
            articles = Article.find(filter, auth_user)
        else:
            articles = auth_user.articles
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return articles


@articles.get(
    "/{article_id}",
    response_model=schemas.Article,
    responses={
        200: dict(description="Article <article_id>."),
        404: dict(description="Article <article_id> does not exist.", model=schemas.HTTPError)
    }
)
def read_article(article_id: int, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        article = Article.get(article_id, auth_user, db)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return article


@articles.get(
    "/{article_id}/prices",
    response_model=List[schemas.Price],
    responses={
        200: dict(description="Prices of article <article_id>."),
        404: dict(description="Article <article_id> does not exist.", model=schemas.HTTPError)
    }
)
def read_article_prices(article_id: int, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        article = Article.get(article_id, auth_user, db)
        prices = article.prices
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return prices


@articles.get(
    "/{article_id}/prices",
    response_model=schemas.Price,
    responses={
        200: dict(description="Price of article <article_id> valid at <at>."),
        404: dict(description="Article <article_id> does not exist.", model=schemas.HTTPError)
    }
)
def read_article_price(article_id: int, at: datetime = None, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        article = Article.get(article_id, auth_user, db)
        price = article.price(at)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return price


@articles.post(
    "/",
    status_code=201,
    response_model=schemas.Article,
    responses={
        201: dict(description="Created article."),
        400: dict(description="Input validation failed.", model=schemas.HTTPError)
    }
)
def create_article(article: schemas.ArticleCreate, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        current_article = Article()
        current_article.name = Article.process_name(article.name, auth_user)
        if article.detail is not None:
            current_article.detail = Article.process_detail(article.detail)
        store = Store.get(article.store_id, auth_user, db)
        current_article.store_id = store.id
        category = Category.get(article.category_id, auth_user, db)
        current_article.category_id = category.id
        current_article.username = auth_user.username

        current_price = Price()
        current_price.price = article.price
        current_price.valid_at = datetime.utcnow()
        current_price.currency = "EUR"
        current_price.article = current_article
        current_price.username = auth_user.username

        db.add(current_article)
        db.add(current_price)
        db.commit()
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return current_article


@articles.put(
    "/",
    response_model=schemas.Article,
    responses={
        200: dict(description="Updated article."),
        400: dict(description="Input validation failed.", model=schemas.HTTPError)
    }
)
def update_article(article: schemas.ArticleUpdate, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        current_article = Article.get(article.id, auth_user, db)
        if article.name is not None:
            current_article.name = Article.process_name(article.name, auth_user, current_article.name)
        if article.detail is not None:
            current_article.detail = Article.process_detail(article.detail)
        if article.store_id is not None:
            store = Store.get(article.store_id, auth_user, db)
            current_article.store_id = store.id
        if article.category_id is not None:
            category = Category.get(article.category_id, auth_user, db)
            current_article.category_id = category.id
        if article.price is not None:
            if current_article.price().price != article.price:
                current_price = Price()
                current_price.price = article.price
                current_price.valid_at = datetime.utcnow()
                current_price.currency = "EUR"
                current_price.article = current_article
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
        return current_article


@articles.delete(
    "/{article_id}",
    status_code=204,
    responses={
        204: dict(description="Deleted article."),
        404: dict(description="Article does not exist.", model=schemas.HTTPError)
    }
)
def delete_article(article_id: int, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        current_article = Article.get(article_id, auth_user, db)
        if len(current_article.instances) > 0:
            raise ValueError("There are shopping lists containing this article")

        db.delete(current_article)
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