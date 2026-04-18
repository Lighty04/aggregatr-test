"""API configuration settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "sqlite:///./aggregatr.db"
    database_echo: bool = False

    # API
    api_title: str = "Aggregatr API"
    api_description: str = "Event aggregation API with normalized venue data"
    api_version: str = "1.0.0"
    api_prefix: str = "/api/v1"

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:8080"
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "GET,POST,PUT,DELETE,OPTIONS"
    cors_allow_headers: str = "*"

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def cors_allow_methods_list(self) -> list[str]:
        """Return allowed methods as a list."""
        return [method.strip() for method in self.cors_allow_methods.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
