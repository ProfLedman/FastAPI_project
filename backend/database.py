from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please check your .env file."
    )

def test_connection(engine):
    """Test database connection and print detailed error messages"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"Successfully connected to PostgreSQL. Version: {version}")
            return True
    except SQLAlchemyError as e:
        print(f"Database connection error: {str(e.__dict__['orig'])}")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False

try:
    engine = create_engine(
        DB_URL,
        echo=True,
        pool_pre_ping=True,  # Enable connection health checks
        pool_recycle=300     # Recycle connections every 5 minutes
    )
    
    # Test the connection during startup
    if not test_connection(engine):
        raise ConnectionError("Failed to establish database connection")

except Exception as e:
    print(f"Failed to create database engine: {str(e)}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Dependency injection for database sessions.
    Yields a session and ensures proper cleanup.
    """
    db = None
    try:
        db = SessionLocal()
        # Verify connection is still alive
        db.execute(text("SELECT 1"))
        yield db
    except SQLAlchemyError as e:
        print(f"Session error: {str(e.__dict__['orig'])}")
        raise
    finally:
        if db:
            db.close()