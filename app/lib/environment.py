import os, sys
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(BASE_DIR, ".env"))
sys.path.append(BASE_DIR)

SQLALCHEMY_DATABASE_URL = os.environ["DATABASE_URL"]
CREATE_DATABASE = os.environ["CREATE_DATABASE"] == "true"
SALT = os.environ["SALT"]
SECRET_KEY = os.environ["SECRET_KEY"]