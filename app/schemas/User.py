from typing import Optional
from pydantic import BaseModel

from app.lib import UserRoles

class UserCreate(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    
class UserUpdate(BaseModel):
    username: str
    current_password: Optional[str]
    password: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    role: Optional[UserRoles]
    
    
class User(BaseModel):
    username: str
    pw_hash: str
    first_name: str
    last_name: str
    role: UserRoles
    
    class Config:
        orm_mode = True
