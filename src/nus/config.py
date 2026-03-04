"""Configuration management for the news curation system."""

import json
from pathlib import Path
from typing import Any, Literal, Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Provider Selection
    ai_provider: Literal["anthropic", "gemini"] = Field(
        "anthropic", alias="AI_PROVIDER"
    )

    # API Keys
    anthropic_api_key: Optional[str] = Field(None, alias="ANTHROPIC_API_KEY")
    gemini_api_key: Optional[str] = Field(None, alias="GEMINI_API_KEY")

    # Model Configuration
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    gemini_model: str = "gemini-2.0-flash"
    max_tokens: int = 1024
    temperature: float = 0.3

    # Fetching Configuration
    fetch_timeout: int = 30
    max_concurrent_feeds: int = 20
    max_concurrent_api_calls: int = 5
    retry_attempts: int = 3
    retry_delay: float = 1.0

    # Paths
    feeds_config: Path = Path("config/feeds.json")
    prompt_template: Path = Path("prompts/categorization.md")
    output_dir: Path = Path("docs")

    # Output Configuration
    output_filename: str = "index.html"
    max_articles_per_category: int = 50

    # Feature Flags
    filter_clickbait: bool = True
    deduplicate_articles: bool = True

    @model_validator(mode="after")
    def validate_api_key_for_provider(self) -> "Settings":
        """Validate that the appropriate API key is set for the selected provider."""
        if self.ai_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY required when AI_PROVIDER=anthropic")
        if self.ai_provider == "gemini" and not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY required when AI_PROVIDER=gemini")
        return self


def load_feeds(path: Path) -> list[dict[str, Any]]:
    """Load RSS feeds from JSON configuration."""
    with path.open() as f:
        return json.load(f)


def load_prompt_template(path: Path) -> str:
    """Load Claude prompt template."""
    return path.read_text(encoding="utf-8")
