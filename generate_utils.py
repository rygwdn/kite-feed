#!/usr/bin/env python3
"""
Shared utilities for HTML and RSS generation scripts.
"""

from datetime import datetime, timezone
from urllib.parse import quote
from jinja2 import Environment, FileSystemLoader, select_autoescape


def format_date_html(timestamp) -> str:
    """Format timestamp for HTML display."""
    if timestamp is None:
        return ""
    try:
        if isinstance(timestamp, (int, float)):
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d")
        elif isinstance(timestamp, str):
            # Try parsing various date formats
            for fmt in ["%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]:
                try:
                    dt = datetime.strptime(timestamp, fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
        return ""
    except Exception:
        return ""


def format_date_rss(timestamp) -> str:
    """Format timestamp for RSS."""
    if timestamp is None:
        return datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    try:
        if isinstance(timestamp, (int, float)):
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
        elif isinstance(timestamp, str):
            # Try parsing various date formats
            for fmt in ["%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]:
                try:
                    dt = datetime.strptime(timestamp, fmt)
                    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
                except ValueError:
                    continue
        # Fallback to current time
        return datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    except Exception:
        return datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")


def get_story_slug(story: dict) -> str:
    """Generate a URL slug from a story title."""
    title = story.get("title", "Untitled")
    return quote(title.lower().replace(" ", "-")[:50], safe="")


def get_story_url(story: dict, base_url: str) -> str:
    """Generate the HTML URL for a story."""
    story_slug = get_story_slug(story)
    return f"{base_url}/stories/{story_slug}.html"


def get_jinja_env():
    """Create and return a Jinja2 environment."""
    return Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape(["html", "xml"]))


def process_stories_for_output(stories: list, config: dict, date_formatter, heading_level: int = 1):
    """
    Process stories for output (HTML or RSS).
    
    Args:
        stories: List of story dictionaries
        config: Configuration dictionary
        date_formatter: Function to format dates (format_date_html or format_date_rss)
        heading_level: Heading level to set in story dict (1 for HTML, 2 for RSS)
    
    Returns:
        Tuple of (story_data, story_html_urls)
    """
    site_config = config.get("site", {})
    base_url = site_config.get("base_url", "https://example.com")
    
    story_data = []
    story_html_urls = []
    
    for story in stories:
        story_html_url = get_story_url(story, base_url)
        story_html_urls.append(story_html_url)
        
        # Format publication date
        pub_timestamp = story.get("published")
        pub_date = date_formatter(pub_timestamp)
        
        story_dict = dict(story)
        story_dict["pub_date"] = pub_date
        story_dict["heading_level"] = heading_level
        story_data.append(story_dict)
    
    return story_data, story_html_urls
