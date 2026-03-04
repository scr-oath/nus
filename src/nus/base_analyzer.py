"""Abstract base class for article analyzers."""

import asyncio
from abc import ABC, abstractmethod
from typing import Optional

from .models import AnalysisResult, Article


class BaseAnalyzer(ABC):
    """Abstract base class for article analyzers."""

    def __init__(
        self,
        model: str,
        max_tokens: int = 1024,
        temperature: float = 0.3,
        max_concurrent: int = 5,
    ):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.prompt_template: Optional[str] = None

    def set_prompt_template(self, template: str) -> None:
        """Set the categorization prompt template."""
        self.prompt_template = template

    async def analyze_batch(
        self,
        articles: list[Article],
        filter_clickbait: bool = True,
    ) -> list[AnalysisResult]:
        """Analyze articles in parallel with rate limiting."""
        from loguru import logger

        logger.info(f"Analyzing {len(articles)} articles...")

        tasks = [
            self._analyze_article(article, filter_clickbait) for article in articles
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_results = []
        for article, result in zip(articles, results):
            if isinstance(result, Exception):
                logger.error(f"Analysis failed for '{article.title}': {result}")
            elif isinstance(result, AnalysisResult):
                valid_results.append(result)

        logger.info(f"Successfully analyzed {len(valid_results)} articles")
        return valid_results

    @abstractmethod
    async def _analyze_article(
        self, article: Article, filter_clickbait: bool
    ) -> AnalysisResult:
        """Analyze a single article. Subclasses must implement."""
        pass

    def _build_prompt(self, article: Article) -> str:
        """Build analysis prompt from template."""
        if not self.prompt_template:
            raise ValueError("Prompt template not set")

        return self.prompt_template.format(
            title=article.title,
            summary=article.summary or "No summary available",
            source=article.source,
        )

    @staticmethod
    def _parse_response(response: str) -> dict:
        """Parse structured response (common for all providers)."""
        import json
        import re

        from .exceptions import AnalysisError
        from .models import Category

        # Strip markdown code fences (```json ... ```) that LLMs often add
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", response.strip())
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)

        try:
            data = json.loads(cleaned)
            return {
                "category": Category(data["category"]),
                "is_clickbait": data["is_clickbait"],
                "confidence": float(data["confidence"]),
                "reasoning": data.get("reasoning"),
            }
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise AnalysisError(f"Invalid response format: {e}")
