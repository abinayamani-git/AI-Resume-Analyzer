"""
Application configuration.

Loads settings from environment variables so secrets stay out of source code.
"""

from pathlib import Path
from pydantic_settings import BaseSettings


# Resolve paths relative to the backend folder
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent


class Settings(BaseSettings):
    """Central app settings — override via .env or environment variables."""

    app_name: str = "AI Resume Analyzer"
    host: str = "0.0.0.0"
    port: int = 8000

    # File upload limits
    upload_dir: str = str(PROJECT_ROOT / "uploads")
    max_file_size_mb: int = 5
    allowed_extensions: str = ".pdf,.docx"

    # AI provider: "fallback" (rule-based) or "openai" (future)
    ai_provider: str = "fallback"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # SQLite path (modular — swap for PostgreSQL later)
    database_url: str = f"sqlite:///{BASE_DIR / 'data' / 'analyses.db'}"

    class Config:
        env_file = str(BASE_DIR / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def allowed_ext_list(self) -> list[str]:
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",") if ext.strip()]


settings = Settings()

# Ensure upload and data directories exist
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Path(BASE_DIR / "data").mkdir(parents=True, exist_ok=True)
