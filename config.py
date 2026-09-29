from typing import Any

class Settings:
    SECRET_KEY: str = "replace-with-secure-secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

settings = Settings()
