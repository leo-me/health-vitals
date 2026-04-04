# schemas/user.py
from typing import Optional

from pydantic import BaseModel, ConfigDict
from uuid import UUID
from app.models.user import UserTypeEnum




class UserCreate(BaseModel):       # create user
    email: str
    password: str

class UserResponse(BaseModel):     # user info
    id: UUID
    email: str
    name: str
    sex: str
    age: int
    weight: float
    illness_history: str
    user_type: UserTypeEnum
    caregiver_id: UUID

    model_config = ConfigDict(from_attributes=True)



class UpdateUser(BaseModel):  # update user info
    name: Optional[str] = None
    sex: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    illness_history: Optional[str] = None
    user_type: Optional[UserTypeEnum] = None
    caregiver_id: Optional[UUID] = None
