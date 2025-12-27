#!/usr/bin/env python3
"""
Shared utilities for HTML and RSS generation scripts.
"""

import hashlib
import re
from datetime import UTC, datetime
from html import escape
from typing import Any
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


def get_story_slug(story: dict[str, Any]) -> str:
    """Generate a URL slug from a story title."""
    title = story.get("title", "Untitled")
    if not title or not isinstance(title, str):
        title = "Untitled"

    # Convert to lowercase and replace spaces with hyphens
    slug = title.lower().strip()

    # Replace multiple spaces/hyphens with single hyphen
    slug = re.sub(r"[-\s]+", "-", slug)

    # Remove characters that aren't alphanumeric, hyphens, or underscores
    slug = re.sub(r"[^a-z0-9\-_]", "", slug)

    # Remove leading/trailing hyphens and underscores
    slug = slug.strip("- _")

    # Truncate to 50 characters, but ensure we don't cut in the middle of a word
    if len(slug) > 50:
        slug = slug[:50].rstrip("- _")

    # Ensure we have a valid slug
    if not slug:
        slug = "untitled"

    # URL encode the slug (quote handles encoding properly)
    return quote(slug, safe="-")


def get_story_url(story: dict[str, Any], base_url: str) -> str:
    """Generate the HTML URL for a story."""
    story_slug = get_story_slug(story)
    return f"{base_url}/stories/{story_slug}.html"


def process_footnote_references(text: str, story: dict[str, Any]) -> str:
    """
    Convert footnote references like [domain.com#1] to HTML footnote links.
    The number refers to the occurrence index of that domain in the articles list.
    Escapes the rest of the text for security.

    Args:
        text: Text that may contain footnote references
        story: Story dict containing 'articles' list with 'domain', 'title', and 'link' fields

    Returns:
        Text with footnote references converted to HTML links, rest escaped
    """
    if not text:
        return ""

    articles = story.get("articles", []) if story else []

    if not articles:
        return escape(text)

    # Create a mapping: (domain, occurrence_number) -> (article_index, article_link)
    # Group articles by domain and track occurrence order
    domain_occurrences = {}  # domain -> list of (occurrence_index, article_index, article_link)

    for idx, article in enumerate(articles):
        domain = article.get("domain", "")
        link = article.get("link", "")

        if not domain or not link:
            continue

        # Use domain as-is, no normalization
        domain_key = domain.strip()

        if domain_key:
            if domain_key not in domain_occurrences:
                domain_occurrences[domain_key] = []

            # Add this occurrence with its index (1-based) and article index
            occurrence_num = len(domain_occurrences[domain_key]) + 1
            domain_occurrences[domain_key].append((occurrence_num, idx, escape(link)))

    # Pattern to match [domain.com#number] BEFORE escaping
    def replace_footnote(match):
        full_match = match.group(0)
        content = match.group(1)  # Content inside brackets

        # Check if it's a footnote reference (contains # followed by number)
        if "#" in content:
            parts = content.rsplit("#", 1)
            if len(parts) == 2:
                domain_part = parts[0].strip()
                footnote_num_str = parts[1].strip()

                # Verify footnote number is actually numeric
                if footnote_num_str.isdigit():
                    footnote_num = int(footnote_num_str)

                    # Use domain as-is for matching, no normalization
                    domain_key = domain_part.strip()

                    # Find matching domain and occurrence
                    if domain_key in domain_occurrences:
                        occurrences = domain_occurrences[domain_key]
                        # Find the article with matching occurrence number
                        for occ_num, article_idx, article_link in occurrences:
                            if occ_num == footnote_num:
                                # Use the article index (1-based) as the replacement
                                article_index_display = article_idx + 1
                                footnote_num_escaped = escape(str(article_index_display))
                                return f'<a href="{article_link}" class="footnote-ref">[{footnote_num_escaped}]</a>'

                    # Fallback: Look for Google.com domains with domain name in title
                    # Search for articles where domain contains "google.com" and title contains the domain name
                    domain_lower = domain_key.lower()
                    google_matches = []  # Track Google.com articles matching this domain
                    for idx, article in enumerate(articles):
                        article_domain = article.get("domain", "").lower()
                        article_title = article.get("title", "").lower()
                        article_link = article.get("link", "")

                        # Check if this is a Google.com domain and title contains the domain name
                        if "google.com" in article_domain and domain_lower in article_title:
                            google_matches.append((len(google_matches) + 1, idx, article_link))

                    # If we found matching Google.com articles, use the occurrence number matching the footnote
                    if google_matches:
                        for occ_num, article_idx, article_link in google_matches:
                            if occ_num == footnote_num:
                                # Use the article index (1-based) as the replacement
                                article_index_display = article_idx + 1
                                footnote_num_escaped = escape(str(article_index_display))
                                return f'<a href="{escape(article_link)}" class="footnote-ref">[{footnote_num_escaped}]</a>'

        # Not a footnote reference, escape and return
        return escape(full_match)

    # Split text into parts: footnote references and regular text
    # Match [anything] patterns
    pattern = r"\[([^\]]+)\]"
    parts = []
    last_end = 0

    for match in re.finditer(pattern, text):
        # Add text before the match (escaped)
        if match.start() > last_end:
            parts.append(escape(text[last_end : match.start()]))

        # Process the footnote reference
        replacement = replace_footnote(match)
        parts.append(replacement)
        last_end = match.end()

    # Add remaining text (escaped)
    if last_end < len(text):
        parts.append(escape(text[last_end:]))

    return "".join(parts)


def get_jinja_env():
    """Create and return a Jinja2 environment."""
    env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape(["html", "xml"]))

    # Add custom filter for processing footnote references
    def process_footnotes_filter(text: str, story: dict[str, Any] | None = None) -> str:
        """Jinja2 filter to process footnote references."""
        if not text:
            return text
        if story is None:
            story = {}
        return process_footnote_references(text, story)

    env.filters["process_footnotes"] = process_footnotes_filter
    return env


def process_stories_for_output(
    stories: list[dict[str, Any]], config: dict[str, Any], date_formatter, heading_level: int = 1
) -> tuple[list[dict[str, Any]], list[str]]:
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

        # Extract thumbnail information from primary_image
        primary_image = story.get("primary_image")
        if primary_image and isinstance(primary_image, dict):
            thumbnail_url = primary_image.get("url")
            if thumbnail_url:
                story_dict["thumbnail_url"] = thumbnail_url
                # Extract width and height if available
                if "width" in primary_image:
                    story_dict["thumbnail_width"] = primary_image["width"]
                if "height" in primary_image:
                    story_dict["thumbnail_height"] = primary_image["height"]

        story_data.append(story_dict)

    return story_data, story_html_urls
