#!/usr/bin/env python3
"""
UV script entry points for common development tasks.
"""

import subprocess
import sys


def run_check():
    """Run all checks."""
    from check_all import main

    main()


def run_format():
    """Format code with ruff."""
    result = subprocess.run(["ruff", "format", "."], check=False)
    sys.exit(result.returncode)


def run_process():
    """Run the processing workflow."""
    from process_workflow import main

    main()
