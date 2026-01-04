from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Default to a local PostgreSQL database if not provided
# User should replace this with their actual DB credentials
# SQLALCHEMY_DATABASE_URL = os.getenv(
#     "DATABASE_URL", 
#     "postgresql://postgres:postgres@localhost:5432/tcm_pulse_db"
# )

# If using SQLite for fallback (not recommended for JSONB but supported by SQLAlchemy with restrictions)
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
