from typing import Optional

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("dev.env", ".env"), env_file_encoding="utf-8")

    # S3
    S3_ACCESS_ID: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_BUCKET_URL: Optional[str] = None

    # SELF AUTH
    SECRET_KEY: Optional[str] = None
    ALGORITHM: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: Optional[str] = None
    DATETIME_FORMAT: Optional[str] = None

    # THIRD AUTH
    AUTH_SERVICE_ENDPOINT: Optional[str] = None


settings = Settings()
