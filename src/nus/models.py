"""Data models for the news curation system."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class Category(str, Enum):
    """Article categories for curation."""

    MUST_KNOW = "Must Know"
    SPORTS = "Sports Context"
    TECH = "Tech & Tools"
    FUN = "Fun Stuff"
    UNCATEGORIZED = "Uncategorized"


@dataclass(frozen=True)
class RSSFeed:
    """Configuration for an RSS feed source."""

    name: str
    url: str
    enabled: bool = True
    timeout: int = 30
    priority: int = 0  # Higher = process first


@dataclass
class Article:
    """Represents a news article."""

    title: str
    url: str
    source: str
    published: Optional[datetime]
    summary: Optional[str] = None
    category: Category = Category.UNCATEGORIZED
    is_clickbait: bool = False
    fetch_error: Optional[str] = None

    def __hash__(self) -> int:
        """Enable deduplication by URL."""
        return hash(self.url)


@dataclass
class AnalysisResult:
    """Result from Claude API analysis."""

    article: Article
    category: Category
    is_clickbait: bool
    confidence: float  # 0-1
    reasoning: Optional[str] = None


@dataclass
class Digest:
    """Complete news digest."""

    generated_at: datetime
    articles_by_category: dict[Category, list[Article]]
    total_fetched: int
    total_filtered: int
    errors: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate the success rate of article fetching."""
        if self.total_fetched == 0:
            return 0.0
        return (self.total_fetched - len(self.errors)) / self.total_fetched
