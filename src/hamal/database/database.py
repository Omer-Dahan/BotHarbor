"""Database connection and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from hamal.core.config import get_database_path
from hamal.database.models import Base


# Global engine and session factory
ENGINE = None
SESSION_LOCAL = None


def get_engine():
    """Get or create the SQLAlchemy engine."""
    global ENGINE  # pylint: disable=global-statement
    if ENGINE is None:
        db_path = get_database_path()
        ENGINE = create_engine(
            f"sqlite:///{db_path}",
            echo=False,  # Set to True for SQL debugging
            connect_args={"check_same_thread": False}  # Required for SQLite with threads
        )
    return ENGINE


def get_session_factory() -> sessionmaker:
    """Get or create the session factory."""
    global SESSION_LOCAL  # pylint: disable=global-statement
    if SESSION_LOCAL is None:
        engine = get_engine()
        SESSION_LOCAL = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return SESSION_LOCAL


def init_database():
    """Initialize the database, creating tables if they don't exist."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    """Get a new database session. Caller is responsible for closing it."""
    factory = get_session_factory()
    return factory()
