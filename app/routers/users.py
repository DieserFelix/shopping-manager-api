from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic.errors import DecimalIsNotFiniteError
from starlette.responses import Response
from app.db.models import User
from app.lib import create_access_token, get_current_user, get_db, UserRoles
import app.schemas as schemas
from sqlalchemy.orm import Session

users = APIRouter(
    prefix="/api",
    responses={
        500: dict(description="Internal server error.", model=schemas.HTTPError)
    }
)   #yapf:disable

@users.get(
    "/users",
    response_model=List[schemas.User],
    responses={
        200: dict(description="List of users. USER role only sees their own entry. ADMIN role sees all entries."),
    }
)
def read_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        users: List[User]
        if current_user.role == UserRoles.ADMIN:
            users = db.query(User).all()
        else:
            users = [current_user]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return users


@users.post(
    "/login",
    response_model=schemas.Token,
    responses={
        200: dict(description="Authorization successful. Access token granted for user."),
        400: dict(description="Input validation failed.", model=schemas.HTTPError),
        403: dict(description="Invalid password for user.", model=schemas.HTTPError),
        404: dict(description="User does not exist.", model=schemas.HTTPError)
    }
)
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
    status_code=204,
    responses={
        204: dict(description="User was logged out.")
    }
)   #yapf:disable
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
    response_model=schemas.User,
    responses={
        201: dict(description="Created user."),
        400: dict(description="Input validation failed.", model=schemas.HTTPError)
    }
)
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
    response_model=schemas.User,
    responses={
        200: dict(description="Updated user."),
        400: dict(description="Input validation failed.", model=schemas.HTTPError),
        403: dict(description="User update failed due to missing privileges.", model=schemas.HTTPError),
        404: dict(description="User does not exist.", model=schemas.HTTPError)
    }
)
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


@users.delete(
    "/users/{username}",
    status_code=204,
    responses={
        204: dict(description="Deleted user."),
        400: dict(description="Input validation failed.", model=schemas.HTTPError),
        403: dict(description="User deletion failed due to missing privileges.", model=schemas.HTTPError),
        404: dict(description="User does not exist.", model=schemas.HTTPError)
    }
)
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