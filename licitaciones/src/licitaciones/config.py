"""Application configuration using pydantic-settings."""

from enum import Enum
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    GEMINI = "gemini"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM API Keys
    openai_api_key: str = ""
    google_api_key: str = ""

    # Structured Output Configuration
    structured_output_provider: Literal["openai", "gemini"] = "gemini"
    structured_output_model_openai: str = "gpt-4o-mini"
    structured_output_model_gemini: str = "gemini-2.5-flash"
    structured_output_temperature: float = 0

    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "catalogo_servelec"

    @property
    def database_url(self) -> str:
        """Build database URL from components."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # PDF Options
    pdf_max_pages: int = 50
    pdf_max_size_mb: int = 100  # in megabytes
    pdf_low_res_dpi_threshold: int = 150
    pdf_text_to_size_ratio_threshold: float = 0.01
    pdf_min_acceptable_quality_score: int = 10


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()
