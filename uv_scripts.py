#!/usr/bin/env python3
"""
UV script runner - allows 'uv run <script>' to work.
This file provides entry points for common development tasks.
"""

import sys
import subprocess


def run_check():
    """Run all checks."""
    from check_all import main
    main()


def run_format():
    """Format code with black."""
    result = subprocess.run(["black", "."], check=False)
    sys.exit(result.returncode)


def run_process():
    """Run the processing workflow."""
    from process_workflow import main
    main()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python uv_scripts.py <command>")
        print("Commands: check, format, process")
        sys.exit(1)
    
    command = sys.argv[1]
    if command == "check":
        run_check()
    elif command == "format":
        run_format()
    elif command == "process":
        run_process()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
