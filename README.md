# Kite Feed Generator

Generate HTML and RSS feeds from Kagi Kite stories.

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

### Run Scripts

```bash
# Process Kite feeds
uv run python3 process_kite.py > processed_stories.json

# Generate RSS feed
uv run python3 generate_rss.py < processed_stories.json > feed.xml

# Generate HTML pages
uv run python3 generate_html.py < processed_stories.json
```

## Project Structure

- `process_kite.py`: Processes Kagi Kite feeds
- `generate_html.py`: Generates HTML pages
- `generate_rss.py`: Generates RSS feed
- `generate_utils.py`: Shared utilities (date formatting, story processing, etc.)
- `check_all.py`: Check script run via `uv run check`
- `config.json`: Configuration file
- `pyproject.toml`: Project configuration, dependencies, and scripts

## CI/CD

The CI workflow automatically runs `uv run check` on every push and pull request to `main`.
