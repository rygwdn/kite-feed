#!/usr/bin/env python3
"""
Generate RSS feed from processed Kagi Kite stories.
"""

import json
import sys
from datetime import datetime, timezone
from html import escape
from urllib.parse import quote


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


def get_story_content(story: dict) -> str:
    """Generate HTML content for a story from all available fields."""
    content_parts = []
    
    # Title
    title = story.get("title", "Untitled")
    if title:
        content_parts.append(f"<h2>{escape(str(title))}</h2>")
    
    # Category
    category = story.get("category", "")
    if category:
        content_parts.append(f"<p><strong>Category:</strong> {escape(str(category))}</p>")
    
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
        content_parts.append("<h3>Key Points</h3><ul>")
        for point in talking_points:
            content_parts.append(f"<li>{escape(str(point))}</li>")
        content_parts.append("</ul>")
    
    # Perspectives
    perspectives = story.get("perspectives", [])
    if perspectives:
        content_parts.append("<h3>Perspectives</h3>")
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
        content_parts.append("<h3>Timeline</h3><ul>")
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
        content_parts.append("<h3>Technical Details</h3><ul>")
        for detail in technical_details:
            content_parts.append(f"<li>{escape(str(detail))}</li>")
        content_parts.append("</ul>")
    
    # Industry impact
    industry_impact = story.get("industry_impact", [])
    if industry_impact:
        content_parts.append("<h3>Industry Impact</h3><ul>")
        for impact in industry_impact:
            content_parts.append(f"<li>{escape(str(impact))}</li>")
        content_parts.append("</ul>")
    
    # Scientific significance
    scientific_significance = story.get("scientific_significance", [])
    if scientific_significance:
        content_parts.append("<h3>Scientific Significance</h3><ul>")
        for sig in scientific_significance:
            content_parts.append(f"<li>{escape(str(sig))}</li>")
        content_parts.append("</ul>")
    
    # Historical background
    historical_background = story.get("historical_background", "")
    if historical_background:
        content_parts.append(f"<h3>Historical Background</h3><p>{escape(str(historical_background))}</p>")
    
    # Future outlook
    future_outlook = story.get("future_outlook", "")
    if future_outlook:
        content_parts.append(f"<h3>Future Outlook</h3><p>{escape(str(future_outlook))}</p>")
    
    # Q&A
    suggested_qna = story.get("suggested_qna", [])
    if suggested_qna:
        content_parts.append("<h3>Q&A</h3>")
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
        content_parts.append("<h3>Action Items</h3><ul>")
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
            img_tag = f'<img src="{escape(img_url)}" alt="{escape(caption or title)}" />'
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


def generate_rss(stories: list, config: dict) -> str:
    """Generate RSS XML from stories."""
    site_config = config.get("site", {})
    title = site_config.get("title", "Kagi Kite Combined Feed")
    description = site_config.get("description", "Combined feed from Kagi Kite service")
    base_url = site_config.get("base_url", "https://example.com")
    author = site_config.get("author", "Kite Feed Generator")
    
    rss_items = []
    
    for story in stories:
        story_title = story.get("title", "Untitled")
        story_url = story.get("url", "")
        
        # Generate a slug for the HTML page
        story_slug = quote(story_title.lower().replace(" ", "-")[:50], safe="")
        story_html_url = f"{base_url}/stories/{story_slug}.html"
        
        # Use HTML page URL if source URL not available or is hash-based
        if not story_url or story_url.startswith("hash:"):
            story_url = story_html_url
        
        # Get content
        content = get_story_content(story)
        
        # Get date
        pub_timestamp = story.get("published")
        pub_date = format_date(pub_timestamp) if pub_timestamp else datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
        
        # Get description (summary)
        description_text = story.get("summary", "")
        if not description_text:
            description_text = story_title
        
        guid = story_url if story_url and not story_url.startswith("hash:") else story_html_url
        
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
        <lastBuildDate>{datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>
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
