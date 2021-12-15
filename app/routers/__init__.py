# enable automatic setup by importing routers here and collecting them in a list,
# main.py iterates the list and adds each router to the app.
from app.routers.users import users
from app.routers.stores import stores
from app.routers.categories import categories
from app.routers.articles import articles
from app.routers.lists import lists

routers = [users, stores, categories, articles, lists]