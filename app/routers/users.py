from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import Response
from app.db.models import User
from app.lib import create_access_token, get_current_user, get_db, UserRoles
import app.schemas as schemas
from sqlalchemy.orm import Session

users = APIRouter(
    prefix="/api"
)   #yapf:disable

@users.get("/users", response_model=List[schemas.User])
def read_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == UserRoles.ADMIN:
        return db.query(User).all()
    else:
        return [current_user]

@users.post("/login")
def login(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        current_user = User.get(credentials.username, db)
        if current_user.pw_hash != User.process_password(credentials.password):
            raise PermissionError("Invalid password")
        current_user.logged_in = True
        db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return dict(access_token=create_access_token(dict(sub=current_user.username)), token_type="bearer")
    
@users.get(
    "/logout", 
    status_code=204
)
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        current_user.logged_in = False

        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return Response(status_code=204)

@users.post(
    "/users",
    status_code=201,
    response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        current_user = User()
        current_user.username = User.process_username(user.username, db)
        current_user.first_name = User.process_first_name(user.first_name)
        current_user.last_name = User.process_last_name(user.last_name)
        current_user.pw_hash = User.process_password(user.password)
        current_user.role = UserRoles.USER
        
        db.add(current_user)
        db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return current_user
        
@users.put(
    "/users",
    response_model=schemas.User)
def update_user(user: schemas.UserUpdate, auth_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        if user.username != auth_user.username and auth_user.role != UserRoles.ADMIN:
            raise PermissionError("You are not allowed to update users other than yourself")

        current_user = User.get(user.username, db)
        if user.first_name:
            current_user.first_name = User.process_first_name(user.first_name)
        if user.last_name:
            current_user.last_name = User.process_last_name(user.last_name)
        if user.role:
            if auth_user.role != UserRoles.ADMIN:
                raise PermissionError("You are not allowed to update users other than yourself")
            current_user.role = user.role
    
        db.commit()
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return current_user

@users.delete("/users/{username}", status_code=204)
def delete_user(username: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        if user.role != UserRoles.ADMIN:
            raise PermissionError("Only administrators can delete users")
        current_user = User.get(username, db)
        
        db.delete(current_user)
        db.commit()
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return Response(status_code=204)