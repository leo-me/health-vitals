# crud/base.py
class CRUDBase:
    def __init__(self, model):
        self.model = model               # ← 泛型思路

    def get(self, db, id):
        return db.query(self.model).filter(self.model.id == id).first()

    def create(self, db, obj): ...
    def update(self, db, obj): ...
    def delete(self, db, id): ...
    
    