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
    get_story_slug,
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

    # Generate individual story pages
    for story in stories:
        story_slug = get_story_slug(story)
        filename = f"stories/{story_slug}.html"

        html = generate_story_html(story, config)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

    # Generate index page
    index_html = generate_index_html(stories, config)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    print(f"Generated {len(stories)} story pages and index.html", file=sys.stderr)
