"""Database connection.

SQLAlchemy is the layer that lets the SAME code talk to SQLite or PostgreSQL.
Only DATABASE_URL (in .env) changes; no code changes are needed.
"""
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings

_engine_kwargs: dict = {}
if settings.database_url.startswith("sqlite"):
    # SQLite objects are tied to one thread by default; FastAPI uses a thread pool.
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
    if settings.database_url in ("sqlite://", "sqlite:///:memory:"):
        # An in-memory SQLite DB lives inside ONE connection, so share it (used by tests).
        _engine_kwargs["poolclass"] = StaticPool

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    **_engine_kwargs,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Parent class of all table definitions."""


def get_db() -> Iterator[Session]:
    """FastAPI dependency: one DB session per request, always closed afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
