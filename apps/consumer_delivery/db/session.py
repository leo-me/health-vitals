import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv(os.getenv("ENV_FILE", ".env"))   # 把那行死代码激活


DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql://postgres:0000@db:5432/health_db"


# DATABASE_URL="postgresql://postgres:0000@localhost:5432/health_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
