# NUS - Daily News Curator

An AI-powered daily news curation system that helps you stay informed without the noise. NUS (plural of the Greek letter ν, "nu") fetches news from quality sources, uses Claude AI to categorize and filter articles, and generates a mobile-friendly daily digest.

## Features

- **AI-Powered Curation**: Claude API analyzes and categorizes articles into:
  - **Must Know**: Critical news and events
  - **Sports Context**: Sports news with "why people care" explanations
  - **Tech & Tools**: Technology and productivity news
  - **Fun Stuff**: Interesting diversions and cultural content

- **Smart Filtering**:
  - Clickbait detection and removal
  - Duplicate article elimination
  - Balanced perspective (anti-bubble)
  - Quality source prioritization

- **Mobile-Friendly**:
  - Responsive design works on all devices
  - Bookmark-able daily page
  - Offline-capable with localStorage
  - Read/unread tracking
  - Save for later functionality

- **Low Maintenance**:
  - GitHub Actions automation
  - Static site hosting on GitHub Pages
  - No server infrastructure needed
  - Easy customization via config files

## Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd nus
cp .env.example .env
```

### 2. Get Anthropic API Key

1. Sign up at [Anthropic Console](https://console.anthropic.com/)
2. Go to API Keys and create a new key
3. Add to `.env`:
   ```bash
   ANTHROPIC_API_KEY=your_api_key_here
   ```

### 3. Install Dependencies

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### 4. Test Locally

```bash
# Generate a test digest
uv run generate-digest

# View the output
open docs/index.html
```

### 5. Configure GitHub Actions

1. Go to your GitHub repository settings
2. Navigate to **Secrets and variables** → **Actions**
3. Add a new secret:
   - Name: `ANTHROPIC_API_KEY`
   - Value: Your Anthropic API key

### 6. Enable GitHub Pages

1. Go to repository **Settings** → **Pages**
2. Set source to **GitHub Actions**
3. The workflow will automatically deploy to `https://<username>.github.io/nus/`

## Configuration

### RSS Feeds

Edit `config/feeds.json` to add/remove news sources:

```json
[
  {
    "name": "Your Source",
    "url": "https://example.com/feed.xml",
    "enabled": true,
    "priority": 10
  }
]
```

### AI Prompt

Edit `prompts/categorization.md` to adjust how Claude categorizes articles. This is where you can:
- Fine-tune category definitions
- Adjust clickbait detection criteria
- Change the "why people care" framing for sports
- Modify balance/bubble-avoidance instructions

### Environment Variables

All settings can be overridden in `.env`:

```bash
# API Configuration
ANTHROPIC_API_KEY=your_key
CLAUDE_MODEL=claude-3-5-sonnet-20241022
MAX_TOKENS=1024
TEMPERATURE=0.3

# Performance
MAX_CONCURRENT_FEEDS=20
MAX_CONCURRENT_API_CALLS=5
FETCH_TIMEOUT=30

# Features
FILTER_CLICKBAIT=true
DEDUPLICATE_ARTICLES=true
```

### Schedule

Edit `.github/workflows/daily-digest.yml` to change the schedule:

```yaml
on:
  schedule:
    # Run at 7 AM UTC (2 AM Pacific, 5 AM Eastern)
    - cron: '0 7 * * *'
```

Use [crontab.guru](https://crontab.guru/) to generate cron schedules.

## Usage

### Automatic Daily Generation

Once configured, GitHub Actions will automatically:
1. Run at your scheduled time
2. Fetch and analyze articles
3. Generate the HTML digest
4. Deploy to GitHub Pages
5. Commit the changes to your repo

### Manual Trigger

You can manually trigger a digest from GitHub:
1. Go to **Actions** tab
2. Select "Generate Daily News Digest"
3. Click **Run workflow**

### Local Development

```bash
# Full digest generation
uv run generate-digest

# Test mode (fewer API calls)
uv run test-local

# View the output
open docs/index.html
```

### Bookmarking

Add this to your phone's home screen or browser bookmarks:
```
https://<username>.github.io/nus/
```

## How It Works

1. **Fetch**: Async fetching of RSS feeds from configured sources (httpx + asyncio)
2. **Analyze**: Claude API categorizes articles and detects clickbait
3. **Filter**: Removes duplicates, clickbait, and low-quality content
4. **Render**: Generates static HTML with Jinja2 templates
5. **Deploy**: GitHub Actions publishes to GitHub Pages
6. **Track**: Client-side JavaScript uses localStorage for read/save state

## Project Structure

```
nus/
├── .github/workflows/      # GitHub Actions
├── config/                 # RSS feeds configuration
├── prompts/                # Claude prompt templates
├── src/nus/                # Python source code
│   ├── main.py            # Entry point
│   ├── fetcher.py         # RSS fetching
│   ├── analyzer.py        # Claude integration
│   ├── orchestrator.py    # Workflow coordination
│   └── ...
├── templates/              # HTML templates
├── docs/                   # Generated output (GitHub Pages)
└── pyproject.toml          # Project configuration
```

## Customization

### Adding New Categories

1. Edit `src/nus/models.py` to add to the `Category` enum
2. Update `prompts/categorization.md` with the new category definition
3. Adjust `templates/digest.html` styling if needed

### Changing Appearance

Edit `templates/digest.html`:
- Modify CSS variables in `:root` for colors
- Adjust layout/structure in HTML
- Add new JavaScript features

### Adjusting AI Behavior

The AI prompt in `prompts/categorization.md` is the key to customization:
- Make it more/less strict about clickbait
- Adjust category criteria
- Add domain-specific knowledge
- Tune the balance requirements

## Troubleshooting

### GitHub Action Fails

1. Check that `ANTHROPIC_API_KEY` is set in repository secrets
2. Verify API key has sufficient credits
3. Check workflow logs for specific errors

### No Articles Generated

1. Verify RSS feed URLs are accessible
2. Check that feeds are enabled in `config/feeds.json`
3. Look at logs for fetch errors

### Articles Not Categorized Correctly

1. Adjust the prompt in `prompts/categorization.md`
2. Increase `TEMPERATURE` for more creative categorization
3. Add examples to the prompt

### Read/Save State Not Persisting

- This uses localStorage, which is per-browser
- Clearing browser data will reset state
- State doesn't sync across devices (by design for privacy)

## Cost Estimate

Using Claude 3.5 Sonnet:
- ~100 articles/day × $0.003/1K tokens × ~500 tokens/article = **~$0.15/day**
- Monthly: **~$4.50**
- New accounts get **$5 in free credits**

Tips to reduce costs:
- Reduce number of feeds
- Lower `MAX_CONCURRENT_API_CALLS`
- Use Claude 3 Haiku for cheaper analysis (~70% less)

## License

MIT

## Contributing

This is a personal project, but feel free to fork and customize for your own use!
