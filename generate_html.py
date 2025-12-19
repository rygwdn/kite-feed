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
    config = json.load(open("config.json"))
    stories = json.load(sys.stdin)

    # Create stories directory
    os.makedirs("stories", exist_ok=True)

    # Get the URLs that will be used in the index (to ensure filenames match)
    _, story_html_urls = process_stories_for_output(stories, config, format_date_html, heading_level=1)

    # Extract slugs from URLs to ensure consistency
    base_url = config.get("site", {}).get("base_url", "https://example.com")

    # Generate individual story pages
    for i, story in enumerate(stories):
        # Extract slug from the URL that will be used in index
        story_url = story_html_urls[i]
        # Remove base_url and /stories/ prefix and .html suffix
        slug_from_url = story_url.replace(f"{base_url}/stories/", "").replace(".html", "")

        filename = f"stories/{slug_from_url}.html"

        html = generate_story_html(story, config)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

    # Generate index page
    index_html = generate_index_html(stories, config)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    print(f"Generated {len(stories)} story pages and index.html", file=sys.stderr)
