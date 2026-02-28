from pydantic_settings import BaseSettings
from pathlib import Path

# Get the backend directory path
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGO: str = "HS256"
    ACCESS_TOKEN_EXPIRE: int = 30
    ENVIRONMENT: str
    DEBUG: bool = False
    FRONTEND_URL: str

    model_config = {
        "extra": "allow",
        "env_file": str(BASE_DIR / ".env")
    }

settings = Settings()
