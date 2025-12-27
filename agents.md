# Agent Configuration

## Validation Script

**IMPORTANT**: Before committing any changes, always run the validation script to ensure all CI checks will pass:

```bash
python3 validate.py
```

This script runs the same checks as CI:
1. Ruff linting
2. Ruff formatting
3. Type checking (non-blocking)
4. Site generation
5. File verification
6. RSS feed validation (including Media RSS namespace)
7. HTML semantic structure validation

All checks must pass before committing. The script will show a clear success/failure message.

## Manual Checks

If you need to run individual checks:

```bash
# Linting
uv run ruff check .

# Fix linting issues automatically
uv run ruff check --fix .

# Format check
uv run ruff format --check .

# Format code
uv run ruff format .

# Type checking
uv run ty check

# Run processing workflow
uv run process
```

## CI Information

- CI runs on all pushes and PRs to `main` branch
- CI runs the same checks as `validate.py`
- If CI fails due to linting, run `uv run ruff check --fix .` and `uv run ruff format .`
- The site is deployed daily via GitHub Actions to GitHub Pages

## RSS Feed Implementation

The RSS feed includes:
- **Media RSS namespace** (`xmlns:media="http://search.yahoo.com/mrss/"`)
- **media:thumbnail elements** for items with primary images
- **Semantic HTML** using `<figure>` and `<figcaption>` elements

Thumbnails are automatically extracted from `primary_image.url` in the story data.
