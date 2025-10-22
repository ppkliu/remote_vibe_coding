from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://admin:password@localhost/claude_remote"
    JWT_SECRET: str = "dev-secret-key-min-32-characters-long"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CLAUDE_CODE_PATH: str = "claude"
    CLAUDE_CODE_TIMEOUT: int = 300
    CLAUDE_WORKING_DIRECTORY: str = "."  # Default working directory for Claude Code process
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    LOG_DIR: str = "logs"  # Directory for application logs
    LOG_LEVEL: str = "INFO"  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
