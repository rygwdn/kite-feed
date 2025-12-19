#!/usr/bin/env python3
"""
Run all linting and validation checks.
This script is run via 'uv run check'
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description, critical=True):
    """Run a command and return success status."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print(f"  ✓ {description} passed")
            return True
        else:
            print(f"  ✗ {description} failed")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            return False
    except Exception as e:
        print(f"  ✗ {description} failed: {e}")
        return False


def main():
    """Run all checks."""
    print("=== Running All Checks ===\n")

    checks = [
        (
            "python -c \"import py_compile; [py_compile.compile(f) for f in ['process_kite.py', 'generate_rss.py', 'generate_html.py', 'generate_utils.py']]\"",
            "Python Syntax Check",
            True,
        ),
        (
            "black --check --diff .",
            "Black Formatting Check",
            True,
        ),
        (
            "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics",
            "Flake8 Critical Checks",
            True,
        ),
        (
            "flake8 . --count --exit-zero --statistics",
            "Flake8 All Checks",
            False,  # Warnings acceptable
        ),
        (
            "mypy --ignore-missing-imports --no-strict-optional --follow-imports=silent process_kite.py generate_rss.py generate_html.py generate_utils.py",
            "Mypy Type Check",
            False,  # Warnings acceptable
        ),
        (
            "python -c \"import json; json.load(open('config.json'))\"",
            "Config Validation",
            True,
        ),
        (
            'python -c "import process_kite; import generate_rss; import generate_html; import generate_utils"',
            "Import Validation",
            True,
        ),
    ]

    failed_critical = False
    for cmd, description, critical in checks:
        success = run_command(cmd, description, critical)
        if not success and critical:
            failed_critical = True

    print("\n=== Check Summary ===")
    if failed_critical:
        print("✗ Some critical checks failed")
        sys.exit(1)
    else:
        print("✓ All checks completed")
        sys.exit(0)


if __name__ == "__main__":
    main()
