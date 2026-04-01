 # Define database connection and Base class


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql://user:password@localhost/db")
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()    # ← 核心 core