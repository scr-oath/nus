"""Main workflow coordinator for news curation."""

from dataclasses import dataclass
from datetime import datetime

from loguru import logger

from .base_analyzer import BaseAnalyzer
from .config import Settings, load_feeds, load_prompt_template
from .fetcher import RSSFetcher
from .models import Article, Category, Digest, RSSFeed
from .renderer import HTMLRenderer


@dataclass
class Orchestrator:
    """Coordinates the entire news curation workflow."""

    analyzer: BaseAnalyzer
    fetcher: RSSFetcher
    renderer: HTMLRenderer
    settings: Settings

    async def run(self) -> Digest:
        """Execute the complete curation pipeline."""
        logger.info("Starting news curation pipeline...")
        start_time = datetime.now()

        # Load configuration
        feeds = self._load_feeds()
        prompt = load_prompt_template(self.settings.prompt_template)
        self.analyzer.set_prompt_template(prompt)

        # Fetch articles
        async with self.fetcher:
            articles, fetch_errors = await self.fetcher.fetch_all(feeds)

        # Deduplicate
        if self.settings.deduplicate_articles:
            articles = self._deduplicate(articles)

        # Analyze with Claude
        results = await self.analyzer.analyze_batch(
            articles, filter_clickbait=self.settings.filter_clickbait
        )

        # Filter clickbait
        if self.settings.filter_clickbait:
            results = [r for r in results if not r.is_clickbait]

        # Group by category
        categorized = self._group_by_category(results)

        # Create digest
        digest = Digest(
            generated_at=start_time,
            articles_by_category=categorized,
            total_fetched=len(articles),
            total_filtered=len(articles) - len(results),
            errors=fetch_errors,
        )

        # Render HTML
        output_path = self.settings.output_dir / self.settings.output_filename
        self.renderer.render_digest(digest, output_path)

        logger.info(
            f"Pipeline complete in {(datetime.now() - start_time).seconds}s. "
            f"Generated {output_path}"
        )
        return digest

    def _load_feeds(self) -> list[RSSFeed]:
        """Load and validate feed configuration."""
        feed_data = load_feeds(self.settings.feeds_config)
        return [RSSFeed(**feed) for feed in feed_data]

    @staticmethod
    def _deduplicate(articles: list[Article]) -> list[Article]:
        """Remove duplicate articles by URL."""
        seen = set()
        unique = []
        for article in articles:
            if article.url not in seen:
                seen.add(article.url)
                unique.append(article)
        return unique

    @staticmethod
    def _group_by_category(results: list) -> dict[Category, list[Article]]:
        """Group analyzed articles by category."""
        grouped = {cat: [] for cat in Category}
        for result in results:
            article = result.article
            article.category = result.category
            grouped[result.category].append(article)
        return grouped
