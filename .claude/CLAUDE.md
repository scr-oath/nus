# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**NUS** is an AI-powered daily news curation system that fetches RSS feeds, uses Claude API or Gemini API to categorize articles, and generates a mobile-friendly static HTML digest deployed via GitHub Pages. Features pluggable AI providers via dependency injection.

## Development Commands

```bash
# Install dependencies
uv sync

# Run the full digest pipeline
uv run generate-digest

# Test locally (limited API calls for cost/speed)
uv run test-local

# Code quality checks
uv run mypy src/
uv run ruff check src/

# Format code
uv run ruff format src/
```

## Code Architecture

### Module Organization (src/nus/)

- **main.py**: Entry point. Configures logging, initializes DI container, and runs orchestrator.
- **container.py**: Dependency injection container. Wires all components with `dependency-injector` using `providers.Selector` for provider selection.
- **orchestrator.py**: Coordinates the entire pipeline (fetch → analyze → filter → render). Injected with all dependencies as dataclass fields.
- **fetcher.py**: Async RSS fetching with concurrency control and retry logic.
- **base_analyzer.py**: Abstract base class for AI providers. Defines `analyze_batch()` and shared logic like `_build_prompt()`.
- **analyzers.py**: Provider implementations (AnthropicAnalyzer, GeminiAnalyzer). Shared config dataclass `AnalyzerConfig`.
- **renderer.py**: Jinja2 template rendering. Converts categorized articles to static HTML.
- **models.py**: Data models (Article, Category, Digest, RSSFeed, AnalysisResult).
- **config.py**: Pydantic Settings with `ai_provider` selector and validation for API keys.

### Data Flow

1. **Initialize**: `main.py` loads Settings, creates DI container, passes config via `from_pydantic()`.
2. **Provide**: Container's `providers.Selector` routes to AnthropicAnalyzer or GeminiAnalyzer based on `AI_PROVIDER`.
3. **Inject**: `Orchestrator` receives all dependencies (analyzer, fetcher, renderer, settings) as constructor args.
4. **Load config**: Reads `config/feeds.json` (RSS sources) and `prompts/categorization.md` (prompt).
5. **Fetch**: `RSSFetcher` concurrently fetches all feeds, handling timeouts/failures gracefully.
6. **Analyze**: Selected analyzer (`BaseAnalyzer` subclass) sends articles to API in batches (rate-limited by `max_concurrent_api_calls`).
7. **Filter**: Deduplicates, removes clickbait, respects category balance requirements.
8. **Render**: `HTMLRenderer` generates the static digest using Jinja2 template.
9. **Output**: Writes to `docs/index.html` (GitHub Pages deploys this).

### Key Design Decisions

- **Pluggable Providers**: Abstract `BaseAnalyzer` with Anthropic and Gemini implementations. Selected at runtime via DI.
- **Dependency Injection**: `dependency-injector` with `providers.Selector` for clean provider routing. All stateful objects are Singletons.
- **Dataclass Composition**: `Orchestrator` and `AnalyzerConfig` use frozen dataclasses; the container composes the object tree.
- **Graceful Degradation**: If a feed fails, the pipeline continues with partial results. The success_rate metric tracks this.
- **Rate Limiting**: Uses asyncio Semaphore to limit concurrent API calls (respect provider rate limits).
- **Deduplication**: Articles are hashed by URL to prevent duplicates across feeds.
- **External Config**: Prompts and feeds are in separate files (not hardcoded), making tuning easy without code changes.

## Configuration & Settings

Environment variables (override in `.env`):

```bash
# Provider Selection
AI_PROVIDER=gemini              # anthropic or gemini

# API Keys (set the one for your chosen provider)
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...

# Model Configuration
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
GEMINI_MODEL=gemini-2.0-flash
MAX_TOKENS=1024
TEMPERATURE=0.3

# Performance
MAX_CONCURRENT_FEEDS=20        # RSS fetch concurrency
MAX_CONCURRENT_API_CALLS=5     # Provider API rate limit
FETCH_TIMEOUT=30              # Seconds per feed

# Features
FILTER_CLICKBAIT=true
DEDUPLICATE_ARTICLES=true
```

**Important**: The `validate_api_key_for_provider` validator in Settings ensures the correct API key is set for the selected provider.

Paths are relative to project root:
- `config/feeds.json`: List of RSS feed sources with enabled/priority flags.
- `prompts/categorization.md`: Claude prompt template (user-editable for tuning).
- `docs/index.html`: Generated digest output (GitHub Pages source).

## When Making Changes

### Modifying Python Code
1. Maintain type hints on all functions.
2. Update docstrings if behavior changes.
3. Preserve async patterns (use httpx.AsyncClient, asyncio).
4. Check code quality: `uv run ruff check src/` and `uv run mypy src/`.
5. Test locally: `uv run test-local`.

### Tuning AI Behavior
Edit `prompts/categorization.md` (not Python code). The prompt instructs Claude to:
- Categorize into: Must Know, Sports Context, Tech & Tools, Fun Stuff
- Detect clickbait
- Suggest balance across categories
- Provide "why people care" explanations for sports

Expected Claude response format: JSON with `category`, `is_clickbait`, `summary` fields.

### Adding/Modifying Categories
1. Update `models.py`: Add to `Category` enum.
2. Update `prompts/categorization.md`: Define the new category.
3. Update `templates/digest.html`: Add styling if needed.

### Adding a New AI Provider

To add a new provider (e.g., OpenAI):

1. **Create implementation in `analyzers.py`**:
   ```python
   class OpenAIAnalyzer(BaseAnalyzer):
       def __init__(self, config: AnalyzerConfig) -> None:
           super().__init__(...)
           self.client = openai.AsyncOpenAI(api_key=config.api_key)

       async def _analyze_article(self, article: Article, filter_clickbait: bool = True) -> AnalysisResult:
           # Implement provider-specific logic
   ```

2. **Update `container.py`**:
   ```python
   openai_config = providers.Factory(AnalyzerConfig, ...)
   openai_analyzer = providers.Singleton(OpenAIAnalyzer, config=openai_config)
   analyzer = providers.Selector(
       config.ai_provider,
       anthropic=anthropic_analyzer,
       gemini=gemini_analyzer,
       openai=openai_analyzer,  # Add here
   )
   ```

3. **Update `config.py`**:
   - Add `openai_api_key: Optional[str]` field
   - Add `openai_model: str` field
   - Update `validate_api_key_for_provider()` to check for openai key
   - Update `AI_PROVIDER` Literal to include "openai"

4. **Update `.env.example`**: Add OpenAI API key and model config.

### Adding RSS Feeds
1. Edit `config/feeds.json`: Add source object with name, url, enabled, priority.
2. Higher priority = processed first.
3. Test feed URL is accessible.

### Changing Schedule
Edit `.github/workflows/daily-digest.yml`:
```yaml
schedule:
  - cron: '0 7 * * *'  # Run at 7 AM UTC
```
Use [crontab.guru](https://crontab.guru/) to generate cron expressions.

## Debugging Tips

- **Check logs**: Loguru logs to stderr with timestamps and line numbers.
- **Test mode**: `uv run test-local` limits concurrent API calls to 2 for fast iteration.
- **Inspect output**: Check `docs/index.html` after running.
- **Feed issues**: Check `config/feeds.json` for enabled/URL, verify feeds are accessible.
- **GitHub Actions logs**: Check Actions tab in GitHub for CI failures.

## Important Notes

- **Never commit `.env`** (contains API keys).
- **GitHub Pages** deploys from `docs/` directory (GitHub Actions workflow pushes there).
- **localStorage** state is per-browser, no sync across devices (by design for privacy).
- **RSS feeds can be flaky** — error handling is critical, partial results expected.
- **Cost**: ~$0.15/day for 100 articles/day using Claude 3.5 Sonnet (~$4.50/month).

## Customization Philosophy

- **Configuration over code**: Use JSON and Markdown files, not hardcoded values.
- **Prompts are editable**: Users should tune AI behavior without touching Python.
- **Mobile-first**: Templates prioritize responsive design.
- **Low maintenance**: GitHub Actions + static hosting, no servers to manage.
- **Privacy-respecting**: Client-side state with localStorage, no tracking.

## File Organization

```
nus/
├── .github/workflows/
│   └── daily-digest.yml          # GitHub Actions schedule
├── config/
│   └── feeds.json                # RSS feed sources
├── prompts/
│   └── categorization.md         # Claude prompt (user-editable)
├── src/nus/
│   ├── main.py                   # Entry point & DI container init
│   ├── container.py              # Dependency injection wiring
│   ├── orchestrator.py           # Pipeline coordinator
│   ├── fetcher.py                # RSS fetching
│   ├── base_analyzer.py          # Abstract AI analyzer interface
│   ├── analyzers.py              # Anthropic & Gemini implementations
│   ├── renderer.py               # HTML generation
│   ├── models.py                 # Data classes
│   ├── config.py                 # Settings management & validation
│   └── exceptions.py             # Custom exceptions
├── templates/
│   └── digest.html               # Jinja2 template
├── docs/                         # GitHub Pages output
├── pyproject.toml                # Project metadata & scripts
└── README.md                     # User guide
```
