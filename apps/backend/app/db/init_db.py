from app.db.base import Base
from app.db.session import engine

def init_db():
    Base.metadata.create_all(bind=engine)  # ← read all models and create table


def insert_origin_data(db: Session):
    # 建表之后，插入一些默认数据
    admin = User(email="admin@admin.com", role="admin")
    db.add(admin)
    db.commit()