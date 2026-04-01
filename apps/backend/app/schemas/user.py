# schemas/user.py
class UserCreate(BaseModel):       # 创建用户时，前端传什么
    email: str
    password: str

class UserResponse(BaseModel):     # 返回给前端的是什么
    id: int
    email: str
    # password 没有！← 不能把密码返回给前端