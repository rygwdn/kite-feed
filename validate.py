#!/usr/bin/env python3
"""
Validation script that runs the same checks as CI.
Run this before committing to ensure CI will pass.

Usage:
    python3 validate.py
    # or with uv:
    uv run python3 validate.py
"""

import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def print_header(text: str) -> None:
    """Print a section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")


def print_step(number: int, text: str) -> None:
    """Print a step header."""
    print(f"{Colors.BOLD}{number}. {text}{Colors.RESET}")
    print(f"{'-' * 70}")


def print_success(text: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text: str) -> None:
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def run_command(cmd: list[str], description: str, allow_failure: bool = False) -> bool:
    """Run a command and return success status."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            print_success(f"{description}: PASS")
            if result.stdout.strip():
                print(f"  {result.stdout.strip()}")
            return True
        else:
            if allow_failure:
                print_warning(f"{description}: SKIPPED (non-blocking)")
                if result.stderr.strip():
                    print(f"  {result.stderr.strip()}")
                return True
            else:
                print_error(f"{description}: FAIL")
                if result.stdout.strip():
                    print(f"  {result.stdout.strip()}")
                if result.stderr.strip():
                    print(f"  {result.stderr.strip()}")
                return False
    except FileNotFoundError:
        print_error(f"{description}: Command not found - {' '.join(cmd)}")
        return False
    except Exception as e:
        print_error(f"{description}: Error - {e}")
        return False


def check_ruff_linting() -> bool:
    """Check code with ruff linter."""
    print_step(1, "Ruff Linting")
    return run_command(["uv", "run", "ruff", "check", "."], "Linting check")


def check_ruff_formatting() -> bool:
    """Check code formatting with ruff."""
    print_step(2, "Ruff Formatting")
    return run_command(["uv", "run", "ruff", "format", "--check", "."], "Format check")


def check_type_checking() -> bool:
    """Run type checking (non-blocking)."""
    print_step(3, "Type Checking")
    return run_command(["uv", "run", "ty", "check"], "Type check", allow_failure=True)


def generate_site() -> bool:
    """Generate the site."""
    print_step(4, "Site Generation")

    # Clean up old files
    files_to_remove = ["feed.xml", "index.html", "processed_stories.json"]
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"  Cleaned up old {file}")

    if os.path.exists("stories"):
        import shutil

        shutil.rmtree("stories")
        print("  Cleaned up old stories/ directory")

    # Generate site
    result = subprocess.run(["uv", "run", "process"], capture_output=True, text=True, check=False)

    if result.returncode == 0:
        print_success("Site generation: PASS")
        return True
    else:
        print_error("Site generation: FAIL")
        if result.stderr:
            # Print last 20 lines of stderr
            stderr_lines = result.stderr.strip().split("\n")
            for line in stderr_lines[-20:]:
                print(f"  {line}")
        return False


def verify_generated_files() -> bool:
    """Verify that all required files were generated."""
    print_step(5, "File Verification")

    all_ok = True

    # Check key files
    key_files = ["processed_stories.json", "feed.xml", "index.html"]
    for file in key_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print_success(f"{file} exists ({size:,} bytes)")
        else:
            print_error(f"{file} MISSING!")
            all_ok = False

    # Check stories directory
    if os.path.exists("stories") and os.path.isdir("stories"):
        story_files = list(Path("stories").glob("*.html"))
        story_count = len(story_files)
        if story_count > 0:
            print_success(f"stories/ directory exists with {story_count} HTML files")
        else:
            print_warning("stories/ directory exists but is empty")
    else:
        print_error("stories/ directory MISSING!")
        all_ok = False

    return all_ok


def validate_rss_feed() -> bool:
    """Validate RSS feed structure."""
    print_step(6, "RSS Feed Validation")

    if not os.path.exists("feed.xml"):
        print_error("feed.xml not found - cannot validate")
        return False

    try:
        # Register namespaces
        ET.register_namespace("media", "http://search.yahoo.com/mrss/")
        ET.register_namespace("content", "http://purl.org/rss/1.0/modules/content/")
        ET.register_namespace("atom", "http://www.w3.org/2005/Atom")

        # Parse XML
        tree = ET.parse("feed.xml")
        root = tree.getroot()

        # Check RSS version
        rss_version = root.attrib.get("version")
        if rss_version == "2.0":
            print_success(f"RSS version: {rss_version}")
        else:
            print_error(f"Invalid RSS version: {rss_version}")
            return False

        # Check for Media RSS namespace in raw XML
        with open("feed.xml") as f:
            first_lines = f.read(500)
            has_media = 'xmlns:media="http://search.yahoo.com/mrss/"' in first_lines

        if has_media:
            print_success("Media RSS namespace declared")
        else:
            print_warning("Media RSS namespace not found")

        # Count items and thumbnails
        items = root.findall(".//item")
        thumbnails = root.findall(".//{http://search.yahoo.com/mrss/}thumbnail")

        print_success(f"RSS items: {len(items)}")
        print_success(f"Items with media:thumbnail: {len(thumbnails)}")

        if len(items) > 0:
            coverage = (len(thumbnails) / len(items)) * 100
            print_success(f"Thumbnail coverage: {coverage:.1f}%")
        else:
            print_warning("No RSS items found")

        # Check required channel elements
        channel = root.find("channel")
        if channel is not None:
            required_elements = ["title", "link", "description"]
            for elem in required_elements:
                if channel.find(elem) is not None:
                    print_success(f"Required element present: {elem}")
                else:
                    print_error(f"Missing required element: {elem}")
                    return False

        # Validate that items have required elements
        items_valid = True
        for i, item in enumerate(items[:3]):  # Check first 3 items
            title = item.find("title")
            link = item.find("link")
            if title is None or not title.text:
                print_error(f"Item {i + 1} missing title")
                items_valid = False
            if link is None or not link.text:
                print_error(f"Item {i + 1} missing link")
                items_valid = False

        if items_valid:
            print_success("All checked items have required elements")

        return True

    except ET.ParseError as e:
        print_error(f"XML parsing error: {e}")
        return False
    except Exception as e:
        print_error(f"Validation error: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_html_semantic_structure() -> bool:
    """Check that HTML uses semantic elements."""
    print_step(7, "HTML Semantic Structure")

    all_ok = True

    # Check index.html
    if os.path.exists("index.html"):
        with open("index.html") as f:
            index_html = f.read()

        if '<figure class="story-thumbnail">' in index_html:
            print_success("index.html uses semantic <figure> for thumbnails")
        else:
            print_warning("index.html doesn't use <figure> for thumbnails")

        if 'loading="lazy"' in index_html:
            print_success("index.html uses lazy loading")
        else:
            print_warning("index.html doesn't use lazy loading")
    else:
        print_error("index.html not found")
        all_ok = False

    # Check story files
    story_files = list(Path("stories").glob("*.html")) if os.path.exists("stories") else []
    if story_files:
        with open(story_files[0]) as f:
            story_html = f.read()

        if "<figure class='image'>" in story_html:
            print_success("Story pages use semantic <figure> for images")
        else:
            print_warning("Story pages don't use <figure> for images")

        if "<figcaption class='caption'>" in story_html:
            print_success("Story pages use semantic <figcaption>")
        else:
            print_warning("Story pages don't use <figcaption>")

        if "figure.image" in story_html:
            print_success("Story pages have CSS for semantic elements")
        else:
            print_warning("Story pages missing CSS for semantic elements")
    else:
        print_warning("No story files found to check")

    return all_ok


def main() -> int:
    """Run all validation checks."""
    print_header("VALIDATION SCRIPT - Running All CI Checks")

    checks = [
        ("Ruff Linting", check_ruff_linting),
        ("Ruff Formatting", check_ruff_formatting),
        ("Type Checking", check_type_checking),
        ("Site Generation", generate_site),
        ("File Verification", verify_generated_files),
        ("RSS Feed Validation", validate_rss_feed),
        ("HTML Semantic Structure", check_html_semantic_structure),
    ]

    results = {}

    for name, check_func in checks:
        try:
            results[name] = check_func()
            print()  # Add spacing between checks
        except Exception as e:
            print_error(f"{name} crashed: {e}")
            import traceback

            traceback.print_exc()
            results[name] = False
            print()

    # Print summary
    print_header("VALIDATION SUMMARY")

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for name, result in results.items():
        if result:
            print_success(f"{name}: PASS")
        else:
            print_error(f"{name}: FAIL")

    print()
    print(f"{Colors.BOLD}Results: {passed}/{total} checks passed{Colors.RESET}")

    if passed == total:
        print()
        print_success("All validation checks passed! ✨")
        print()
        print(f"{Colors.GREEN}Your changes are ready to commit and push.{Colors.RESET}")
        return 0
    else:
        print()
        print_error(f"{total - passed} check(s) failed!")
        print()
        print(f"{Colors.RED}Please fix the issues before committing.{Colors.RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
