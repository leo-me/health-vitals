from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlalchemy.orm import Session

from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.db.session import get_db
from app.crud import crud_user as crud

from app.models.user import User, UserTypeEnum
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["users"])



@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID, current_user: User = Depends(get_current_user), db: Session=Depends(get_db)):
  if user_id != current_user.id and current_user.user_type != UserTypeEnum.ADMIN:
     raise HTTPException(status_code=403, detail='No permission')

  user = crud.get_user_by_id(db, user_id)
  if not user:
    raise HTTPException(status_code=404, detail='User not found')
  return user

@router.post("/", response_model=UserResponse)
def create_user(data: UserCreate, db: Session=Depends(get_db)):
    try:
      return crud.create_user(db, data)
    except ValueError as e:
      raise HTTPException(status_code=409, detail=str(e))


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: UUID, data: UserUpdate, current_user: User = Depends(get_current_user), db: Session=Depends(get_db)):
  
  # 用户刚注册，user_type 是普通用户，他只能改自己的信息（user_id ==
  # current_user.id）。所以修自己的 user_type 为 ADMIN
  # 从权限上看是放行的，但这是个安全漏洞 —— 你得确认 UserUpdate schema
  # 是否允许修改 user_type 字段。
  if user_id != current_user.id and current_user.user_type != UserTypeEnum.ADMIN:
    raise HTTPException(status_code=403, detail='No permission')

  update = crud.update_user(db, user_id, data)

  if not update:
    raise HTTPException(status_code=404, detail='User not found')

  return update

@router.delete("/{user_id}")
def delete_user(
  user_id: UUID,
  _: User = Depends(require_admin),
  db: Session=Depends(get_db)
):
  success = crud.delete_user(db, user_id)

  if not success:
    raise HTTPException(status_code=404, detail='User not found')

  return {"message": 'User deleted'}
