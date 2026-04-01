from base import CRUDBase

class CRUDUser(CRUDBase):
    pass                                 # ← 通用操作全部继承

crud_user = CRUDUser(User)              # ← 传入 model 就够了

