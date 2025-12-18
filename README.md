# Kite Feed Generator

A static site generator that combines multiple Kagi Kite JSON feeds, filters and merges them, and generates both RSS feeds and HTML pages. The site is automatically updated daily via GitHub Actions and served via GitHub Pages.

## Features

- 🔄 **Automated Updates**: Cron-based GitHub Action runs daily at 12:30 PM UTC (30 minutes after Kite updates)
- 📰 **RSS Feed**: Generates a combined RSS feed (`feed.xml`) with full story content
- 🌐 **HTML Pages**: Creates individual HTML pages for each story (no JavaScript required)
- 🔗 **Deduplication**: Removes duplicate stories based on source article URLs
- ⚙️ **Configurable**: Easy configuration via `config.json`
- 📊 **Filtering**: Apply score-based filters to stories
- 🎨 **Clean Design**: Modern, responsive HTML pages with clean styling

## Setup

1. **Fork or clone this repository**

2. **Configure the project**:
   Edit `config.json` to customize:
   - Feed URLs to combine
   - Top N stories limit
   - Filter settings
   - Site metadata (title, description, base URL)

   ```json
   {
     "feeds": {
       "list": [
         "https://kite.kagi.com/kite.json"
       ],
       "top_n": 10
     },
     "filters": {
       "enabled": true,
       "min_score": 0
     },
     "site": {
       "title": "Kagi Kite Combined Feed",
       "description": "Combined feed from Kagi Kite service",
       "base_url": "https://YOUR_USERNAME.github.io/kite-feed",
       "author": "Kite Feed Generator"
     }
   }
   ```

3. **Update `base_url` in config.json**:
   Replace `YOUR_USERNAME` with your GitHub username and `kite-feed` with your repository name.

4. **Enable GitHub Pages**:
   - Go to your repository Settings → Pages
   - Select "GitHub Actions" as the source
   - The site will be deployed automatically after the first workflow run

5. **Test locally** (optional):
   ```bash
   pip install -r requirements.txt
   python3 process_kite.py > processed_stories.json
   python3 generate_rss.py < processed_stories.json > feed.xml
   python3 generate_html.py < processed_stories.json
   ```

## How It Works

1. **Fetch**: The workflow fetches JSON files from configured Kagi Kite URLs
2. **Extract**: Stories are extracted from the JSON structure (handles various formats)
3. **Filter**: Stories are filtered based on score thresholds (if enabled)
4. **Merge**: Duplicate stories are removed based on source article URLs
5. **Limit**: Top N stories are selected (if configured)
6. **Generate**: 
   - RSS feed (`feed.xml`) with full content
   - HTML index page (`index.html`) listing all stories
   - Individual HTML pages for each story in `stories/` directory
7. **Deploy**: Changes are committed and pushed, triggering GitHub Pages deployment

## Project Structure

```
.
├── .github/
│   └── workflows/
│       ├── update-feed.yml      # Daily cron job to update feed
│       └── pages.yml             # GitHub Pages deployment
├── stories/                      # Generated HTML pages (created automatically)
├── config.json                   # Configuration file
├── process_kite.py               # Main processing script
├── generate_rss.py               # RSS feed generator
├── generate_html.py              # HTML page generator
├── requirements.txt              # Python dependencies
├── feed.xml                      # Generated RSS feed (created automatically)
├── index.html                    # Generated index page (created automatically)
└── README.md                     # This file
```

## Configuration Options

### Feeds
- `feeds.list`: Array of Kagi Kite JSON URLs to fetch
- `feeds.top_n`: Maximum number of stories to include (0 = no limit)

### Filters
- `filters.enabled`: Enable/disable filtering
- `filters.min_score`: Minimum score threshold (0 = no threshold)

### Site
- `site.title`: Site title
- `site.description`: Site description
- `site.base_url`: Base URL for GitHub Pages (must match your repo)
- `site.author`: Author name for RSS feed

## Story Content

Each story page and RSS item includes all available fields from the Kite JSON:
- Title/Headline
- Summary/Description
- Content/Body
- Source URL
- Author/Byline
- Published Date
- Categories/Tags
- Score/Relevance
- Any additional metadata fields

## Manual Updates

You can manually trigger an update by:
1. Going to the "Actions" tab in your repository
2. Selecting "Update Kite Feed" workflow
3. Clicking "Run workflow"

## License

This project is open source. The Kagi Kite data is licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).

## References

- [Kagi Kite Public Repository](https://github.com/kagisearch/kite-public)
- [Kagi Kite Service](https://kite.kagi.com)
