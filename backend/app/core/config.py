from functools import lru_cache
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str | None = Field(default=None)
    DB_USER: str | None = None
    DB_PASSWORD: str = ""
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "geovault"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    CORS_ORIGINS: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
    )

    LOG_LEVEL: str = "INFO"

    SARVAM_API_KEY: str = ""
    SARVAM_TTS_URL: str = "https://api.sarvam.ai/text-to-speech"

    PROJECT_EXPORT_DIR: str = r"C:\Users\srihari.p\Desktop\YT\Projects"

    @field_validator("DATABASE_URL")
    @classmethod
    def strip_database_url(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        return s if s else None

    @property
    def resolved_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if not self.DB_USER:
            raise ValueError("Set DATABASE_URL or DB_USER.")
        user = quote_plus(self.DB_USER)
        auth = f"{user}:{quote_plus(self.DB_PASSWORD)}" if self.DB_PASSWORD else user
        return f"postgresql://{auth}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def async_database_url(self) -> str:
        url = self.resolved_database_url
        if url.startswith("postgresql+asyncpg://"):
            return url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        raise ValueError("DATABASE_URL must start with postgresql://, postgres://, or postgresql+asyncpg://")

    @property
    def cors_origins_list(self) -> list[str]:
        raw = [x.strip() for x in self.CORS_ORIGINS.split(",") if x.strip()]
        return raw or ["http://localhost:5173", "http://127.0.0.1:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
