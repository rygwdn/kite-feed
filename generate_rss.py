#!/usr/bin/env python3
"""
Generate RSS feed from processed Kagi Kite stories using Jinja templates.
"""

import json
import sys
from datetime import datetime, timezone
from urllib.parse import quote
from jinja2 import Environment, FileSystemLoader, select_autoescape


def format_date(timestamp) -> str:
    """Format timestamp for RSS."""
    try:
        if isinstance(timestamp, (int, float)):
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
        elif isinstance(timestamp, str):
            # Try parsing various date formats
            for fmt in [
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d",
                "%Y-%m-%d %H:%M:%S"
            ]:
                try:
                    dt = datetime.strptime(timestamp, fmt)
                    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
                except ValueError:
                    continue
        # Fallback to current time
        return datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    except:
        return datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")


def generate_rss(stories: list, config: dict) -> str:
    """Generate RSS XML from stories using Jinja template."""
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('rss.xml')
    
    site_config = config.get("site", {})
    base_url = site_config.get("base_url", "https://example.com")
    
    # Prepare story data with formatted dates and HTML URLs
    story_data = []
    story_html_urls = []
    
    for story in stories:
        story_title = story.get("title", "Untitled")
        story_slug = quote(story_title.lower().replace(" ", "-")[:50], safe="")
        story_html_url = f"{base_url}/stories/{story_slug}.html"
        story_html_urls.append(story_html_url)
        
        # Format publication date
        pub_timestamp = story.get("published")
        pub_date = format_date(pub_timestamp) if pub_timestamp else datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
        
        story_dict = dict(story)
        story_dict['pub_date'] = pub_date
        story_dict['heading_level'] = 2  # For RSS content (h2, h3, etc.)
        story_data.append(story_dict)
    
    build_date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    
    return template.render(
        stories=story_data,
        story_html_urls=story_html_urls,
        config=config,
        build_date=build_date
    )


if __name__ == "__main__":
    config = json.load(open("config.json"))
    stories = json.load(sys.stdin)
    
    rss_xml = generate_rss(stories, config)
    print(rss_xml)
