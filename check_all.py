#!/usr/bin/env python3
"""
Run all linting and validation checks.
This script is run via 'uv run check'
"""

import subprocess
import sys


def main():
    """Run all checks."""
    print("=== Running All Checks ===\n")

    checks = [
        ("ruff check .", "Ruff linting", True),
        ("ruff format --check .", "Ruff formatting", True),
        ("ty check", "Type checking", False),  # Warnings acceptable for now
        ("python -c \"import json; json.load(open('config.json'))\"", "Config validation", True),
        (
            'python -c "import process_kite; import generate_rss; import generate_html; import generate_utils"',
            "Import validation",
            True,
        ),
    ]

    failed = False
    for cmd, description, critical in checks:
        print(f"\n{description}...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print(f"  ✓ {description} passed")
        else:
            print(f"  ✗ {description} failed")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            if critical:
                failed = True

    print("\n=== Check Summary ===")
    if failed:
        print("✗ Some checks failed")
        sys.exit(1)
    else:
        print("✓ All checks passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
