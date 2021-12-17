from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import app.routers as routers
from app.lib.environment import CREATE_DATABASE

if CREATE_DATABASE:
    from app.db import Base, engine
    from app.db.models import User, \
                              Article, \
                              Category, Store, Price, \
                              ShoppingList, ShoppingListItem, ShoppingListCost

    Base.metadata.create_all(engine)

app = FastAPI()
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in routers.routers:
    app.include_router(router)

app.openapi_schema = get_openapi(
    title="Shopping Manager API",
    version="1.0",
    description="The Shopping Manager API maintains users, lists and products and their relations.",
    routes=app.routes
)