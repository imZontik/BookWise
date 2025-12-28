from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_PORT: int
    DATABASE_URL: str
    LOCAL_DATABASE_URL: str

    REDIS_URL: str

    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_HOST: str
    MINIO_PORT: int
    MINIO_ENDPOINT: str
    MINIO_PUBLIC_ENDPOINT: str
    MINIO_BUCKET_AVATARS: str

    APP_PORT: int

    AUTH_SECRET_KEY: str
    AUTH_ALGORITHM: str


settings = Settings() # type: ignore