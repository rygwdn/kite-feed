#!/usr/bin/env python3
"""
Generate RSS feed from processed Kagi Kite stories using Jinja templates.
"""

import json
import sys
from datetime import UTC, datetime

from generate_utils import (
    format_date_rss,
    get_jinja_env,
    process_stories_for_output,
)


def generate_rss(stories: list, config: dict) -> str:
    """Generate RSS XML from stories using Jinja template."""
    env = get_jinja_env()
    template = env.get_template("rss.xml")

    story_data, story_html_urls = process_stories_for_output(stories, config, format_date_rss, heading_level=2)

    build_date = datetime.now(UTC).strftime("%a, %d %b %Y %H:%M:%S +0000")

    return template.render(stories=story_data, story_html_urls=story_html_urls, config=config, build_date=build_date)


if __name__ == "__main__":
    from datetime import datetime

    print(f"[LOG] generate_rss.py started at: {datetime.now().isoformat()}", file=sys.stderr)

    config = json.load(open("config.json"))
    print("[LOG] Config loaded from config.json", file=sys.stderr)

    stories = json.load(sys.stdin)
    print(f"[LOG] Loaded {len(stories)} stories from stdin", file=sys.stderr)

    rss_xml = generate_rss(stories, config)
    rss_size = len(rss_xml)
    print(f"[LOG] Generated RSS XML: {rss_size} characters", file=sys.stderr)

    # Log first few lines of RSS for verification
    rss_lines = rss_xml.split("\n")[:5]
    print("[LOG] RSS preview (first 5 lines):", file=sys.stderr)
    for line in rss_lines:
        print(f"[LOG]   {line[:80]}", file=sys.stderr)

    print(rss_xml)
