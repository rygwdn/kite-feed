#!/usr/bin/env python3
"""
Generate HTML pages for individual stories using Jinja templates.
"""

import json
import os
import sys

from generate_utils import (
    format_date_html,
    get_jinja_env,
    process_stories_for_output,
)


def generate_story_html(story: dict, config: dict) -> str:
    """Generate a complete HTML page for a story using Jinja template."""
    env = get_jinja_env()
    template = env.get_template("story.html")

    story_dict = dict(story)
    story_dict["heading_level"] = 1  # For HTML pages (h1, h2, etc.)

    return template.render(story=story_dict, config=config)


def generate_index_html(stories: list, config: dict) -> str:
    """Generate an index HTML page listing all stories using Jinja template."""
    env = get_jinja_env()
    template = env.get_template("index.html")

    story_data, story_html_urls = process_stories_for_output(stories, config, format_date_html, heading_level=1)

    return template.render(stories=story_data, story_html_urls=story_html_urls, config=config)


if __name__ == "__main__":
    from datetime import datetime

    print(f"[LOG] generate_html.py started at: {datetime.now().isoformat()}", file=sys.stderr)

    config = json.load(open("config.json"))
    print("[LOG] Config loaded from config.json", file=sys.stderr)

    stories = json.load(sys.stdin)
    print(f"[LOG] Loaded {len(stories)} stories from stdin", file=sys.stderr)

    # Create stories directory
    stories_dir = "stories"
    os.makedirs(stories_dir, exist_ok=True)
    print(f"[LOG] Stories directory: {stories_dir} (exists: {os.path.exists(stories_dir)})", file=sys.stderr)

    # Get the URLs that will be used in the index (to ensure filenames match)
    _, story_html_urls = process_stories_for_output(stories, config, format_date_html, heading_level=1)
    print(f"[LOG] Generated {len(story_html_urls)} story URLs", file=sys.stderr)

    # Extract slugs from URLs to ensure consistency
    base_url = config.get("site", {}).get("base_url", "https://example.com")
    print(f"[LOG] Base URL: {base_url}", file=sys.stderr)

    # Generate individual story pages
    generated_count = 0
    for i, story in enumerate(stories):
        # Extract slug from the URL that will be used in index
        story_url = story_html_urls[i]
        # Remove base_url and /stories/ prefix and .html suffix
        slug_from_url = story_url.replace(f"{base_url}/stories/", "").replace(".html", "")

        filename = f"{stories_dir}/{slug_from_url}.html"

        html = generate_story_html(story, config)
        html_size = len(html)

        # Log first few stories
        if i < 3:
            print(f"[LOG] Generating story {i + 1}: {filename}", file=sys.stderr)
            print(f"[LOG]   - Title: {story.get('title', 'N/A')[:50]}", file=sys.stderr)
            print(f"[LOG]   - HTML size: {html_size} characters", file=sys.stderr)

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)

            # Verify write
            if os.path.exists(filename):
                actual_size = os.path.getsize(filename)
                if actual_size > 0:
                    generated_count += 1
                    if i < 3:
                        print(f"[LOG]   - File written: {actual_size} bytes", file=sys.stderr)
                else:
                    print(f"[LOG]   - WARNING: File {filename} is empty!", file=sys.stderr)
            else:
                print(f"[LOG]   - ERROR: File {filename} was not created!", file=sys.stderr)
        except Exception as e:
            print(f"[LOG]   - ERROR writing {filename}: {e}", file=sys.stderr)
            import traceback

            traceback.print_exc(file=sys.stderr)

    print(f"[LOG] Generated {generated_count}/{len(stories)} story pages", file=sys.stderr)

    # Generate index page
    print("[LOG] Generating index.html...", file=sys.stderr)
    index_html = generate_index_html(stories, config)
    index_size = len(index_html)
    print(f"[LOG] Index HTML size: {index_size} characters", file=sys.stderr)

    try:
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(index_html)

        # Verify write
        if os.path.exists("index.html"):
            actual_size = os.path.getsize("index.html")
            print(f"[LOG] index.html written: {actual_size} bytes", file=sys.stderr)
            if actual_size == 0:
                print("[LOG] WARNING: index.html is empty!", file=sys.stderr)
        else:
            print("[LOG] ERROR: index.html was not created!", file=sys.stderr)
    except Exception as e:
        print(f"[LOG] ERROR writing index.html: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)

    print(f"[LOG] Generated {len(stories)} story pages and index.html", file=sys.stderr)
