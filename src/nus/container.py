"""Dependency injection container for the NUS application."""

from dependency_injector import containers, providers

from .analyzers import AnalyzerConfig, AnthropicAnalyzer, GeminiAnalyzer
from .base_analyzer import BaseAnalyzer
from .config import Settings
from .fetcher import RSSFetcher
from .orchestrator import Orchestrator
from .renderer import HTMLRenderer


class Container(containers.DeclarativeContainer):
    """Application dependency container."""

    config = providers.Singleton(Settings)  # Settings object as Singleton

    # Config bundles — Factory (immutable dataclasses, cheap to create)
    anthropic_config = providers.Factory(
        AnalyzerConfig,
        api_key=config.provided.anthropic_api_key,
        model=config.provided.anthropic_model,
        max_tokens=config.provided.max_tokens,
        temperature=config.provided.temperature,
        max_concurrent=config.provided.max_concurrent_api_calls,
    )

    gemini_config = providers.Factory(
        AnalyzerConfig,
        api_key=config.provided.gemini_api_key,
        model=config.provided.gemini_model,
        max_tokens=config.provided.max_tokens,
        temperature=config.provided.temperature,
        max_concurrent=config.provided.max_concurrent_api_calls,
    )

    # Analyzers — Singleton (stateful: API client, asyncio.Semaphore)
    anthropic_analyzer = providers.Singleton(
        AnthropicAnalyzer,
        config=anthropic_config,
    )

    gemini_analyzer = providers.Singleton(
        GeminiAnalyzer,
        config=gemini_config,
    )

    # Selector routes to the right Singleton based on ai_provider config
    analyzer: providers.Provider[BaseAnalyzer] = providers.Selector(
        config.provided.ai_provider,
        anthropic=anthropic_analyzer,
        gemini=gemini_analyzer,
    )

    # Infrastructure — Singleton (stateful: httpx client)
    fetcher = providers.Singleton(
        RSSFetcher,
        timeout=config.provided.fetch_timeout,
        max_concurrent=config.provided.max_concurrent_feeds,
    )

    # Renderer — Singleton (no state, but consistent lifecycle)
    renderer = providers.Singleton(HTMLRenderer)

    # Orchestrator — Singleton (wires all dependencies together)
    orchestrator = providers.Singleton(
        Orchestrator,
        analyzer=analyzer,
        fetcher=fetcher,
        renderer=renderer,
        settings=config,
    )
