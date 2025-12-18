#!/usr/bin/env python3
"""
Process Kagi Kite JSON files, combine them, filter, and merge duplicates.
"""

import json
import sys
import hashlib
from typing import List, Dict, Any, Set
from urllib.parse import urlparse
import requests


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load configuration from JSON file."""
    with open(config_path, "r") as f:
        return json.load(f)


def fetch_json(url: str) -> Dict[str, Any]:
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


def extract_clusters_from_category(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract clusters from a category JSON file."""
    clusters = data.get("clusters", [])
    category_name = data.get("category", "")
    
    # Add category name to each cluster
    for cluster in clusters:
        cluster["_category"] = category_name
    
    return clusters


def get_source_urls_from_cluster(cluster: Dict[str, Any]) -> List[str]:
    """Extract all source URLs from a cluster."""
    urls = set()
    
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


def get_primary_source_url(cluster: Dict[str, Any]) -> str:
    """Get the primary source URL for deduplication."""
    urls = get_source_urls_from_cluster(cluster)
    
    # Prefer quote_source_url, then first perspective source, then image link
    if cluster.get("quote_source_url"):
        return cluster.get("quote_source_url")
    elif urls:
        return urls[0]
    else:
        # Generate hash-based ID if no URL found
        cluster_str = json.dumps(cluster, sort_keys=True)
        return f"hash:{hashlib.md5(cluster_str.encode()).hexdigest()}"


def cluster_to_story(cluster: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a cluster to a story format."""
    story = {
        "title": cluster.get("title", "Untitled"),
        "summary": cluster.get("short_summary", ""),
        "category": cluster.get("_category", cluster.get("category", "")),
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
    
    # Set primary source URL
    story["url"] = get_primary_source_url(cluster)
    story["source_urls"] = get_source_urls_from_cluster(cluster)
    
    # Set published date (use timestamp if available)
    if "timestamp" in cluster:
        story["published"] = cluster["timestamp"]
    
    return story


def apply_filters(stories: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
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


def merge_duplicates(stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merge duplicate stories based on source article URLs."""
    seen_urls: Set[str] = {}
    merged = []
    
    for story in stories:
        source_url = story.get("url", "")
        
        # Normalize URL for comparison
        normalized_url = source_url.lower().strip()
        
        # Skip hash-based URLs for deduplication
        if normalized_url.startswith("hash:"):
            merged.append(story)
            continue
        
        if normalized_url not in seen_urls:
            seen_urls[normalized_url] = story
            merged.append(story)
        else:
            # Merge with existing story (prefer more complete data)
            existing = seen_urls[normalized_url]
            # Merge source URLs
            existing_urls = set(existing.get("source_urls", []))
            new_urls = set(story.get("source_urls", []))
            existing["source_urls"] = list(existing_urls | new_urls)
            
            # Merge other fields, preferring non-empty values
            for key in story:
                if key not in ["url", "source_urls"]:
                    if story[key] and not existing.get(key):
                        existing[key] = story[key]
                    elif isinstance(story[key], list) and story[key]:
                        existing_list = existing.get(key, [])
                        existing[key] = list(set(existing_list + story[key]))
    
    return merged


def process_kite_feeds(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Main processing function."""
    all_stories = []
    
    # Get category names from config
    categories = config.get("feeds", {}).get("categories", [])
    top_n_per_feed = config.get("feeds", {}).get("top_n", 5)
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
        
        # Convert clusters to stories
        category_stories = [cluster_to_story(cluster) for cluster in clusters]
        
        # Apply top_n per feed (sort by cluster_number, lower is better)
        if top_n_per_feed and top_n_per_feed > 0:
            category_stories.sort(key=lambda x: x.get("cluster_number", 999))
            category_stories = category_stories[:top_n_per_feed]
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
