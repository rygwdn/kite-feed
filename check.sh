#!/bin/bash
# Run all linting and validation checks

set -e  # Exit on error

echo "=== Running All Checks ==="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: uv is not installed. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
    exit 1
fi

# Install dependencies if needed
echo "1. Installing dependencies..."
uv sync --dev > /dev/null 2>&1
echo -e "   ${GREEN}✓ Dependencies installed${NC}"
echo ""

# Python syntax check
echo "2. Python Syntax Check:"
if uv run python3 -m py_compile process_kite.py generate_rss.py generate_html.py generate_utils.py 2>&1; then
    echo -e "   ${GREEN}✓ Syntax check passed${NC}"
else
    echo -e "   ${RED}✗ Syntax check failed${NC}"
    exit 1
fi
echo ""

# Black formatting check
echo "3. Black Formatting Check:"
if uv run black --check --diff . > /dev/null 2>&1; then
    echo -e "   ${GREEN}✓ Black formatting check passed${NC}"
else
    echo -e "   ${YELLOW}⚠ Code formatting issues found. Run 'uv run black .' to fix${NC}"
    uv run black --check --diff . 2>&1 | head -20
    exit 1
fi
echo ""

# Flake8 critical checks
echo "4. Flake8 Critical Checks:"
if uv run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics > /dev/null 2>&1; then
    echo -e "   ${GREEN}✓ Critical flake8 checks passed${NC}"
else
    echo -e "   ${RED}✗ Critical flake8 checks failed${NC}"
    uv run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    exit 1
fi
echo ""

# Flake8 all checks (warnings acceptable)
echo "5. Flake8 All Checks:"
FLAKE8_OUTPUT=$(uv run flake8 . --count --exit-zero --statistics 2>&1)
FLAKE8_COUNT=$(echo "$FLAKE8_OUTPUT" | grep -E "^[0-9]+" | head -1 || echo "0")
if [ "$FLAKE8_COUNT" != "0" ]; then
    echo -e "   ${YELLOW}⚠ Found $FLAKE8_COUNT issues (warnings acceptable)${NC}"
    echo "$FLAKE8_OUTPUT" | tail -5
else
    echo -e "   ${GREEN}✓ No flake8 issues found${NC}"
fi
echo ""

# Mypy type check
echo "6. Mypy Type Check:"
if uv run mypy --ignore-missing-imports --no-strict-optional --follow-imports=silent process_kite.py generate_rss.py generate_html.py generate_utils.py 2>&1 | grep -q "Success"; then
    echo -e "   ${GREEN}✓ Type check passed${NC}"
else
    echo -e "   ${YELLOW}⚠ Type check completed with warnings${NC}"
    uv run mypy --ignore-missing-imports --no-strict-optional --follow-imports=silent process_kite.py generate_rss.py generate_html.py generate_utils.py 2>&1 | tail -5
fi
echo ""

# Config validation
echo "7. Config Validation:"
if uv run python3 -c "import json; json.load(open('config.json'))" > /dev/null 2>&1; then
    echo -e "   ${GREEN}✓ Config validation passed${NC}"
else
    echo -e "   ${RED}✗ Config validation failed${NC}"
    exit 1
fi
echo ""

# Import validation
echo "8. Import Validation:"
if uv run python3 -c "import process_kite; import generate_rss; import generate_html; import generate_utils" > /dev/null 2>&1; then
    echo -e "   ${GREEN}✓ All imports successful${NC}"
else
    echo -e "   ${RED}✗ Import validation failed${NC}"
    exit 1
fi
echo ""

echo -e "${GREEN}=== All Checks Completed Successfully ===${NC}"
