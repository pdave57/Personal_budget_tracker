from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from app.config import get_settings

settings = get_settings()


def get_engine_args():
    is_sqlite = "sqlite" in settings.database_url.lower()

    if is_sqlite:
        # SQLite configuration for Development
        engine_args = {
            "connect_args": {"check_same_thread": False},
        }
        if ":memory:" in settings.database_url.lower():
            engine_args["poolclass"] = StaticPool
        return engine_args
    else:
        # PostgreSQL configuration for Production
        return {
            "pool_size": settings.db_pool_size,
            "max_overflow": settings.db_max_overflow,
            "pool_timeout": settings.db_pool_timeout,
            "pool_recycle": settings.db_pool_recycle,
            "pool_pre_ping": settings.db_pool_pre_ping,
            "echo": settings.db_echo,
        }


engine = create_engine(
    settings.database_url,
    **get_engine_args(),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
