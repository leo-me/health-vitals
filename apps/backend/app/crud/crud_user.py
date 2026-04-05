# from base import CRUDBase

# class CRUDUser(CRUDBase):
#     pass                                 # ← 通用操作全部继承

# crud_user = CRUDUser(User)              # ← 传入 model 就够了
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from uuid import UUID
from app.core.security import hash_password


def get_user_by_id(db: Session, user_id: UUID) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, user_email: str) -> User:
    return db.query(User).filter(User.email == user_email).first()


def create_user(db: Session, data: UserCreate) -> User:
    existing = get_user_by_email(db, data.email)
    if existing:
        raise ValueError("Email already registered")

    user = User(
        email = data.email,
        password=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: UUID) -> bool:
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True



def update_user(db: Session, user_id: UUID, data: UserUpdate) -> User | None:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    for key, val in data.model_dump(exclude_none=True).items():
        setattr(user, key, val)
    db.commit()
    db.refresh(user)
    return user
