# environment variables/settings file

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # App
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # default top k for search
    DEFAULT_TOP_K: int = 3

    # AI Keys (Phase 4)
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # redis for background tasks
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"

settings = Settings()
