"""
Database connection.

The connection string is read from the DATABASE_URL environment variable.
For local development it is stored in the .env file (see .env.example).
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Read variables from the .env file into the environment
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Copy .env.example to .env and fill in your database settings.")

# The engine manages the connections to PostgreSQL
engine = create_engine(DATABASE_URL)

# Every request gets its own session (a "conversation" with the database)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    """All database models inherit from this class."""
    pass


def get_db():
    """FastAPI dependency: open a session for one request and always close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
