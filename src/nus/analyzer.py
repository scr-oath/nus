"""Claude-powered article analyzer with batching."""

import asyncio
import json
from typing import Optional

import anthropic
from loguru import logger

from .exceptions import AnalysisError
from .models import AnalysisResult, Article, Category


class ArticleAnalyzer:
    """Claude-powered article analyzer with batching."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 1024,
        temperature: float = 0.3,
        max_concurrent: int = 5,
    ):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
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

    async def _analyze_article(
        self, article: Article, filter_clickbait: bool
    ) -> AnalysisResult:
        """Analyze a single article with Claude."""
        async with self.semaphore:
            prompt = self._build_prompt(article)

            try:
                message = await self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[{"role": "user", "content": prompt}],
                )

                # Parse structured response
                response_text = message.content[0].text
                parsed = self._parse_response(response_text)

                return AnalysisResult(
                    article=article,
                    category=parsed["category"],
                    is_clickbait=parsed["is_clickbait"],
                    confidence=parsed["confidence"],
                    reasoning=parsed.get("reasoning"),
                )

            except Exception as e:
                raise AnalysisError(f"Claude API error: {e}")

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
        """Parse Claude's structured response."""
        # Expect JSON response with schema validation
        try:
            data = json.loads(response)
            return {
                "category": Category(data["category"]),
                "is_clickbait": data["is_clickbait"],
                "confidence": float(data["confidence"]),
                "reasoning": data.get("reasoning"),
            }
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise AnalysisError(f"Invalid response format: {e}")
