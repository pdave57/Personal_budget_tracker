from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class Settings(BaseSettings):
    # Environment mode: "development" | "production" | "testing"
    environment: str = "development"
    debug: Optional[bool] = None

    # Database URLs & Paths
    database_url: Optional[str] = None
    sqlite_db_path: str = "./budget_tracker.db"

    # PostgreSQL configuration (Production)
    postgres_user: str = "postgres"
    postgres_password: str = "1q2w3e*"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "budget_tracker"

    # PostgreSQL Connection Pool configuration (Production)
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800
    db_pool_pre_ping: bool = True
    db_echo: bool = False

    # Security
    secret_key: str = "vPTCnlf_1ICUPXSOsuUmFlldYXanuCzMw9pLsHJAHtK-ynGK4-oDs037f9xUkGeP4WmXfBXqOL7AWKwyq105Cw"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=(".env", "app/.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"

    @model_validator(mode="after")
    def setup_environment_and_db(self):
        env = self.environment.lower().strip()

        # Debug mode: default True for dev, False for prod
        if self.debug is None:
            self.debug = (env == "development")

        # Database URL resolution
        if not self.database_url:
            if env == "production":
                # PostgreSQL connection for production
                self.database_url = (
                    f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
                    f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
                )
            elif env in ("test", "testing"):
                # In-memory SQLite for testing
                self.database_url = "sqlite:///:memory:"
            else:
                # SQLite connection for development
                self.database_url = f"sqlite:///{self.sqlite_db_path}"
        else:
            # Normalize PostgreSQL dialect prefix for SQLAlchemy + psycopg
            if self.database_url.startswith("postgres://"):
                self.database_url = self.database_url.replace("postgres://", "postgresql+psycopg://", 1)
            elif self.database_url.startswith("postgresql://") and "+psycopg" not in self.database_url:
                self.database_url = self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)

        return self


@lru_cache()
def get_settings() -> Settings:
    return Settings()
