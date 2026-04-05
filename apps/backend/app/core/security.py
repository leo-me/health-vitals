from fastapi import HTTPException
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password: str) -> str:
  return pwd_context.hash(password[:72])

def verify_password(plain_password: str, hashed_password: str) -> bool:
  return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
  to_encode = data.copy()
  expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
  to_encode.update({"exp": expire})

  return jwt.encode(
    to_encode,
    settings.SECURITY_KEY,
    algorithm=settings.ALGORITHM
  )


def verify_token(token: str) -> dict:
  try:
    payload = jwt.decode(token, settings.SECURITY_KEY, algorithms=[settings.ALGORITHM])
    return payload
  except JWTError:
    raise HTTPException(status_code=401, detail="Invalid token")
