#!/usr/bin/env python3
"""
Process Kagi Kite JSON files, combine them, filter, and merge duplicates.
"""

import hashlib
import json
import sys
from typing import Any

import requests


def load_config(config_path: str = "config.json") -> dict[str, Any]:
    """Load configuration from JSON file."""
    with open(config_path) as f:
        return json.load(f)


def fetch_json(url: str) -> dict[str, Any]:
    """Fetch JSON data from a URL."""
    try:
        response = requests.get(url, timeout=30, allow_redirects=True)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return {}


def get_category_file_url(category_name: str, base_url: str = "https://kite.kagi.com") -> str:
    """Get the URL for a category file based on category name."""
    # Fetch kite.json to find the category file name
    kite_data = fetch_json(f"{base_url}/kite.json")
    categories = kite_data.get("categories", [])

    for cat in categories:
        if cat.get("name") == category_name:
            return f"{base_url}/{cat.get('file')}"

    # Fallback: try common patterns
    category_lower = category_name.lower().replace(" ", "_")
    return f"{base_url}/{category_lower}.json"


def extract_clusters_from_category(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract clusters from a category JSON file."""
    clusters = data.get("clusters", [])
    category_name = data.get("category", "")

    # Add category name to each cluster
    for cluster in clusters:
        cluster["_category"] = category_name

    return clusters


def get_source_urls_from_cluster(cluster: dict[str, Any]) -> list[str]:
    """Extract all source URLs from a cluster."""
    urls = set()

    # Get URLs from articles list (primary source for deduplication)
    articles = cluster.get("articles", [])
    for article in articles:
        article_link = article.get("link")
        if article_link:
            urls.add(article_link)

    # Get quote source URL
    quote_url = cluster.get("quote_source_url")
    if quote_url:
        urls.add(quote_url)

    # Get URLs from perspectives
    perspectives = cluster.get("perspectives", [])
    for perspective in perspectives:
        sources = perspective.get("sources", [])
        for source in sources:
            source_url = source.get("url")
            if source_url:
                urls.add(source_url)

    # Get primary image link
    primary_image = cluster.get("primary_image")
    if primary_image and primary_image.get("link"):
        urls.add(primary_image.get("link"))

    return list(urls)


def get_primary_source_url(cluster: dict[str, Any]) -> str:
    """Get the primary source URL for deduplication."""
    # Prefer first article link (most reliable source)
    articles = cluster.get("articles", [])
    if articles and articles[0].get("link"):
        return articles[0].get("link")

    # Fallback to quote_source_url
    if cluster.get("quote_source_url"):
        return cluster.get("quote_source_url")

    # Fallback to first perspective source
    perspectives = cluster.get("perspectives", [])
    if perspectives:
        sources = perspectives[0].get("sources", [])
        if sources and sources[0].get("url"):
            return sources[0].get("url")

    # Fallback to image link
    primary_image = cluster.get("primary_image")
    if primary_image and primary_image.get("link"):
        return primary_image.get("link")

    # Generate hash-based ID if no URL found
    cluster_str = json.dumps(cluster, sort_keys=True)
    return f"hash:{hashlib.md5(cluster_str.encode()).hexdigest()}"


def cluster_to_story(cluster: dict[str, Any], file_timestamp: Any = None, feed_category: str = "") -> dict[str, Any]:
    """Convert a cluster to a story format."""
    story = {
        "title": cluster.get("title", "Untitled"),
        "summary": cluster.get("short_summary", ""),
        "feed_category": feed_category or cluster.get("_category", ""),
        "item_category": cluster.get("category", ""),
        "category": cluster.get("_category", cluster.get("category", "")),  # Keep for backward compatibility
        "cluster_number": cluster.get("cluster_number"),
        "unique_domains": cluster.get("unique_domains"),
        "number_of_titles": cluster.get("number_of_titles"),
        "quote": cluster.get("quote", ""),
        "quote_author": cluster.get("quote_author", ""),
        "quote_attribution": cluster.get("quote_attribution", ""),
        "talking_points": cluster.get("talking_points", []),
        "perspectives": cluster.get("perspectives", []),
        "timeline": cluster.get("timeline", []),
        "did_you_know": cluster.get("did_you_know", ""),
        "primary_image": cluster.get("primary_image"),
        "domains": cluster.get("domains", []),
        "articles": cluster.get("articles", []),  # Include articles list
        "technical_details": cluster.get("technical_details", []),
        "scientific_significance": cluster.get("scientific_significance", []),
        "industry_impact": cluster.get("industry_impact", []),
        "suggested_qna": cluster.get("suggested_qna", []),
        "user_action_items": cluster.get("user_action_items", []),
        "historical_background": cluster.get("historical_background", ""),
        "future_outlook": cluster.get("future_outlook", ""),
        "geopolitical_context": cluster.get("geopolitical_context", ""),
        "humanitarian_impact": cluster.get("humanitarian_impact", ""),
        "economic_implications": cluster.get("economic_implications", ""),
        "international_reactions": cluster.get("international_reactions", []),
        "key_players": cluster.get("key_players", []),
        "emoji": cluster.get("emoji", ""),
        "location": cluster.get("location", ""),
    }

    # Set primary source URL (prefer first article)
    story["url"] = get_primary_source_url(cluster)
    story["source_urls"] = get_source_urls_from_cluster(cluster)

    # Set published date (prefer file timestamp, then cluster timestamp, then first article date)
    if file_timestamp is not None:
        story["published"] = file_timestamp
    elif "timestamp" in cluster:
        story["published"] = cluster["timestamp"]
    elif cluster.get("articles") and cluster["articles"][0].get("date"):
        story["published"] = cluster["articles"][0].get("date")

    return story


def apply_filters(stories: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    """Apply filters to stories based on configuration."""
    if not config.get("filters", {}).get("enabled", True):
        return stories

    filtered = []
    min_score = config.get("filters", {}).get("min_score", 0)

    for story in stories:
        # For clusters, we can use cluster_number as a proxy for ranking
        # Lower cluster_number typically means higher importance
        score = story.get("cluster_number", 999)
        # Invert so lower cluster_number = higher score
        score = 100 - score if score < 100 else 0

        if score >= min_score:
            filtered.append(story)
        elif min_score == 0:
            # If no score requirement, include all
            filtered.append(story)

    return filtered


def merge_duplicates(stories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge duplicate stories based on source article URLs from articles list."""
    seen_urls: dict[str, dict[str, Any]] = {}
    merged = []

    for story in stories:
        # Extract article URLs directly from articles list
        articles = story.get("articles", [])
        article_urls = []
        for article in articles:
            article_link = article.get("link")
            if article_link:
                article_urls.append(article_link)

        # If no articles, fall back to primary URL
        if not article_urls:
            primary_url = story.get("url", "")
            if primary_url and not primary_url.startswith("hash:"):
                article_urls.append(primary_url)

        # Find if any of these article URLs have been seen
        found_duplicate = False
        matching_url = None

        for url in article_urls:
            normalized_url = url.lower().strip()
            if normalized_url in seen_urls:
                found_duplicate = True
                matching_url = normalized_url
                break

        if found_duplicate:
            # Merge with existing story
            existing = seen_urls[matching_url]
            # Merge articles lists
            existing_articles = existing.get("articles", [])
            new_articles = story.get("articles", [])
            # Merge articles, avoiding duplicates based on link
            existing_article_links = {a.get("link") for a in existing_articles if a.get("link")}
            for article in new_articles:
                if article.get("link") not in existing_article_links:
                    existing_articles.append(article)
            existing["articles"] = existing_articles

            # Merge source URLs
            existing_urls = set(existing.get("source_urls", []))
            new_urls = set(story.get("source_urls", []))
            existing["source_urls"] = list(existing_urls | new_urls)

            # Merge feed_category: combine unique feed categories
            existing_feed_cats = existing.get("feed_category", "")
            new_feed_cats = story.get("feed_category", "")
            if new_feed_cats and new_feed_cats != existing_feed_cats:
                # Combine feed categories, avoiding duplicates
                existing_list = [existing_feed_cats] if existing_feed_cats else []
                new_list = [new_feed_cats] if new_feed_cats else []
                combined_feed_cats = list(set(existing_list + new_list))
                if len(combined_feed_cats) == 1:
                    existing["feed_category"] = combined_feed_cats[0]
                elif combined_feed_cats:
                    existing["feed_category"] = ", ".join(sorted(combined_feed_cats))
            
            # Merge item_category: prefer non-empty
            existing_item_cat = existing.get("item_category", "")
            new_item_cat = story.get("item_category", "")
            if new_item_cat and not existing_item_cat:
                existing["item_category"] = new_item_cat
            
            # Merge other fields, preferring non-empty values
            for key in story:
                if key not in ["url", "source_urls", "articles", "feed_category", "item_category"]:
                    if story[key] and not existing.get(key):
                        existing[key] = story[key]
                    elif isinstance(story[key], list) and story[key]:
                        existing_list = existing.get(key, [])
                        combined = existing_list + story[key]
                        # Only use set() if items are hashable (strings, numbers, etc.)
                        # For lists containing dicts, just concatenate and keep all items
                        try:
                            existing[key] = list(set(combined))
                        except TypeError:
                            # Items are not hashable (e.g., dicts), just keep the combined list
                            existing[key] = combined
        else:
            # New story - add all article URLs to seen set
            merged.append(story)
            for url in article_urls:
                normalized_url = url.lower().strip()
                if normalized_url and not normalized_url.startswith("hash:"):
                    seen_urls[normalized_url] = story

    return merged


def process_kite_feeds(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Main processing function."""
    all_stories = []

    # Get category names from config
    categories = config.get("feeds", {}).get("categories", [])
    top_n_per_feed = config.get("feeds", {}).get("top_n", 5)
    top_n_by_category = config.get("feeds", {}).get("top_n_by_category", {})
    base_url = config.get("feeds", {}).get("base_url", "https://kite.kagi.com")

    # Fetch kite.json to get category mappings
    print(f"Fetching category index from {base_url}/kite.json...", file=sys.stderr)
    kite_data = fetch_json(f"{base_url}/kite.json")

    if not kite_data:
        print("Error: Could not fetch kite.json", file=sys.stderr)
        return []

    # Process each category
    for category_name in categories:
        print(f"Processing category: {category_name}...", file=sys.stderr)

        # Find the category file name
        category_file = None
        for cat in kite_data.get("categories", []):
            if cat.get("name") == category_name:
                category_file = cat.get("file")
                break

        if not category_file:
            print(f"Warning: Category '{category_name}' not found in kite.json", file=sys.stderr)
            continue

        # Fetch the category file
        category_url = f"{base_url}/{category_file}"
        print(f"Fetching {category_url}...", file=sys.stderr)
        category_data = fetch_json(category_url)

        if not category_data:
            print(f"Warning: Could not fetch {category_url}", file=sys.stderr)
            continue

        # Extract clusters
        clusters = extract_clusters_from_category(category_data)
        print(f"Found {len(clusters)} clusters in {category_name}", file=sys.stderr)

        # Get file-level timestamp (top-level key in JSON)
        file_timestamp = category_data.get("timestamp")

        # Convert clusters to stories
        category_stories = [cluster_to_story(cluster, file_timestamp, category_name) for cluster in clusters]

        # Determine top_n for this category (category-specific or default)
        category_top_n = top_n_by_category.get(category_name, top_n_per_feed)

        # Apply top_n per feed (sort by cluster_number, lower is better)
        if category_top_n and category_top_n > 0:
            category_stories.sort(key=lambda x: x.get("cluster_number", 999))
            category_stories = category_stories[:category_top_n]
            print(f"Selected top {len(category_stories)} stories from {category_name}", file=sys.stderr)

        all_stories.extend(category_stories)

    # Apply filters
    filtered_stories = apply_filters(all_stories, config)
    print(f"After filtering: {len(filtered_stories)} stories", file=sys.stderr)

    # Merge duplicates across categories
    merged_stories = merge_duplicates(filtered_stories)
    print(f"After merging duplicates: {len(merged_stories)} stories", file=sys.stderr)

    return merged_stories


if __name__ == "__main__":
    config = load_config()
    stories = process_kite_feeds(config)

    # Output as JSON
    print(json.dumps(stories, indent=2, ensure_ascii=False))
