from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime
from app.lib.environment import SECRET_KEY
from app.lib import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        expires_at = payload.get("exp")

        from app.db.models import User
        current_user = User.get(username, db)
        if datetime.utcnow() > datetime.fromtimestamp(expires_at):
            current_user.logged_in = False
            db.commit()

        if not current_user.logged_in:
            raise Exception()
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    else:
        return current_user