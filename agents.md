# Agent Configuration

Run checks and workflows via `uv`:

```bash
# Run checks
uv run ruff check .          # Linting
uv run ruff format --check . # Format check
uv run ty check              # Type checking

# Format code
uv run ruff format .

# Run processing workflow
uv run process
```
