from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    app_name: str = "Global Pharma Passport API"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/global_pharma_passport"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    jwt_issuer: str = "global-pharma-passport-api"
    jwt_audience: str = "global-pharma-passport-clients"
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_premium_monthly_price_id: str | None = None
    app_base_url: str = "http://localhost:3000"
    default_language: str = "fr"
    default_country: str = "MA"
    allowed_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    trusted_hosts: list[str] = ["localhost", "127.0.0.1"]
    force_https: bool = False
    docs_enabled: bool = True
    enable_product_analytics: bool = True
    log_level: str = "INFO"
    enable_request_logging: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @field_validator("allowed_origins", "trusted_hosts", mode="before")
    @classmethod
    def parse_csv_list(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


settings = Settings()
