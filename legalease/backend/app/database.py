"""Database engine, session factory and declarative base.

Uses SQLAlchemy 2.0 style. The URL is supplied entirely by configuration so the
same code runs on SQLite locally and PostgreSQL in production.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """Declarative base shared by every ORM model."""


def _engine_kwargs(url: str) -> dict[str, Any]:
    kwargs: dict[str, Any] = {"pool_pre_ping": True, "future": True}
    if url.startswith("sqlite"):
        # SQLite + threaded uvicorn needs this to avoid cross-thread handles.
        kwargs["connect_args"] = {"check_same_thread": False}
    return kwargs


engine: Engine = create_engine(
    settings.database_url, **_engine_kwargs(settings.database_url)
)

SessionLocal = sessionmaker(
    bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
)


@event.listens_for(engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    """SQLite ignores FK constraints unless explicitly switched on."""
    if settings.database_url.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a scoped session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables for all registered models."""
    from app import models  # noqa: F401  (ensure models are imported/registered)

    Base.metadata.create_all(bind=engine)
