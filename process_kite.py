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
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return {}


def extract_stories(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract stories from Kagi Kite JSON structure."""
    stories = []
    
    # Handle different possible structures
    if isinstance(data, dict):
        # Check for common keys that might contain stories
        if "stories" in data:
            stories.extend(data["stories"])
        elif "items" in data:
            stories.extend(data["items"])
        elif "articles" in data:
            stories.extend(data["articles"])
        elif "news" in data:
            stories.extend(data["news"])
        else:
            # If it's a list of stories directly
            if all(isinstance(v, dict) for v in data.values() if isinstance(v, dict)):
                # Try to find story-like objects
                for key, value in data.items():
                    if isinstance(value, list):
                        stories.extend(value)
                    elif isinstance(value, dict) and "url" in value:
                        stories.append(value)
    
    elif isinstance(data, list):
        stories.extend(data)
    
    return stories


def get_source_url(story: Dict[str, Any]) -> str:
    """Extract the source article URL from a story."""
    # Try various possible fields
    for field in ["url", "source_url", "article_url", "link", "source", "original_url"]:
        if field in story and story[field]:
            return str(story[field])
    
    # If no URL found, generate a hash-based ID
    story_str = json.dumps(story, sort_keys=True)
    return f"hash:{hashlib.md5(story_str.encode()).hexdigest()}"


def apply_filters(stories: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply filters to stories based on configuration."""
    if not config.get("filters", {}).get("enabled", True):
        return stories
    
    filtered = []
    min_score = config.get("filters", {}).get("min_score", 0)
    
    for story in stories:
        # Apply score filter if score field exists
        score = story.get("score", story.get("relevance", story.get("importance", 0)))
        if isinstance(score, (int, float)) and score >= min_score:
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
        source_url = get_source_url(story)
        
        # Normalize URL for comparison
        normalized_url = source_url.lower().strip()
        
        if normalized_url not in seen_urls:
            seen_urls[normalized_url] = story
            merged.append(story)
        else:
            # Merge with existing story (prefer more complete data)
            existing = seen_urls[normalized_url]
            # Merge dictionaries, preferring non-empty values
            merged_story = {**existing, **story}
            for key in story:
                if story[key] and not existing.get(key):
                    merged_story[key] = story[key]
            # Update in merged list
            idx = merged.index(existing)
            merged[idx] = merged_story
    
    return merged


def process_kite_feeds(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Main processing function."""
    all_stories = []
    
    # Fetch all configured feeds
    feed_urls = config.get("feeds", {}).get("list", [])
    
    for url in feed_urls:
        print(f"Fetching {url}...", file=sys.stderr)
        data = fetch_json(url)
        stories = extract_stories(data)
        print(f"Found {len(stories)} stories in {url}", file=sys.stderr)
        all_stories.extend(stories)
    
    # Apply filters
    filtered_stories = apply_filters(all_stories, config)
    print(f"After filtering: {len(filtered_stories)} stories", file=sys.stderr)
    
    # Merge duplicates
    merged_stories = merge_duplicates(filtered_stories)
    print(f"After merging duplicates: {len(merged_stories)} stories", file=sys.stderr)
    
    # Apply top_n limit if specified
    top_n = config.get("feeds", {}).get("top_n")
    if top_n and top_n > 0:
        # Sort by score/relevance if available, otherwise keep original order
        try:
            merged_stories.sort(
                key=lambda x: x.get("score", x.get("relevance", x.get("importance", 0))),
                reverse=True
            )
        except:
            pass
        merged_stories = merged_stories[:top_n]
        print(f"After top_n limit: {len(merged_stories)} stories", file=sys.stderr)
    
    return merged_stories


if __name__ == "__main__":
    config = load_config()
    stories = process_kite_feeds(config)
    
    # Output as JSON
    print(json.dumps(stories, indent=2, ensure_ascii=False))
