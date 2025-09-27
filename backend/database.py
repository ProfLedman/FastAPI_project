from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os


DB_URL = "postgresql://postgres:******@localhost:5432/fastapi_db"

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Single source of Base for entire project
Base = declarative_base()

def get_db():
    """
    Dependency injection for database sessions.
    Yields a session and ensures proper cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()