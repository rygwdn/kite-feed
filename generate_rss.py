#!/usr/bin/env python3
"""
Generate RSS feed from processed Kagi Kite stories.
"""

import json
import sys
from datetime import datetime
from html import escape
from urllib.parse import quote


def format_date(date_str: str) -> str:
    """Format date string for RSS."""
    try:
        # Try parsing various date formats
        for fmt in [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S"
        ]:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
            except ValueError:
                continue
        # Fallback to current time
        return datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
    except:
        return datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")


def get_story_content(story: dict) -> str:
    """Generate HTML content for a story from all available fields."""
    content_parts = []
    
    # Title
    title = story.get("title", story.get("headline", "Untitled"))
    if title:
        content_parts.append(f"<h2>{escape(str(title))}</h2>")
    
    # Summary/Description
    summary = story.get("summary", story.get("description", story.get("excerpt", "")))
    if summary:
        content_parts.append(f"<p><strong>Summary:</strong> {escape(str(summary))}</p>")
    
    # Content/Body
    content = story.get("content", story.get("body", story.get("text", "")))
    if content:
        content_parts.append(f"<div>{escape(str(content))}</div>")
    
    # Source URL
    source_url = story.get("url", story.get("source_url", story.get("article_url", story.get("link", ""))))
    if source_url:
        content_parts.append(f'<p><strong>Source:</strong> <a href="{escape(source_url)}">{escape(source_url)}</a></p>')
    
    # Author
    author = story.get("author", story.get("byline", ""))
    if author:
        content_parts.append(f"<p><strong>Author:</strong> {escape(str(author))}</p>")
    
    # Published date
    pub_date = story.get("published", story.get("date", story.get("published_date", "")))
    if pub_date:
        content_parts.append(f"<p><strong>Published:</strong> {escape(str(pub_date))}</p>")
    
    # Categories/Tags
    categories = story.get("categories", story.get("tags", story.get("topics", [])))
    if categories:
        if isinstance(categories, list):
            cats_str = ", ".join(str(c) for c in categories)
        else:
            cats_str = str(categories)
        content_parts.append(f"<p><strong>Categories:</strong> {escape(cats_str)}</p>")
    
    # Additional metadata
    score = story.get("score", story.get("relevance", story.get("importance")))
    if score is not None:
        content_parts.append(f"<p><strong>Score:</strong> {score}</p>")
    
    # Any other fields
    known_fields = {"title", "headline", "summary", "description", "excerpt", "content", 
                    "body", "text", "url", "source_url", "article_url", "link", "author",
                    "byline", "published", "date", "published_date", "categories", "tags",
                    "topics", "score", "relevance", "importance"}
    
    for key, value in story.items():
        if key not in known_fields and value:
            if isinstance(value, (str, int, float)):
                content_parts.append(f"<p><strong>{escape(str(key).title())}:</strong> {escape(str(value))}</p>")
            elif isinstance(value, list):
                content_parts.append(f"<p><strong>{escape(str(key).title())}:</strong> {escape(', '.join(str(v) for v in value))}</p>")
    
    return "\n".join(content_parts)


def generate_rss(stories: list, config: dict) -> str:
    """Generate RSS XML from stories."""
    site_config = config.get("site", {})
    title = site_config.get("title", "Kagi Kite Combined Feed")
    description = site_config.get("description", "Combined feed from Kagi Kite service")
    base_url = site_config.get("base_url", "https://example.com")
    author = site_config.get("author", "Kite Feed Generator")
    
    rss_items = []
    
    for story in stories:
        story_title = story.get("title", story.get("headline", "Untitled"))
        story_url = story.get("url", story.get("source_url", story.get("article_url", story.get("link", ""))))
        
        # Generate a slug for the HTML page
        story_slug = quote(story_title.lower().replace(" ", "-")[:50], safe="")
        story_html_url = f"{base_url}/stories/{story_slug}.html"
        
        # Use HTML page URL if source URL not available
        if not story_url:
            story_url = story_html_url
        
        # Get content
        content = get_story_content(story)
        
        # Get date
        pub_date_str = story.get("published", story.get("date", story.get("published_date", "")))
        pub_date = format_date(pub_date_str) if pub_date_str else datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
        
        # Get description (summary)
        description_text = story.get("summary", story.get("description", story.get("excerpt", "")))
        if not description_text:
            description_text = story_title
        
        guid = story_url if story_url else f"{base_url}/stories/{hash(story_title)}"
        
        item = f"""    <item>
        <title>{escape(story_title)}</title>
        <link>{escape(story_url)}</link>
        <guid isPermaLink="true">{escape(guid)}</guid>
        <pubDate>{pub_date}</pubDate>
        <description><![CDATA[{description_text}]]></description>
        <content:encoded><![CDATA[{content}]]></content:encoded>
    </item>"""
        
        rss_items.append(item)
    
    rss_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
    <channel>
        <title>{escape(title)}</title>
        <link>{base_url}</link>
        <description>{escape(description)}</description>
        <language>en-us</language>
        <lastBuildDate>{datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>
        <generator>Kite Feed Generator</generator>
        <managingEditor>{escape(author)}</managingEditor>
{chr(10).join(rss_items)}
    </channel>
</rss>"""
    
    return rss_xml


if __name__ == "__main__":
    config = json.load(open("config.json"))
    stories = json.load(sys.stdin)
    
    rss_xml = generate_rss(stories, config)
    print(rss_xml)
