#!/usr/bin/env python3
"""
Generate HTML pages for individual stories using Jinja templates.
"""

import json
import sys
import os
from datetime import datetime, timezone
from urllib.parse import quote
from jinja2 import Environment, FileSystemLoader, select_autoescape


def format_date(timestamp) -> str:
    """Format timestamp for display."""
    try:
        if isinstance(timestamp, (int, float)):
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d")
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
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
        return ""
    except:
        return ""


def generate_story_html(story: dict, config: dict) -> str:
    """Generate a complete HTML page for a story using Jinja template."""
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('story.html')
    
    story_dict = dict(story)
    story_dict['heading_level'] = 1  # For HTML pages (h1, h2, etc.)
    
    return template.render(story=story_dict, config=config)


def generate_index_html(stories: list, config: dict) -> str:
    """Generate an index HTML page listing all stories using Jinja template."""
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('index.html')
    
    site_config = config.get("site", {})
    base_url = site_config.get("base_url", "https://example.com")
    
    story_data = []
    story_html_urls = []
    
    for story in stories:
        title = story.get("title", "Untitled")
        story_slug = quote(title.lower().replace(" ", "-")[:50], safe="")
        story_url = f"{base_url}/stories/{story_slug}.html"
        story_html_urls.append(story_url)
        
        # Format publication date
        pub_timestamp = story.get("published")
        pub_date = format_date(pub_timestamp) if pub_timestamp else ""
        
        story_dict = dict(story)
        story_dict['pub_date'] = pub_date
        story_data.append(story_dict)
    
    return template.render(
        stories=story_data,
        story_html_urls=story_html_urls,
        config=config
    )


if __name__ == "__main__":
    config = json.load(open("config.json"))
    stories = json.load(sys.stdin)
    
    # Create stories directory
    os.makedirs("stories", exist_ok=True)
    
    # Generate individual story pages
    for story in stories:
        title = story.get("title", "Untitled")
        story_slug = quote(title.lower().replace(" ", "-")[:50], safe="")
        filename = f"stories/{story_slug}.html"
        
        html = generate_story_html(story, config)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
    
    # Generate index page
    index_html = generate_index_html(stories, config)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    
    print(f"Generated {len(stories)} story pages and index.html", file=sys.stderr)
