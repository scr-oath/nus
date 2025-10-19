# NUS Project Instructions for Claude

## Project Overview

NUS is an AI-powered daily news curation system that:
- Fetches RSS feeds from quality news sources
- Uses Claude API to categorize and filter articles
- Generates a mobile-friendly static HTML digest
- Deploys automatically via GitHub Actions to GitHub Pages

## Code Style & Preferences

- **Language**: Python 3.11+ with modern async patterns
- **Dependency Management**: Use `uv` exclusively (not pip/poetry/conda)
- **Type Hints**: Required on all function signatures
- **Code Quality**: Follow the architecture from python-pro agent
- **Async**: Use `httpx.AsyncClient` and `asyncio` for concurrency
- **Logging**: Use `loguru` for all logging

## Key Conventions

1. **Scripts**: Defined in `pyproject.toml`, run with `uv run <script-name>`
2. **Configuration**: External files (JSON/Markdown) over hardcoded values
3. **Error Handling**: Graceful degradation (partial results on failures)
4. **Testing**: Local testing with `uv run test-local` before pushing

## File Organization

- `src/nus/`: All Python source code
- `config/`: RSS feeds and settings
- `prompts/`: Claude prompt templates (editable by user)
- `templates/`: Jinja2 HTML templates
- `docs/`: Generated output for GitHub Pages
- `.github/workflows/`: GitHub Actions automation

## When Making Changes

### Modifying Python Code
- Always maintain type hints
- Update docstrings if changing behavior
- Keep async patterns consistent
- Test locally before committing

### Adjusting AI Behavior
- Edit `prompts/categorization.md` (this is the main tuning knob)
- Don't hardcode prompts in Python code
- Ensure JSON response format is maintained

### Adding RSS Feeds
- Edit `config/feeds.json`
- Higher priority = processed first
- Test feed URL accessibility before adding

### Changing Schedule
- Edit `.github/workflows/daily-digest.yml`
- Use crontab syntax for schedule
- Remember times are in UTC

## Common Tasks

### Adding a New Feature
1. Update relevant module in `src/nus/`
2. Add configuration to `config.py` if needed
3. Update README with usage instructions
4. Test locally with `uv run generate-digest`

### Debugging
1. Check logs output by loguru
2. Run `uv run test-local` for reduced API calls
3. Inspect `docs/index.html` for output
4. Review GitHub Actions logs for CI issues

### Performance Tuning
- Adjust `MAX_CONCURRENT_FEEDS` for fetch speed
- Adjust `MAX_CONCURRENT_API_CALLS` for API rate limits
- Monitor API costs (check Anthropic console)

## Important Notes

- **Never commit `.env`** (contains API keys)
- **Always use `uv run`** for running scripts
- **GitHub Pages** deploys from `docs/` directory
- **localStorage** state is browser-specific (no sync)
- **RSS feeds** can be flaky - error handling is critical

## User's Goals

The user wants to:
- Stay informed without wasting time on clickbait
- Get balanced perspectives (avoid echo chambers)
- Understand "why people care" about sports (even though they don't)
- Discover productivity tools relevant to their work
- Form a daily habit of reading quality news

## Customization Philosophy

- Prompts should be easily editable (external files)
- Configuration over code changes
- Mobile-first design
- Privacy-respecting (localStorage, no tracking)
- Low maintenance (GitHub Actions, static hosting)
