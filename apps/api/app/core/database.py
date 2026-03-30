from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


def _make_engine():
    database_url = settings.database_url.strip()
    if not database_url:
        raise RuntimeError("DATABASE_URL is required to start the API")
    if settings.is_production and settings.uses_default_database_url:
        raise RuntimeError(
            "DATABASE_URL must be configured in production. The API is still pointing to the local default PostgreSQL URL.",
        )

    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(database_url, future=True, pool_pre_ping=True, connect_args=connect_args)


engine = _make_engine()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False, class_=Session)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
