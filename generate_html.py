#!/usr/bin/env python3
"""
Generate HTML pages for individual stories.
"""

import json
import sys
import os
from html import escape
from urllib.parse import quote


def get_story_content(story: dict) -> str:
    """Generate HTML content for a story from all available fields."""
    content_parts = []
    
    # Title
    title = story.get("title", story.get("headline", "Untitled"))
    if title:
        content_parts.append(f"<h1>{escape(str(title))}</h1>")
    
    # Summary/Description
    summary = story.get("summary", story.get("description", story.get("excerpt", "")))
    if summary:
        content_parts.append(f"<p class='summary'><strong>Summary:</strong> {escape(str(summary))}</p>")
    
    # Content/Body
    content = story.get("content", story.get("body", story.get("text", "")))
    if content:
        content_parts.append(f"<div class='content'>{escape(str(content))}</div>")
    
    # Source URL
    source_url = story.get("url", story.get("source_url", story.get("article_url", story.get("link", "")))
    if source_url:
        content_parts.append(f'<p class="source"><strong>Source:</strong> <a href="{escape(source_url)}">{escape(source_url)}</a></p>')
    
    # Author
    author = story.get("author", story.get("byline", ""))
    if author:
        content_parts.append(f"<p class='author'><strong>Author:</strong> {escape(str(author))}</p>")
    
    # Published date
    pub_date = story.get("published", story.get("date", story.get("published_date", "")))
    if pub_date:
        content_parts.append(f"<p class='date'><strong>Published:</strong> {escape(str(pub_date))}</p>")
    
    # Categories/Tags
    categories = story.get("categories", story.get("tags", story.get("topics", [])))
    if categories:
        if isinstance(categories, list):
            cats_str = ", ".join(str(c) for c in categories)
        else:
            cats_str = str(categories)
        content_parts.append(f"<p class='categories'><strong>Categories:</strong> {escape(cats_str)}</p>")
    
    # Additional metadata
    score = story.get("score", story.get("relevance", story.get("importance")))
    if score is not None:
        content_parts.append(f"<p class='score'><strong>Score:</strong> {score}</p>")
    
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


def generate_story_html(story: dict, config: dict) -> str:
    """Generate a complete HTML page for a story."""
    site_config = config.get("site", {})
    site_title = site_config.get("title", "Kagi Kite Combined Feed")
    base_url = site_config.get("base_url", "https://example.com")
    
    title = story.get("title", story.get("headline", "Untitled"))
    content = get_story_content(story)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)} - {escape(site_title)}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
            background-color: #fff;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .summary {{
            background-color: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #3498db;
            margin: 20px 0;
        }}
        .content {{
            margin: 20px 0;
            padding: 15px;
        }}
        .source, .author, .date, .categories, .score {{
            margin: 10px 0;
            padding: 8px;
            background-color: #f8f9fa;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            padding: 8px 16px;
            background-color: #3498db;
            color: white;
            border-radius: 4px;
        }}
        .back-link:hover {{
            background-color: #2980b9;
            text-decoration: none;
        }}
        footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <a href="{base_url}/index.html" class="back-link">← Back to Feed</a>
    {content}
    <footer>
        <p>Generated from <a href="https://kite.kagi.com">Kagi Kite</a> data</p>
    </footer>
</body>
</html>"""
    
    return html


def generate_index_html(stories: list, config: dict) -> str:
    """Generate an index HTML page listing all stories."""
    site_config = config.get("site", {})
    site_title = site_config.get("title", "Kagi Kite Combined Feed")
    description = site_config.get("description", "Combined feed from Kagi Kite service")
    base_url = site_config.get("base_url", "https://example.com")
    
    story_list = []
    for story in stories:
        title = story.get("title", story.get("headline", "Untitled"))
        story_slug = quote(title.lower().replace(" ", "-")[:50], safe="")
        story_url = f"{base_url}/stories/{story_slug}.html"
        source_url = story.get("url", story.get("source_url", story.get("article_url", story.get("link", "")))
        
        summary = story.get("summary", story.get("description", story.get("excerpt", "")))
        pub_date = story.get("published", story.get("date", story.get("published_date", ""))
        
        story_item = f"""        <article class="story-item">
            <h2><a href="{escape(story_url)}">{escape(title)}</a></h2>
            {f'<p class="summary">{escape(summary[:200])}...</p>' if summary else ''}
            {f'<p class="meta">Published: {escape(str(pub_date))}</p>' if pub_date else ''}
            {f'<p class="source-link"><a href="{escape(source_url)}">Read original</a></p>' if source_url else ''}
        </article>"""
        
        story_list.append(story_item)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(site_title)}</title>
    <link rel="alternate" type="application/rss+xml" title="{escape(site_title)}" href="{base_url}/feed.xml">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
            background-color: #fff;
        }}
        header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #3498db;
        }}
        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .description {{
            color: #666;
            font-size: 1.1em;
        }}
        .rss-link {{
            display: inline-block;
            margin-top: 10px;
            padding: 8px 16px;
            background-color: #ff6600;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }}
        .rss-link:hover {{
            background-color: #e55a00;
        }}
        .story-item {{
            margin-bottom: 30px;
            padding: 20px;
            background-color: #f8f9fa;
            border-left: 4px solid #3498db;
        }}
        .story-item h2 {{
            margin-top: 0;
            color: #2c3e50;
        }}
        .story-item h2 a {{
            color: #2c3e50;
            text-decoration: none;
        }}
        .story-item h2 a:hover {{
            color: #3498db;
        }}
        .summary {{
            color: #555;
            margin: 10px 0;
        }}
        .meta {{
            color: #666;
            font-size: 0.9em;
            margin: 5px 0;
        }}
        .source-link {{
            margin-top: 10px;
        }}
        .source-link a {{
            color: #3498db;
            text-decoration: none;
        }}
        .source-link a:hover {{
            text-decoration: underline;
        }}
        footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <header>
        <h1>{escape(site_title)}</h1>
        <p class="description">{escape(description)}</p>
        <a href="{base_url}/feed.xml" class="rss-link">Subscribe via RSS</a>
    </header>
    <main>
{chr(10).join(story_list)}
    </main>
    <footer>
        <p>Generated from <a href="https://kite.kagi.com">Kagi Kite</a> data</p>
        <p>Updated daily at 12PM UTC</p>
    </footer>
</body>
</html>"""
    
    return html


if __name__ == "__main__":
    config = json.load(open("config.json"))
    stories = json.load(sys.stdin)
    
    # Create stories directory
    os.makedirs("stories", exist_ok=True)
    
    # Generate individual story pages
    for story in stories:
        title = story.get("title", story.get("headline", "Untitled"))
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
