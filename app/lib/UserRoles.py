from enum import Enum

class UserRoles(str, Enum):
    USER = "user"
    ADMIN = "admin"