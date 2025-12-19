#!/usr/bin/env python3
"""
Run the complete processing workflow:
1. Process Kite feeds -> processed_stories.json
2. Generate RSS feed -> feed.xml
3. Generate HTML pages -> index.html and stories/*.html
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Run the complete processing workflow."""
    print("=== Running Processing Workflow ===\n")

    # Step 1: Process Kite feeds
    print("1. Processing Kite feeds...")
    try:
        with open("processed_stories.json", "w", encoding="utf-8") as f:
            result = subprocess.run(
                ["python", "process_kite.py"],
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
        print("   ✓ Processed stories saved to processed_stories.json")
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Failed to process Kite feeds: {e.stderr}")
        sys.exit(1)

    # Step 2: Generate RSS feed
    print("\n2. Generating RSS feed...")
    try:
        with open("processed_stories.json", "r", encoding="utf-8") as stdin_file:
            with open("feed.xml", "w", encoding="utf-8") as stdout_file:
                result = subprocess.run(
                    ["python", "generate_rss.py"],
                    stdin=stdin_file,
                    stdout=stdout_file,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True,
                )
        print("   ✓ RSS feed saved to feed.xml")
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Failed to generate RSS feed: {e.stderr}")
        sys.exit(1)

    # Step 3: Generate HTML pages
    print("\n3. Generating HTML pages...")
    try:
        with open("processed_stories.json", "r", encoding="utf-8") as stdin_file:
            result = subprocess.run(
                ["python", "generate_html.py"],
                stdin=stdin_file,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
        print("   ✓ HTML pages generated")
        if result.stderr:
            print(f"   {result.stderr.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Failed to generate HTML pages: {e.stderr}")
        sys.exit(1)

    print("\n=== Processing Workflow Completed Successfully ===")


if __name__ == "__main__":
    main()
