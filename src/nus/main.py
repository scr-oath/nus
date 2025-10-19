"""Main entry point for the news curation system."""

import asyncio
import sys
from pathlib import Path

from loguru import logger

from .config import Settings
from .orchestrator import NewsOrchestrator


def setup_logging() -> None:
    """Configure logging for the application."""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
    )


def main() -> None:
    """Main entry point for digest generation."""
    setup_logging()

    try:
        logger.info("NUS - News Curation System starting...")

        # Load settings
        settings = Settings()

        # Run the orchestrator
        orchestrator = NewsOrchestrator(settings)
        digest = asyncio.run(orchestrator.run())

        logger.success(
            f"Digest generated successfully! "
            f"Articles: {sum(len(articles) for articles in digest.articles_by_category.values())} "
            f"Success rate: {digest.success_rate:.1%}"
        )

    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


def test_local() -> None:
    """Test mode for local development with limited article processing."""
    setup_logging()
    logger.info("Running in TEST mode...")

    # Override settings for testing
    import os

    os.environ["MAX_CONCURRENT_API_CALLS"] = "2"

    main()


if __name__ == "__main__":
    main()
