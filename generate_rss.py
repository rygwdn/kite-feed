#!/usr/bin/env python3
"""
Generate RSS feed from processed Kagi Kite stories using Jinja templates.
"""

import json
import sys
from datetime import datetime, timezone
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

    build_date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

    return template.render(stories=story_data, story_html_urls=story_html_urls, config=config, build_date=build_date)


if __name__ == "__main__":
    config = json.load(open("config.json"))
    stories = json.load(sys.stdin)

    rss_xml = generate_rss(stories, config)
    print(rss_xml)
