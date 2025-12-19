# Kite Feed Generator

Generate HTML and RSS feeds from Kagi Kite stories.

This project processes stories from [Kagi Kite](https://kite.kagi.com), combines them from multiple categories, filters duplicates, and generates both HTML pages and an RSS feed for easy consumption.

## Development Setup

This project uses [`uv`](https://github.com/astral-sh/uv) for fast Python package management.

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install Dependencies

```bash
# Install all dependencies (including dev dependencies)
uv sync --dev
```

### Run Checks

Run all linting and validation checks:

```bash
uv run check
```

This runs:
- Python syntax validation
- Black formatting check
- Flake8 linting
- Mypy type checking
- Config validation
- Import validation

### Format Code

```bash
uv run format
```

### Run Processing Workflow

Run the complete processing workflow (process feeds, generate RSS, generate HTML):

```bash
uv run process
```

Or run individual steps:

```bash
# Process Kite feeds
uv run python3 process_kite.py > processed_stories.json

# Generate RSS feed
uv run python3 generate_rss.py < processed_stories.json > feed.xml

# Generate HTML pages
uv run python3 generate_html.py < processed_stories.json
```

## Project Structure

- `process_kite.py`: Processes Kagi Kite feeds, fetches data from multiple categories, filters and merges duplicates
- `generate_html.py`: Generates HTML pages (index and individual story pages)
- `generate_rss.py`: Generates RSS feed XML
- `generate_utils.py`: Shared utilities (date formatting, story processing, URL generation, etc.)
- `process_workflow.py`: Complete processing workflow that orchestrates all steps
- `check_all.py`: Validation checks script run via `uv run check`
- `uv_scripts.py`: Entry points for `uv run` commands
- `config.json`: Configuration file (categories, filters, site settings)
- `pyproject.toml`: Project configuration, dependencies, and scripts
- `.python-version`: Python version pin (3.11)
- `uv.lock`: Locked dependency versions for reproducible builds

## Configuration

Edit `config.json` to customize:
- Which Kite categories to fetch (`feeds.categories`)
- How many stories per category (`feeds.top_n`)
- Filter settings (`filters.enabled`, `filters.min_score`)
- Site metadata (`site.title`, `site.description`, `site.base_url`, etc.)

## CI/CD

The CI workflow (`.github/workflows/ci.yml`) automatically runs `uv run check` on every push and pull request to `main`.

The update-feed workflow (`.github/workflows/update-feed.yml`) runs daily to process feeds and deploy to GitHub Pages.
