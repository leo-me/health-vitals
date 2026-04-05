# dependencies.py

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.crud.crud_user import get_user_by_id
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = verify_token(token)        # decode token，fail raise 401
    user_id = payload.get("sub")        # get user_id
    user = get_user_by_id(db, user_id)  # get user
  
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user