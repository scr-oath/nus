"""Configuration management for the news curation system."""

import json
from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Configuration
    anthropic_api_key: str = Field(..., alias="ANTHROPIC_API_KEY")
    claude_model: str = "claude-3-haiku-20240307"
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


def load_feeds(path: Path) -> list[dict[str, Any]]:
    """Load RSS feeds from JSON configuration."""
    with path.open() as f:
        return json.load(f)


def load_prompt_template(path: Path) -> str:
    """Load Claude prompt template."""
    return path.read_text(encoding="utf-8")
