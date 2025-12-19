#!/usr/bin/env python3
"""
Run the complete processing workflow:
1. Process Kite feeds -> processed_stories.json
2. Generate RSS feed -> feed.xml
3. Generate HTML pages -> index.html and stories/*.html
"""

import json
import os
import sys

from generate_html import generate_index_html, generate_story_html
from generate_rss import generate_rss
from generate_utils import get_story_slug
from process_kite import load_config, process_kite_feeds


def main():
    """Run the complete processing workflow."""
    print("=== Running Processing Workflow ===\n")

    # Step 1: Process Kite feeds
    print("1. Processing Kite feeds...")
    try:
        config = load_config()
        stories = process_kite_feeds(config)

        with open("processed_stories.json", "w", encoding="utf-8") as f:
            json.dump(stories, f, indent=2, ensure_ascii=False)
        print(f"   ✓ Processed {len(stories)} stories saved to processed_stories.json")
    except Exception as e:
        print(f"   ✗ Failed to process Kite feeds: {e}")
        sys.exit(1)

    # Step 2: Generate RSS feed
    print("\n2. Generating RSS feed...")
    try:
        with open("processed_stories.json", encoding="utf-8") as f:
            stories = json.load(f)
        config = json.load(open("config.json"))

        rss_xml = generate_rss(stories, config)
        with open("feed.xml", "w", encoding="utf-8") as f:
            f.write(rss_xml)
        print("   ✓ RSS feed saved to feed.xml")
    except Exception as e:
        print(f"   ✗ Failed to generate RSS feed: {e}")
        sys.exit(1)

    # Step 3: Generate HTML pages
    print("\n3. Generating HTML pages...")
    try:
        with open("processed_stories.json", encoding="utf-8") as f:
            stories = json.load(f)
        config = json.load(open("config.json"))

        # Create stories directory
        os.makedirs("stories", exist_ok=True)

        # Generate individual story pages
        for story in stories:
            story_slug = get_story_slug(story)
            filename = f"stories/{story_slug}.html"
            html = generate_story_html(story, config)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)

        # Generate index page
        index_html = generate_index_html(stories, config)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(index_html)

        print(f"   ✓ Generated {len(stories)} story pages and index.html")
    except Exception as e:
        print(f"   ✗ Failed to generate HTML pages: {e}")
        sys.exit(1)

    print("\n=== Processing Workflow Completed Successfully ===")


if __name__ == "__main__":
    main()
