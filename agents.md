# Agent Configuration for Kite Feed Generator

## Code Quality Requirements

Before committing or submitting code, ensure:

1. **Python Syntax Validation**: All Python files must have valid syntax
   - Run: `python3 -m py_compile *.py`
   - Files to check: `process_kite.py`, `generate_rss.py`, `generate_html.py`, `generate_utils.py`, `process_workflow.py`, `check_all.py`, `uv_scripts.py`

2. **Code Formatting**: Code must be formatted with Black
   - Run: `uv run format` or `black --check --diff .`
   - Configuration: `pyproject.toml` (line-length: 127)

3. **Linting**: Code must pass flake8 checks
   - Run: `flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`
   - Configuration: `.flake8` and `pyproject.toml`

4. **Type Checking**: Type hints should be checked with mypy
   - Run: `mypy --ignore-missing-imports --no-strict-optional --follow-imports=silent *.py`
   - Configuration: `pyproject.toml`

5. **Config Validation**: `config.json` must be valid JSON
   - Run: `python3 -c "import json; json.load(open('config.json'))"`

6. **Script Validation**: All scripts must be importable and executable
   - Ensure all imports resolve correctly
   - Ensure scripts can be run with `python3 script.py` or `uv run <script>`

## Import Dependencies

When adding new imports or dependencies:
- Update `pyproject.toml` if adding external packages (use `uv add <package>` for runtime deps, `uv add --dev <package>` for dev deps)
- Ensure all imports are used (no unused imports)
- Use type hints where appropriate
- Prefer importing functions directly rather than using subprocess when possible

## File Structure

- `process_kite.py`: Processes Kagi Kite feeds - exports `load_config()` and `process_kite_feeds(config)`
- `generate_html.py`: Generates HTML pages - exports `generate_story_html()`, `generate_index_html()`
- `generate_rss.py`: Generates RSS feed - exports `generate_rss(stories, config)`
- `generate_utils.py`: Shared utilities (date formatting, story processing, URL generation) - exports `get_story_slug()`, `get_story_url()`, `format_date_html()`, `format_date_rss()`, `process_stories_for_output()`, `get_jinja_env()`
- `process_workflow.py`: Complete processing workflow - imports and calls other modules directly
- `check_all.py`: Validation checks script
- `uv_scripts.py`: Entry points for `uv run` commands

## Testing Before Commit

Always run the check command before committing:
```bash
# Run all checks at once
uv run check

# Or format code automatically
uv run format
```

The `uv run check` command runs all validation checks:
1. Python syntax validation
2. Black formatting check
3. Flake8 critical checks
4. Flake8 all checks (warnings acceptable)
5. Mypy type checking
6. Config validation
7. Import validation

## Development Setup

This project uses `uv` for dependency management:

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies (including dev dependencies)
uv sync --dev

# Run processing workflow
uv run process

# Run all checks
uv run check

# Format code
uv run format
```

## Processing Workflow

The processing workflow (`uv run process`) runs:
1. Process Kite feeds → `processed_stories.json`
2. Generate RSS feed → `feed.xml`
3. Generate HTML pages → `index.html` and `stories/*.html`

The workflow uses direct imports rather than subprocess calls for better error handling and performance.

## CI/CD

The CI workflow (`.github/workflows/ci.yml`) uses `uv` and runs `uv run check` automatically on:
- Push to `main` branch
- Pull requests to `main` branch

The update-feed workflow (`.github/workflows/update-feed.yml`) runs `uv run process` to generate and deploy the feed.

Ensure all CI checks pass before merging.
