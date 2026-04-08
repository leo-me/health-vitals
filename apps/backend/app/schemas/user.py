# schemas/user.py
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID
from datetime import datetime
from app.models.user import UserTypeEnum, SexEnum




class UserCreate(BaseModel):       # create user
    email: EmailStr
    password: str

class UserResponse(BaseModel):     # user info
    id: UUID
    email: str
    name: Optional[str] = None
    sex: Optional[SexEnum] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    illness_history: Optional[str] = None
    user_type: Optional[UserTypeEnum] = None
    caregiver_id: Optional[UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



class UserUpdate(BaseModel):  # update user info
    name: Optional[str] = None
    sex: Optional[SexEnum] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    illness_history: Optional[str] = None
    user_type: Optional[UserTypeEnum] = None
    caregiver_id: Optional[UUID] = None
