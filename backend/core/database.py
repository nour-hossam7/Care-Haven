from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.core.config import settings


engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    """Yield one database session and always close it after use."""

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()