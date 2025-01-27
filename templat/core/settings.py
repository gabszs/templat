from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("dev.env", ".env"), env_file_encoding="utf-8")

    S3_ACCESS_ID: str
    S3_SECRET_KEY: str
    S3_BUCKET_URL: str


settings = Settings()
