"""Application settings.

Values come from environment variables (or a local .env file), never from
hard-coded strings. That is how secrets such as a PostgreSQL password stay
out of source control.
"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # SQLite by default. Switch to PostgreSQL by changing only this value.
    database_url: str = "sqlite:///./tickets.db"
    # Comma-separated list, parsed by the `cors_origin_list` property below.
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    log_level: str = "INFO"

    model_path: Path = BASE_DIR / "models" / "ticket_classifier.joblib"
    metrics_path: Path = BASE_DIR / "models" / "metrics.json"
    dataset_path: Path = BASE_DIR / "data" / "tickets_demo.csv"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
