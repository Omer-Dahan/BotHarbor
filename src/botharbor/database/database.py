"""Database connection and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from botharbor.core.config import get_database_path
from botharbor.database.models import Base


# Global engine and session factory
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create the SQLAlchemy engine."""
    global _engine
    if _engine is None:
        db_path = get_database_path()
        _engine = create_engine(
            f"sqlite:///{db_path}",
            echo=False,  # Set to True for SQL debugging
            connect_args={"check_same_thread": False}  # Required for SQLite with threads
        )
    return _engine


def get_session_factory() -> sessionmaker:
    """Get or create the session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return _SessionLocal


def init_database():
    """Initialize the database, creating tables if they don't exist."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    """Get a new database session. Caller is responsible for closing it."""
    factory = get_session_factory()
    return factory()
