# Thumbnail Implementation - Code Examples

## RSS Feed Example

### RSS Root Element with Media Namespace
```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" 
     xmlns:content="http://purl.org/rss/1.0/modules/content/" 
     xmlns:atom="http://www.w3.org/2005/Atom" 
     xmlns:media="http://search.yahoo.com/mrss/">
```

### RSS Item with media:thumbnail
```xml
<item>
    <title>Google rolls out option to change Gmail address</title>
    <link>https://example.com/stories/google-rolls-out-option-to-change-gmail-address.html</link>
    <guid isPermaLink="true">https://example.com/stories/google-rolls-out-option-to-change-gmail-address.html</guid>
    <pubDate>Sat, 27 Dec 2025 10:26:56 +0000</pubDate>
    <author>Kite Feed Generator (Technology / Email)</author>
    <media:thumbnail url="https://example.com/img/thumbnail.jpg" />
    <description><![CDATA[...]]></description>
    <content:encoded><![CDATA[...]]></content:encoded>
</item>
```

## HTML Examples

### Story Page - Primary Image with Semantic HTML
```html
<figure class='image'>
    <a href="https://example.com/article">
        <img src="https://example.com/image.jpg" 
             alt="Article image" 
             title="Image caption" 
             style="max-width: 100%; height: auto;" />
    </a>
    <figcaption class='caption'>
        Image caption <span class='credit'>(Photo credit)</span>
    </figcaption>
</figure>
```

### Index Page - Story Thumbnail
```html
<li class="story-item">
    <figure class="story-thumbnail">
        <img src="https://example.com/thumbnail.jpg" 
             alt="Story title" 
             loading="lazy">
    </figure>
    <div class="story-content">
        <h2 class="story-title">
            <a href="stories/story-slug.html">Story Title</a>
        </h2>
        <div class="story-meta">
            <span class="category">Technology</span>
            <span>2025-12-27</span>
        </div>
        <div class="story-summary">Story summary text...</div>
    </div>
</li>
```

### CSS for Semantic Elements
```css
figure.image {
    margin: 20px 0;
    text-align: center;
}

figure.image img {
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    max-width: 100%;
    height: auto;
}

figcaption.caption {
    margin-top: 10px;
    font-size: 0.9em;
    color: #666;
    text-align: center;
}

.story-thumbnail {
    flex-shrink: 0;
    width: 200px;
    height: 150px;
    overflow: hidden;
    border-radius: 4px;
}

.story-thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}
```

## Python Code - Thumbnail Extraction

### In generate_utils.py
```python
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
```

### Template Usage in rss.xml
```jinja2
{% if story.thumbnail_url %}
<media:thumbnail url="{{ story.thumbnail_url|e }}"
                {% if story.thumbnail_width %} width="{{ story.thumbnail_width }}"{% endif %}
                {% if story.thumbnail_height %} height="{{ story.thumbnail_height }}"{% endif %} />
{% endif %}
```

### Template Usage in index.html
```jinja2
{% if story.thumbnail_url %}
<figure class="story-thumbnail">
    <img src="{{ story.thumbnail_url|e }}" 
         alt="{{ story.title|e }}" 
         loading="lazy">
</figure>
{% endif %}
```

## Testing Commands

### Validate RSS Feed
```bash
python3 -c "import xml.etree.ElementTree as ET; tree = ET.parse('feed.xml'); print('✓ Valid RSS feed')"
```

### Count Thumbnails
```bash
grep -c "media:thumbnail" feed.xml
```

### Check HTML Semantic Elements
```bash
grep -c "figure class='image'" stories/*.html
```

### Verify Namespace
```bash
head -2 feed.xml | grep "xmlns:media"
```
