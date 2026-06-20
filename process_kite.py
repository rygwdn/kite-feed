#!/usr/bin/env python3
"""
Process Kagi News API data, combine categories, filter, and merge duplicates.
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


def fetch_json(url: str) -> dict[str, Any] | list[Any]:
    """Fetch JSON data from a URL."""
    try:
        print(f"[LOG] Fetching {url}...", file=sys.stderr)
        response = requests.get(url, timeout=30, allow_redirects=True)
        response.raise_for_status()
        data = response.json()
        print(f"[LOG] Successfully fetched {url} ({len(str(data))} characters)", file=sys.stderr)
        return data
    except Exception as e:
        print(f"[LOG] Error fetching {url}: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)
        return {}


def get_available_categories(base_url: str) -> list[dict[str, Any]]:
    """Fetch available categories from the latest batch."""
    data = fetch_json(f"{base_url}/api/batches/latest/categories")
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("categories", [])
    return []


def get_batch_timestamp(base_url: str) -> str | None:
    """Fetch the latest batch and return its creation timestamp."""
    data = fetch_json(f"{base_url}/api/batches/latest")
    if isinstance(data, dict):
        return data.get("createdAt")
    return None


def extract_stories_from_response(data: dict[str, Any], category_slug: str, category_name: str) -> list[dict[str, Any]]:
    """Extract stories from a category stories response."""
    if not isinstance(data, dict):
        return []
    stories = data.get("stories", [])
    for story in stories:
        story["_category"] = category_slug
        story["_feed_category_name"] = category_name
    return stories


def get_source_urls_from_cluster(cluster: dict[str, Any]) -> list[str]:
    """Extract all source URLs from a cluster/story."""
    urls = set()

    articles = cluster.get("articles", [])
    for article in articles:
        article_link = article.get("link")
        if article_link:
            urls.add(article_link)

    quote_url = cluster.get("quote_source_url")
    if quote_url:
        urls.add(quote_url)

    perspectives = cluster.get("perspectives", [])
    for perspective in perspectives:
        sources = perspective.get("sources", [])
        for source in sources:
            source_url = source.get("url")
            if source_url:
                urls.add(source_url)

    return list(urls)


def get_primary_source_url(cluster: dict[str, Any]) -> str:
    """Get the primary source URL for deduplication."""
    articles = cluster.get("articles", [])
    if articles and articles[0].get("link"):
        return articles[0].get("link")

    if cluster.get("quote_source_url"):
        return cluster.get("quote_source_url")

    perspectives = cluster.get("perspectives", [])
    if perspectives:
        sources = perspectives[0].get("sources", [])
        if sources and sources[0].get("url"):
            return sources[0].get("url")

    cluster_str = json.dumps(cluster, sort_keys=True)
    return f"hash:{hashlib.md5(cluster_str.encode()).hexdigest()}"


def cluster_to_story(cluster: dict[str, Any], file_timestamp: Any = None, feed_category: str = "") -> dict[str, Any]:
    """Convert a cluster/story to internal story format."""
    feed_cat_display = cluster.get("_feed_category_name") or feed_category or cluster.get("_category", "")

    story = {
        "title": cluster.get("title", "Untitled"),
        "summary": cluster.get("short_summary", ""),
        "feed_category": feed_cat_display,
        "item_category": cluster.get("category", ""),
        "category": feed_cat_display,
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
        "secondary_image": cluster.get("secondary_image"),
        "domains": cluster.get("domains", []),
        "articles": cluster.get("articles", []),
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
        "business_angle": cluster.get("business_angle", ""),
        "international_reactions": cluster.get("international_reactions", []),
        "key_players": cluster.get("key_players", []),
        "travel_advisory": cluster.get("travel_advisory", ""),
        "emoji": cluster.get("emoji", ""),
        "location": cluster.get("location", ""),
    }

    story["url"] = get_primary_source_url(cluster)
    story["source_urls"] = get_source_urls_from_cluster(cluster)

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
        score = story.get("cluster_number", 999)
        score = 100 - score if score < 100 else 0

        if score >= min_score:
            filtered.append(story)
        elif min_score == 0:
            filtered.append(story)

    return filtered


def merge_duplicates(stories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge duplicate stories based on source article URLs."""
    seen_urls: dict[str, dict[str, Any]] = {}
    merged = []

    for story in stories:
        articles = story.get("articles", [])
        article_urls = []
        for article in articles:
            article_link = article.get("link")
            if article_link:
                article_urls.append(article_link)

        if not article_urls:
            primary_url = story.get("url", "")
            if primary_url and not primary_url.startswith("hash:"):
                article_urls.append(primary_url)

        found_duplicate = False
        matching_url = None

        for url in article_urls:
            normalized_url = url.lower().strip()
            if normalized_url in seen_urls:
                found_duplicate = True
                matching_url = normalized_url
                break

        if found_duplicate:
            existing = seen_urls[matching_url]
            existing_articles = existing.get("articles", [])
            new_articles = story.get("articles", [])
            existing_article_links = {a.get("link") for a in existing_articles if a.get("link")}
            for article in new_articles:
                if article.get("link") not in existing_article_links:
                    existing_articles.append(article)
            existing["articles"] = existing_articles

            existing_urls = set(existing.get("source_urls", []))
            new_urls = set(story.get("source_urls", []))
            existing["source_urls"] = list(existing_urls | new_urls)

            existing_feed_cats = existing.get("feed_category", "")
            new_feed_cats = story.get("feed_category", "")
            if new_feed_cats and new_feed_cats != existing_feed_cats:
                existing_list = [existing_feed_cats] if existing_feed_cats else []
                new_list = [new_feed_cats] if new_feed_cats else []
                combined_feed_cats = list(set(existing_list + new_list))
                if len(combined_feed_cats) == 1:
                    existing["feed_category"] = combined_feed_cats[0]
                elif combined_feed_cats:
                    existing["feed_category"] = ", ".join(sorted(combined_feed_cats))

            existing_item_cat = existing.get("item_category", "")
            new_item_cat = story.get("item_category", "")
            if new_item_cat and not existing_item_cat:
                existing["item_category"] = new_item_cat

            for key in story:
                if key not in ["url", "source_urls", "articles", "feed_category", "item_category"]:
                    if story[key] and not existing.get(key):
                        existing[key] = story[key]
                    elif isinstance(story[key], list) and story[key]:
                        existing_list = existing.get(key, [])
                        combined = existing_list + story[key]
                        try:
                            existing[key] = list(set(combined))
                        except TypeError:
                            existing[key] = combined
        else:
            merged.append(story)
            for url in article_urls:
                normalized_url = url.lower().strip()
                if normalized_url and not normalized_url.startswith("hash:"):
                    seen_urls[normalized_url] = story

    return merged


def process_kite_feeds(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Main processing function using the Kagi News API."""
    all_stories = []

    category_slugs = config.get("feeds", {}).get("categories", [])
    top_n_per_feed = config.get("feeds", {}).get("top_n", 5)
    top_n_by_category = config.get("feeds", {}).get("top_n_by_category", {})
    base_url = config.get("feeds", {}).get("base_url", "https://news.kagi.com")

    # Fetch batch timestamp
    print(f"[LOG] Fetching latest batch from {base_url}/api/batches/latest...", file=sys.stderr)
    batch_timestamp = get_batch_timestamp(base_url)
    print(f"[LOG] Batch timestamp: {batch_timestamp}", file=sys.stderr)

    # Fetch available categories
    print(f"[LOG] Fetching category list from {base_url}/api/batches/latest/categories...", file=sys.stderr)
    available = get_available_categories(base_url)

    if not available:
        print("[LOG] Error: Could not fetch category list", file=sys.stderr)
        return []

    print(f"[LOG] Found {len(available)} available categories", file=sys.stderr)

    # Build lookup by categoryId slug (case-insensitive)
    category_lookup: dict[str, dict[str, Any]] = {}
    for cat in available:
        cat_id = cat.get("categoryId", "").lower()
        if cat_id:
            category_lookup[cat_id] = cat

    # Process each configured category
    for idx, category_slug in enumerate(category_slugs):
        print(f"[LOG] Processing category {idx + 1}/{len(category_slugs)}: {category_slug}...", file=sys.stderr)

        cat = category_lookup.get(category_slug.lower())
        if not cat:
            print(f"[LOG] Warning: Category '{category_slug}' not found in available categories", file=sys.stderr)
            print(f"[LOG] Available category IDs: {list(category_lookup.keys())[:20]}", file=sys.stderr)
            continue

        cat_uuid = cat.get("id")
        cat_name = cat.get("categoryName", category_slug)
        print(f"[LOG] Found category: {cat_name} (id={cat_uuid})", file=sys.stderr)

        # Fetch stories for this category
        stories_url = f"{base_url}/api/batches/latest/categories/{cat_uuid}/stories"
        print(f"[LOG] Fetching stories: {stories_url}...", file=sys.stderr)
        stories_data = fetch_json(stories_url)

        if not stories_data:
            print(f"[LOG] Warning: Could not fetch stories for {category_slug}", file=sys.stderr)
            continue

        raw_stories = extract_stories_from_response(stories_data, category_slug, cat_name)
        print(f"[LOG] Found {len(raw_stories)} stories in {cat_name}", file=sys.stderr)

        # Convert to internal story format
        category_stories = [cluster_to_story(s, batch_timestamp, category_slug) for s in raw_stories]
        print(f"[LOG] Converted {len(category_stories)} stories", file=sys.stderr)

        # Apply top_n per category
        category_top_n = top_n_by_category.get(category_slug, top_n_per_feed)
        print(f"[LOG] Using top_n={category_top_n} for {category_slug}", file=sys.stderr)
        if category_top_n and category_top_n > 0:
            category_stories.sort(key=lambda x: x.get("cluster_number", 999))
            original_count = len(category_stories)
            category_stories = category_stories[:category_top_n]
            print(f"[LOG] Selected top {len(category_stories)}/{original_count} stories from {cat_name}", file=sys.stderr)

        all_stories.extend(category_stories)
        print(f"[LOG] Total stories so far: {len(all_stories)}", file=sys.stderr)

    # Apply filters
    print(f"[LOG] Applying filters to {len(all_stories)} stories...", file=sys.stderr)
    filtered_stories = apply_filters(all_stories, config)
    print(
        f"[LOG] After filtering: {len(filtered_stories)} stories (removed {len(all_stories) - len(filtered_stories)})",
        file=sys.stderr,
    )

    # Merge duplicates across categories
    print(f"[LOG] Merging duplicates from {len(filtered_stories)} stories...", file=sys.stderr)
    merged_stories = merge_duplicates(filtered_stories)
    duplicates_merged = len(filtered_stories) - len(merged_stories)
    print(
        f"[LOG] After merging duplicates: {len(merged_stories)} stories (merged {duplicates_merged} duplicates)",
        file=sys.stderr,
    )

    if merged_stories:
        print("[LOG] Final story titles:", file=sys.stderr)
        for i, story in enumerate(merged_stories[:5]):
            title = story.get("title", "Untitled")[:60]
            print(f"[LOG]   {i + 1}. {title}", file=sys.stderr)
        if len(merged_stories) > 5:
            print(f"[LOG]   ... and {len(merged_stories) - 5} more", file=sys.stderr)

    return merged_stories


if __name__ == "__main__":
    import sys
    from datetime import datetime

    print(f"[LOG] process_kite.py started at: {datetime.now().isoformat()}", file=sys.stderr)
    config = load_config()
    print("[LOG] Config loaded successfully", file=sys.stderr)

    stories = process_kite_feeds(config)
    print(f"[LOG] Processing complete: {len(stories)} stories ready for output", file=sys.stderr)

    stories_json = json.dumps(stories, indent=2, ensure_ascii=False)
    print(f"[LOG] JSON output size: {len(stories_json)} characters", file=sys.stderr)
    print(stories_json)
