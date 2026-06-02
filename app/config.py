from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql+psycopg://automotive:automotive@localhost:5432/automotive_car",
        alias="DATABASE_URL",
    )
    camera_stream_url: str = Field(
        default="http://localhost:8081/stream.mjpg",
        alias="CAMERA_STREAM_URL",
    )
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        alias="CORS_ORIGINS",
    )
    jwt_secret_key: str = Field(
        default="change-me-local-jwt-secret",
        alias="JWT_SECRET_KEY",
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expires_minutes: int = Field(default=30, alias="JWT_EXPIRES_MINUTES", gt=0)
    rate_limit_window_seconds: int = Field(default=60, alias="RATE_LIMIT_WINDOW_SECONDS", gt=0)
    rate_limit_general_requests: int = Field(default=120, alias="RATE_LIMIT_GENERAL_REQUESTS", gt=0)
    rate_limit_auth_requests: int = Field(default=12, alias="RATE_LIMIT_AUTH_REQUESTS", gt=0)
    email_verification_required: bool = Field(default=True, alias="EMAIL_VERIFICATION_REQUIRED")
    email_verification_expires_minutes: int = Field(default=60, alias="EMAIL_VERIFICATION_EXPIRES_MINUTES", gt=0)
    public_ui_url: str = Field(default="http://localhost:5173", alias="PUBLIC_UI_URL")
    smtp_host: str | None = Field(default=None, alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT", gt=0)
    smtp_username: str | None = Field(default=None, alias="SMTP_USERNAME")
    smtp_password: str | None = Field(default=None, alias="SMTP_PASSWORD")
    smtp_from_email: str = Field(default="no-reply@automotive-car.local", alias="SMTP_FROM_EMAIL")
    smtp_use_tls: bool = Field(default=True, alias="SMTP_USE_TLS")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
