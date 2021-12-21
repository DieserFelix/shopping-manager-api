from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from app.db.models import Article, Brand, Store, Category, Price, User
from app.lib import get_current_user, get_db
from app.lib.pagination import ArticleColumns, PaginationDefaults
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
    responses={
        200: dict(description="List of articles created by the current user, possibly filtered by name."),
        400: dict(description="Invalid pagination parameters.", model=schemas.HTTPError),
        404: dict(description="Requested page does not exist.", model=schemas.HTTPError)
    }
)
def read_articles(
    name: str = None,
    sort_by: ArticleColumns = ArticleColumns.UPDATED_AT,
    page: int = PaginationDefaults.FIRST_PAGE,
    asc: int = PaginationDefaults.ASC,
    limit: int = PaginationDefaults.LIMIT,
    auth_user: User = Depends(get_current_user),
):
    try:
        if page < 1 or limit < 1:
            raise ValueError(f"Invalid pagination parameters")
        page -= 1

        articles: List[Article]
        if name:
            articles = Article.find(name, auth_user)
        else:
            articles = auth_user.articles

        articles = sorted(
            articles,
            key=lambda article: article.name.casefold() if sort_by == ArticleColumns.NAME    #yapf:disable
            else article.price().price if sort_by == ArticleColumns.PRICE    #yapf:disable
            else (article.store.name.casefold() if article.store else "") if sort_by == ArticleColumns.STORE    #yapf:disable
            else (article.category.name.casefold() if article.category else "") if sort_by == ArticleColumns.CATEGORY    #yapf:disable
            else (article.brand.name.casefold() if article.brand else "") if sort_by == ArticleColumns.BRAND    #yapf:disable
            else article.updated_at,    #yapf:disable  
            reverse=asc != PaginationDefaults.ASC
        )

        if page * limit >= len(articles):
            articles = []
        else:
            articles = articles[page * limit:page * limit + limit]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
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


import traceback


@articles.post(
    "/",
    status_code=201,
    response_model=schemas.Article,
    responses={
        201: dict(description="Created article."),
        400: dict(description="Input validation failed.", model=schemas.HTTPError),
        404: dict(description="Store or Category does not exist", model=schemas.HTTPError)
    }
)
def create_article(article: schemas.ArticleCreate, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    print(article)
    try:
        current_article = Article.create(auth_user)
        if article.store is not None:
            set_store(current_article, article.store, auth_user, db)
        if article.category is not None:
            set_category(current_article, article.category, auth_user, db)
        if article.brand is not None:
            set_brand(current_article, article.brand, auth_user, db)
        current_article.set_name(article.name)
        if article.detail is not None:
            current_article.set_detail(article.detail)

        current_price = Price.create(auth_user)
        current_price.price = Price.process_price(article.price.price)
        current_price.currency = Price.process_currency(article.price.currency)
        current_price.article = current_article

        db.add(current_article)
        db.add(current_price)
        db.commit()
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        traceback.print_exc(e)
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return current_article


@articles.put(
    "/",
    response_model=schemas.Article,
    responses={
        200: dict(description="Updated article."),
        400: dict(description="Input validation failed.", model=schemas.HTTPError),
        404: dict(description="Article, Store or Category does not exist.", model=schemas.HTTPError)
    }
)
def update_article(article: schemas.ArticleUpdate, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        current_article = Article.get(article.id, auth_user, db)
        if article.store is not None:
            set_store(current_article, article.store, auth_user, db)
            current_article.set_name(current_article.name)
        if article.category is not None:
            set_category(current_article, article.category, auth_user, db)
            current_article.set_name(current_article.name)
        if article.brand is not None:
            set_brand(current_article, article.brand, auth_user, db)
            current_article.set_name(current_article.name)
        if article.name is not None:
            current_article.set_name(article.name)
        if article.detail is not None:
            current_article.set_detail(article.detail)
        if article.price is not None:
            if current_article.price().price != article.price.price:
                current_price = Price.create(auth_user)
                current_price.price = Price.process_price(article.price.price)
                current_price.currency = Price.process_currency(article.price.currency)
                current_price.article = current_article

                db.add(current_price)
                current_article.updated_at = datetime.utcnow()

        db.commit()
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
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
        set_store(current_article, "", auth_user, db)
        set_category(current_article, "", auth_user, db)
        set_brand(current_article, "", auth_user, db)

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


def set_store(article: Article, store_name: str, user: User, db: Session) -> None:
    if store_name:
        try:
            store = Store.byName(store_name, user, db)
        except:
            store = Store.create(user)
            store.set_name(store_name)
    else:
        store = None

    previous_store = article.store
    article.set_store(store)
    if article.store != previous_store and previous_store is not None:
        if len(previous_store.articles) == 0:
            db.delete(previous_store)


def set_category(article: Article, category_name: str, user: User, db: Session) -> None:
    if category_name:
        try:
            category = Category.byName(category_name, user, db)
        except:
            category = Category.create(user)
            category.set_name(category_name)
    else:
        category = None

    previous_category = article.category
    article.set_category(category)
    if article.category != previous_category and previous_category is not None:
        if len(previous_category.articles) == 0:
            db.delete(previous_category)


def set_brand(article: Article, brand_name: str, user: User, db: Session) -> None:
    if brand_name:
        try:
            brand = Brand.byName(brand_name, user, db)
        except:
            brand = Brand.create(user)
            brand.set_name(brand_name)
    else:
        brand = None

    previous_brand = article.brand
    article.set_brand(brand)
    if article.brand != previous_brand and previous_brand is not None:
        if len(previous_brand.articles) == 0:
            db.delete(previous_brand)