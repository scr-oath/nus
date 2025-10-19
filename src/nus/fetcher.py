"""Async RSS feed fetcher with error handling."""

import asyncio
from datetime import datetime
from typing import Any, Optional

import feedparser
import httpx
from loguru import logger

from .exceptions import FetchError
from .models import Article, RSSFeed


class RSSFetcher:
    """Async RSS feed fetcher with error handling."""

    def __init__(
        self,
        timeout: int = 30,
        max_concurrent: int = 20,
    ):
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "RSSFetcher":
        """Async context manager entry."""
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            limits=httpx.Limits(max_connections=50),
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()

    async def fetch_all(
        self, feeds: list[RSSFeed]
    ) -> tuple[list[Article], list[str]]:
        """Fetch all feeds concurrently with error handling."""
        logger.info(f"Fetching {len(feeds)} RSS feeds...")

        # Filter enabled feeds and sort by priority
        active_feeds = [f for f in feeds if f.enabled]
        active_feeds.sort(key=lambda f: f.priority, reverse=True)

        # Fetch concurrently
        tasks = [self._fetch_feed(feed) for feed in active_feeds]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Separate successes from failures
        articles: list[Article] = []
        errors: list[str] = []

        for feed, result in zip(active_feeds, results):
            if isinstance(result, Exception):
                error_msg = f"Feed '{feed.name}' failed: {result}"
                logger.error(error_msg)
                errors.append(error_msg)
            elif isinstance(result, list):
                articles.extend(result)
                logger.info(f"Feed '{feed.name}': {len(result)} articles")
            else:
                errors.append(f"Feed '{feed.name}': unexpected result type")

        logger.info(
            f"Fetched {len(articles)} articles from "
            f"{len(active_feeds) - len(errors)}/{len(active_feeds)} feeds"
        )
        return articles, errors

    async def _fetch_feed(self, feed: RSSFeed) -> list[Article]:
        """Fetch a single RSS feed with retries."""
        async with self.semaphore:
            for attempt in range(3):
                try:
                    return await self._parse_feed(feed)
                except Exception as e:
                    if attempt == 2:
                        raise FetchError(f"Failed after 3 attempts: {e}")
                    await asyncio.sleep(2**attempt)  # Exponential backoff
            return []

    async def _parse_feed(self, feed: RSSFeed) -> list[Article]:
        """Parse RSS feed into Article objects."""
        if not self.client:
            raise RuntimeError("Client not initialized")

        response = await self.client.get(feed.url)
        response.raise_for_status()

        # Parse with feedparser (sync, but fast)
        parsed = await asyncio.to_thread(feedparser.parse, response.content)

        articles = []
        for entry in parsed.entries:
            try:
                article = Article(
                    title=entry.get("title", "No title"),
                    url=entry.get("link", ""),
                    source=feed.name,
                    published=self._parse_date(entry),
                    summary=entry.get("summary") or entry.get("description"),
                )
                articles.append(article)
            except Exception as e:
                logger.warning(f"Skipping malformed entry: {e}")

        return articles

    @staticmethod
    def _parse_date(entry: dict) -> Optional[datetime]:
        """Parse published date from feed entry."""
        for field in ["published_parsed", "updated_parsed"]:
            if time_struct := entry.get(field):
                try:
                    return datetime(*time_struct[:6])
                except Exception:
                    pass
        return None
