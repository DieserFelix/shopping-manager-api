# enable automatic setup by importing routers here and collecting them in a list,
# main.py iterates the list and adds each router to the app.
from app.routers.users import users
from app.routers.stores import stores
from app.routers.categories import categories
from app.routers.brands import brands
from app.routers.articles import articles
from app.routers.lists import lists
from app.routers.list_items import list_items

routers = [users, stores, categories, brands, articles, lists, list_items]