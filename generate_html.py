#!/usr/bin/env python3
"""
Generate HTML pages for individual stories.
"""

import json
import sys
import os
from html import escape
from urllib.parse import quote
from datetime import datetime


def get_story_content(story: dict) -> str:
    """Generate HTML content for a story from all available fields."""
    content_parts = []
    
    # Title
    title = story.get("title", "Untitled")
    if title:
        content_parts.append(f"<h1>{escape(str(title))}</h1>")
    
    # Category
    category = story.get("category", "")
    if category:
        content_parts.append(f"<p class='category'><strong>Category:</strong> {escape(str(category))}</p>")
    
    # Summary
    summary = story.get("summary", "")
    if summary:
        content_parts.append(f"<div class='summary'><p>{escape(str(summary))}</p></div>")
    
    # Quote
    quote_text = story.get("quote", "")
    quote_author = story.get("quote_author", "")
    quote_attribution = story.get("quote_attribution", "")
    if quote_text:
        quote_html = f"<blockquote><p>{escape(quote_text)}</p>"
        if quote_author:
            quote_html += f"<cite>— {escape(quote_author)}"
            if quote_attribution:
                quote_html += f" ({escape(quote_attribution)})"
            quote_html += "</cite>"
        quote_html += "</blockquote>"
        content_parts.append(quote_html)
    
    # Did you know
    did_you_know = story.get("did_you_know", "")
    if did_you_know:
        content_parts.append(f"<div class='did-you-know'><p><strong>Did you know:</strong> {escape(str(did_you_know))}</p></div>")
    
    # Talking points
    talking_points = story.get("talking_points", [])
    if talking_points:
        content_parts.append("<h2>Key Points</h2><ul>")
        for point in talking_points:
            content_parts.append(f"<li>{escape(str(point))}</li>")
        content_parts.append("</ul>")
    
    # Perspectives
    perspectives = story.get("perspectives", [])
    if perspectives:
        content_parts.append("<h2>Perspectives</h2>")
        for perspective in perspectives:
            text = perspective.get("text", "")
            sources = perspective.get("sources", [])
            if text:
                content_parts.append(f"<div class='perspective'><p>{escape(str(text))}</p>")
                if sources:
                    content_parts.append("<p><strong>Sources:</strong> ")
                    source_links = []
                    for source in sources:
                        name = source.get("name", "")
                        url = source.get("url", "")
                        if url:
                            source_links.append(f'<a href="{escape(url)}">{escape(name or url)}</a>')
                        elif name:
                            source_links.append(escape(name))
                    content_parts.append(", ".join(source_links))
                    content_parts.append("</p>")
                content_parts.append("</div>")
    
    # Timeline
    timeline = story.get("timeline", [])
    if timeline:
        content_parts.append("<h2>Timeline</h2><ul>")
        for event in timeline:
            date = event.get("date", "")
            content = event.get("content", "")
            if date and content:
                content_parts.append(f"<li><strong>{escape(str(date))}:</strong> {escape(str(content))}</li>")
            elif content:
                content_parts.append(f"<li>{escape(str(content))}</li>")
        content_parts.append("</ul>")
    
    # Technical details
    technical_details = story.get("technical_details", [])
    if technical_details:
        content_parts.append("<h2>Technical Details</h2><ul>")
        for detail in technical_details:
            content_parts.append(f"<li>{escape(str(detail))}</li>")
        content_parts.append("</ul>")
    
    # Industry impact
    industry_impact = story.get("industry_impact", [])
    if industry_impact:
        content_parts.append("<h2>Industry Impact</h2><ul>")
        for impact in industry_impact:
            content_parts.append(f"<li>{escape(str(impact))}</li>")
        content_parts.append("</ul>")
    
    # Scientific significance
    scientific_significance = story.get("scientific_significance", [])
    if scientific_significance:
        content_parts.append("<h2>Scientific Significance</h2><ul>")
        for sig in scientific_significance:
            content_parts.append(f"<li>{escape(str(sig))}</li>")
        content_parts.append("</ul>")
    
    # Historical background
    historical_background = story.get("historical_background", "")
    if historical_background:
        content_parts.append(f"<h2>Historical Background</h2><p>{escape(str(historical_background))}</p>")
    
    # Future outlook
    future_outlook = story.get("future_outlook", "")
    if future_outlook:
        content_parts.append(f"<h2>Future Outlook</h2><p>{escape(str(future_outlook))}</p>")
    
    # Q&A
    suggested_qna = story.get("suggested_qna", [])
    if suggested_qna:
        content_parts.append("<h2>Q&A</h2>")
        for qna in suggested_qna:
            question = qna.get("question", "")
            answer = qna.get("answer", "")
            if question:
                content_parts.append(f"<div class='qna'><p><strong>Q:</strong> {escape(str(question))}</p>")
                if answer:
                    content_parts.append(f"<p><strong>A:</strong> {escape(str(answer))}</p>")
                content_parts.append("</div>")
    
    # User action items
    user_action_items = story.get("user_action_items", [])
    if user_action_items:
        content_parts.append("<h2>Action Items</h2><ul>")
        for item in user_action_items:
            content_parts.append(f"<li>{escape(str(item))}</li>")
        content_parts.append("</ul>")
    
    # Primary image
    primary_image = story.get("primary_image")
    if primary_image:
        img_url = primary_image.get("url", "")
        caption = primary_image.get("caption", "")
        credit = primary_image.get("credit", "")
        img_link = primary_image.get("link", "")
        if img_url:
            img_tag = f'<img src="{escape(img_url)}" alt="{escape(caption or title)}" style="max-width: 100%; height: auto;" />'
            if img_link:
                img_tag = f'<a href="{escape(img_link)}">{img_tag}</a>'
            content_parts.append(f"<div class='image'>{img_tag}")
            if caption:
                content_parts.append(f"<p class='caption'>{escape(str(caption))}")
                if credit:
                    content_parts.append(f" <span class='credit'>({escape(str(credit))})</span>")
                content_parts.append("</p>")
            content_parts.append("</div>")
    
    # Source URLs
    source_urls = story.get("source_urls", [])
    primary_url = story.get("url", "")
    if primary_url and not primary_url.startswith("hash:"):
        content_parts.append(f'<p class="sources"><strong>Primary Source:</strong> <a href="{escape(primary_url)}">{escape(primary_url)}</a></p>')
    
    if source_urls and len(source_urls) > 1:
        content_parts.append("<p><strong>Additional Sources:</strong></p><ul>")
        for url in source_urls:
            if url != primary_url:
                content_parts.append(f'<li><a href="{escape(url)}">{escape(url)}</a></li>')
        content_parts.append("</ul>")
    
    # Domains
    domains = story.get("domains", [])
    if domains:
        domain_names = [d.get("name", "") for d in domains if d.get("name")]
        if domain_names:
            content_parts.append(f"<p><strong>Sources:</strong> {escape(', '.join(domain_names))}</p>")
    
    # Metadata
    cluster_number = story.get("cluster_number")
    unique_domains = story.get("unique_domains")
    number_of_titles = story.get("number_of_titles")
    if cluster_number is not None or unique_domains is not None or number_of_titles is not None:
        metadata = []
        if cluster_number is not None:
            metadata.append(f"Cluster #{cluster_number}")
        if unique_domains is not None:
            metadata.append(f"{unique_domains} unique domains")
        if number_of_titles is not None:
            metadata.append(f"{number_of_titles} articles")
        if metadata:
            content_parts.append(f"<p class='metadata'><strong>Metadata:</strong> {escape(', '.join(metadata))}</p>")
    
    return "\n".join(content_parts)


def generate_story_html(story: dict, config: dict) -> str:
    """Generate a complete HTML page for a story."""
    site_config = config.get("site", {})
    site_title = site_config.get("title", "Kagi Kite Combined Feed")
    base_url = site_config.get("base_url", "https://example.com")
    
    title = story.get("title", "Untitled")
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
            max-width: 900px;
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
        h2 {{
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        .category {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
        .summary {{
            background-color: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #3498db;
            margin: 20px 0;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin: 20px 0;
            font-style: italic;
            color: #555;
        }}
        blockquote cite {{
            display: block;
            margin-top: 10px;
            font-size: 0.9em;
            color: #7f8c8d;
        }}
        .did-you-know {{
            background-color: #fff3cd;
            padding: 15px;
            border-left: 4px solid #ffc107;
            margin: 20px 0;
        }}
        ul {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        li {{
            margin: 8px 0;
        }}
        .perspective {{
            background-color: #f8f9fa;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }}
        .qna {{
            background-color: #e7f3ff;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }}
        .image {{
            margin: 20px 0;
            text-align: center;
        }}
        .image img {{
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .caption {{
            margin-top: 10px;
            font-size: 0.9em;
            color: #666;
            text-align: center;
        }}
        .credit {{
            font-style: italic;
        }}
        .sources {{
            margin-top: 30px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 4px;
        }}
        .metadata {{
            margin-top: 20px;
            padding: 10px;
            background-color: #f8f9fa;
            font-size: 0.9em;
            color: #666;
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
        title = story.get("title", "Untitled")
        story_slug = quote(title.lower().replace(" ", "-")[:50], safe="")
        story_url = f"{base_url}/stories/{story_slug}.html"
        source_url = story.get("url", "")
        category = story.get("category", "")
        
        summary = story.get("summary", "")
        pub_timestamp = story.get("published")
        pub_date = ""
        if pub_timestamp:
            try:
                if isinstance(pub_timestamp, (int, float)):
                    dt = datetime.fromtimestamp(pub_timestamp)
                    pub_date = dt.strftime("%Y-%m-%d")
            except:
                pass
        
        story_item = f"""        <article class="story-item">
            <h2><a href="{escape(story_url)}">{escape(title)}</a></h2>
            {f'<p class="category">Category: {escape(category)}</p>' if category else ''}
            {f'<p class="summary">{escape(summary[:200])}...</p>' if summary else ''}
            {f'<p class="meta">Published: {escape(str(pub_date))}</p>' if pub_date else ''}
            {f'<p class="source-link"><a href="{escape(source_url)}">Read original</a></p>' if source_url and not source_url.startswith("hash:") else ''}
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
        .story-item .category {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin: 5px 0;
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
