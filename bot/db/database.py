import logging
import os
from urllib.parse import quote_plus

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

log = logging.getLogger(__name__)


def _build_database_url() -> str:
    """
    Беремо DATABASE_URL з .env або збираємо з частин (дефолт під docker-compose).
    """
    url = (os.getenv("DATABASE_URL") or "").strip()
    if url:
        return url

    user = os.getenv("DB_USER", "balcony")
    password = os.getenv("DB_PASSWORD", "balcony")
    host = os.getenv("DB_HOST", "postgres")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "balcony")
    return f"postgresql+asyncpg://{quote_plus(user)}:{quote_plus(password)}@{host}:{port}/{name}"


class Base(DeclarativeBase):
    pass


# Сінглтони
_engine: AsyncEngine | None = None
SessionLocal: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """
    Ініціалізує і повертає AsyncEngine + SessionLocal один раз.
    """
    global _engine, SessionLocal
    if _engine is None:
        db_url = _build_database_url()
        log.info("DB URL resolved: %s", db_url.replace(":balcony@", ":****@"))
        _engine = create_async_engine(db_url, echo=False, pool_pre_ping=True)
        SessionLocal = async_sessionmaker(_engine, expire_on_commit=False)
    return _engine
