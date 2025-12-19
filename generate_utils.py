#!/usr/bin/env python3
"""
Shared utilities for HTML and RSS generation scripts.
"""

import hashlib
import re
from datetime import UTC, datetime
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
        return datetime.now(UTC).strftime("%a, %d %b %Y %H:%M:%S +0000")
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
        return datetime.now(UTC).strftime("%a, %d %b %Y %H:%M:%S +0000")
    except Exception:
        return datetime.now(UTC).strftime("%a, %d %b %Y %H:%M:%S +0000")


def get_story_slug(story: dict) -> str:
    """Generate a URL slug from a story title."""
    title = story.get("title", "Untitled")
    if not title or not isinstance(title, str):
        title = "Untitled"
    
    # Convert to lowercase and replace spaces with hyphens
    slug = title.lower().strip()
    
    # Replace multiple spaces/hyphens with single hyphen
    slug = re.sub(r'[-\s]+', '-', slug)
    
    # Remove characters that aren't alphanumeric, hyphens, or underscores
    slug = re.sub(r'[^a-z0-9\-_]', '', slug)
    
    # Remove leading/trailing hyphens and underscores
    slug = slug.strip('- _')
    
    # Truncate to 50 characters, but ensure we don't cut in the middle of a word
    if len(slug) > 50:
        slug = slug[:50].rstrip('- _')
    
    # Ensure we have a valid slug
    if not slug:
        slug = "untitled"
    
    # URL encode the slug (quote handles encoding properly)
    return quote(slug, safe="-")


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
    seen_slugs = {}  # Track slugs to ensure uniqueness

    for story in stories:
        # Generate base slug
        base_slug = get_story_slug(story)
        
        # Ensure uniqueness by adding a hash suffix if needed
        story_slug = base_slug
        if story_slug in seen_slugs:
            # Create a unique identifier from story content
            story_id = story.get("url") or story.get("title", "") or str(id(story))
            hash_suffix = hashlib.md5(story_id.encode()).hexdigest()[:8]
            story_slug = f"{base_slug}-{hash_suffix}"
            # Ensure we don't exceed reasonable length
            if len(story_slug) > 70:
                story_slug = f"{base_slug[:42]}-{hash_suffix}"
        
        seen_slugs[story_slug] = True
        
        # Generate URL with unique slug
        story_html_url = f"{base_url}/stories/{story_slug}.html"
        story_html_urls.append(story_html_url)

        # Format publication date
        pub_timestamp = story.get("published")
        pub_date = date_formatter(pub_timestamp)

        story_dict = dict(story)
        story_dict["pub_date"] = pub_date
        story_dict["heading_level"] = heading_level
        story_data.append(story_dict)

    return story_data, story_html_urls
