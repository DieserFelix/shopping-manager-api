from __future__ import annotations
from typing import Any
from app.db import Base
from app.lib.environment import SALT
from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import Session
import bleach, re, hashlib    

class User(Base):
    __tablename__ = "User"
    
    username: str = Column(String(32), primary_key=True, nullable=False)
    first_name: str = Column(String(64))
    last_name: str = Column(String(64))
    pw_hash: str = Column(Text, nullable=False)
    role: str = Column(Text, nullable=False)
    logged_in: bool = Column(Boolean, default=False)
    
    @staticmethod
    def get(username: Any, db: Session) -> User:
        if not isinstance(username, str) or not username:
            raise ValueError(f"Invalid user name")
        
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise LookupError(f"Could not find user {username}")
        
        return user
    
    @staticmethod
    def process_username(username: Any, db: Session) -> str:
        if not isinstance(username, str) or not username:
            raise ValueError(f"Invalid user name")

        usernames = [u.username for u in db.query(User).all()]
        if username in usernames:
            raise ValueError(f"User name {username} is already used")
        
        if re.match("^[a-zA-Z0-9_]*$", username) is None or len(username) > 32:
            raise ValueError(f"User name must be a string of at most 32 alphanumeric characters")
        
        return username
    
    @staticmethod
    def process_first_name(name: Any) -> str:
        if not isinstance(name, str) or not name:
            raise ValueError(f"Invalid first name")
        
        name = bleach.clean(name, tags=[])
        if len(name) > 64:
            raise ValueError(f"First name cannot be longer than 64 characters")
        
        return name
    
    @staticmethod
    def process_last_name(name: Any) -> str:
        if not isinstance(name, str) or not name:
            raise ValueError(f"Invalid last name")

        name = bleach.clean(name, tags=[])
        if len(name) > 64:
            raise ValueError(f"Last name cannot be longer than 64 characters")
        
        return name
    
    @staticmethod
    def process_password(password: Any) -> str:
        if not isinstance(password, str) or not password:
            raise ValueError(f"Invalid password")

        hash = hashlib.sha512((password + SALT).encode("UTF-8")).hexdigest()
        
        return hash
        

    