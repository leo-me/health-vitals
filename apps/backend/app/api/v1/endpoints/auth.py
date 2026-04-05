# auth.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session


from app.core.security import create_access_token, verify_password
from app.crud.crud_user import get_user_by_email
from app.db.session import get_db


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post('/login')
def generate_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session=Depends(get_db)):
  user = get_user_by_email(db, form_data.username)

  if not user:
    raise HTTPException(status_code=404, detail='User not found')

  if not verify_password(form_data.password, user.password):
    raise HTTPException(status_code=401, detail='Incorrect password')
  else:
    token = create_access_token({'sub': str(user.id)})
    return {
      'access_token': token,
      'token_type': 'bearer'
    }