#!/usr/bin/env python3
"""
Run the complete processing workflow:
1. Process Kite feeds -> processed_stories.json
2. Generate RSS feed -> feed.xml
3. Generate HTML pages -> index.html and stories/*.html
"""

import hashlib
import json
import os
import sys
from datetime import datetime

from generate_html import generate_index_html, generate_story_html
from generate_rss import generate_rss
from generate_utils import get_story_slug
from process_kite import load_config, process_kite_feeds


def get_file_info(filepath: str) -> dict:
    """Get file information for logging."""
    info = {"path": filepath, "exists": False}
    if os.path.exists(filepath):
        info["exists"] = True
        info["size"] = os.path.getsize(filepath)
        info["mtime"] = datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
        # Calculate checksum for first 1KB to verify content
        try:
            with open(filepath, "rb") as f:
                content_sample = f.read(1024)
                info["checksum_sample"] = hashlib.md5(content_sample).hexdigest()
        except Exception as e:
            info["checksum_error"] = str(e)
    return info


def log_file_write(filepath: str, content: str, description: str = ""):
    """Write file and log detailed information."""
    try:
        # Write file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        # Verify write
        file_info = get_file_info(filepath)
        print(f"   [LOG] Wrote {description or filepath}:")
        print(f"   [LOG]   - Size: {file_info.get('size', 0)} bytes")
        print(f"   [LOG]   - Modified: {file_info.get('mtime', 'N/A')}")
        print(f"   [LOG]   - Checksum (first 1KB): {file_info.get('checksum_sample', 'N/A')}")

        # Verify content matches
        if os.path.exists(filepath):
            with open(filepath, encoding="utf-8") as f:
                read_content = f.read()
            if read_content == content:
                print("   [LOG]   - Content verification: ✓ PASSED")
            else:
                print("   [LOG]   - Content verification: ✗ FAILED (content mismatch)")
                print(f"   [LOG]   - Expected length: {len(content)}, Actual length: {len(read_content)}")
        return True
    except Exception as e:
        print(f"   [LOG]   - Write failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main(output_dir: str = "."):
    """Run the complete processing workflow.
    
    Args:
        output_dir: Directory where output files should be written (default: current directory)
    """
    print("=== Running Processing Workflow ===\n")
    print(f"[LOG] Workflow started at: {datetime.now().isoformat()}")
    print(f"[LOG] Working directory: {os.getcwd()}")
    print(f"[LOG] Output directory: {output_dir}")
    print(f"[LOG] Python version: {sys.version}\n")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Log initial directory state
    print("[LOG] Initial directory contents:")
    try:
        for item in sorted(os.listdir(".")):
            if os.path.isfile(item):
                size = os.path.getsize(item)
                print(f"   [LOG]   - {item} ({size} bytes)")
            elif os.path.isdir(item):
                print(f"   [LOG]   - {item}/ (directory)")
    except Exception as e:
        print(f"   [LOG]   Error listing directory: {e}")

    # Step 1: Process Kite feeds
    print("\n1. Processing Kite feeds...")
    try:
        config = load_config()
        print("[LOG] Config loaded from config.json")
        stories = process_kite_feeds(config)
        print(f"[LOG] Processed {len(stories)} stories from Kite feeds")

        # Check if processed_stories.json exists before writing
        processed_stories_path = os.path.join(output_dir, "processed_stories.json")
        old_file_info = get_file_info(processed_stories_path)
        if old_file_info["exists"]:
            print("[LOG] Existing processed_stories.json found:")
            print(f"   [LOG]   - Size: {old_file_info.get('size', 0)} bytes")
            print(f"   [LOG]   - Modified: {old_file_info.get('mtime', 'N/A')}")

        # Serialize stories to JSON
        stories_json = json.dumps(stories, indent=2, ensure_ascii=False)
        success = log_file_write(processed_stories_path, stories_json, "processed_stories.json")

        if not success:
            print("   ✗ Failed to write processed_stories.json")
            sys.exit(1)

        # Verify file was created
        new_file_info = get_file_info(processed_stories_path)
        if new_file_info["exists"]:
            print(f"   ✓ Processed {len(stories)} stories saved to processed_stories.json")
            if old_file_info["exists"]:
                size_diff = new_file_info["size"] - old_file_info["size"]
                print(f"   [LOG] File size change: {size_diff:+d} bytes")
        else:
            print("   ✗ ERROR: processed_stories.json was not created!")
            sys.exit(1)
    except Exception as e:
        print(f"   ✗ Failed to process Kite feeds: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # Step 2: Generate RSS feed
    print("\n2. Generating RSS feed...")
    try:
        # Verify processed_stories.json exists and is readable
        processed_stories_path = os.path.join(output_dir, "processed_stories.json")
        if not os.path.exists(processed_stories_path):
            print("   ✗ ERROR: processed_stories.json not found!")
            sys.exit(1)

        with open(processed_stories_path, encoding="utf-8") as f:
            stories = json.load(f)
        print(f"[LOG] Loaded {len(stories)} stories from processed_stories.json")

        config = json.load(open("config.json"))
        print("[LOG] Config reloaded from config.json")

        rss_xml = generate_rss(stories, config)
        print(f"[LOG] Generated RSS XML ({len(rss_xml)} characters)")

        # Check if feed.xml exists before writing
        feed_xml_path = os.path.join(output_dir, "feed.xml")
        old_file_info = get_file_info(feed_xml_path)
        if old_file_info["exists"]:
            print("[LOG] Existing feed.xml found:")
            print(f"   [LOG]   - Size: {old_file_info.get('size', 0)} bytes")
            print(f"   [LOG]   - Modified: {old_file_info.get('mtime', 'N/A')}")

        success = log_file_write(feed_xml_path, rss_xml, "feed.xml")

        if not success:
            print("   ✗ Failed to write feed.xml")
            sys.exit(1)

        # Verify file was created
        new_file_info = get_file_info(feed_xml_path)
        if new_file_info["exists"]:
            print("   ✓ RSS feed saved to feed.xml")
            if old_file_info["exists"]:
                size_diff = new_file_info["size"] - old_file_info["size"]
                print(f"   [LOG] File size change: {size_diff:+d} bytes")
        else:
            print("   ✗ ERROR: feed.xml was not created!")
            sys.exit(1)
    except Exception as e:
        print(f"   ✗ Failed to generate RSS feed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # Step 3: Generate HTML pages
    print("\n3. Generating HTML pages...")
    try:
        # Verify processed_stories.json exists
        processed_stories_path = os.path.join(output_dir, "processed_stories.json")
        if not os.path.exists(processed_stories_path):
            print("   ✗ ERROR: processed_stories.json not found!")
            sys.exit(1)

        with open(processed_stories_path, encoding="utf-8") as f:
            stories = json.load(f)
        print(f"[LOG] Loaded {len(stories)} stories from processed_stories.json")

        config = json.load(open("config.json"))

        # Create stories directory
        stories_dir = os.path.join(output_dir, "stories")
        os.makedirs(stories_dir, exist_ok=True)
        print(f"[LOG] Stories directory: {stories_dir} (exists: {os.path.exists(stories_dir)})")

        # Count existing story files
        existing_stories = []
        if os.path.exists(stories_dir):
            existing_stories = [f for f in os.listdir(stories_dir) if f.endswith(".html")]
        print(f"[LOG] Found {len(existing_stories)} existing story HTML files")

        # Generate individual story pages
        generated_count = 0
        for i, story in enumerate(stories):
            story_slug = get_story_slug(story)
            filename = os.path.join(stories_dir, f"{story_slug}.html")
            html = generate_story_html(story, config)

            # Log first few stories in detail
            if i < 3:
                print(f"[LOG] Generating story {i + 1}/{len(stories)}: {filename}")
                print(f"   [LOG]   - Title: {story.get('title', 'N/A')[:50]}")
                print(f"   [LOG]   - HTML size: {len(html)} characters")

            success = log_file_write(filename, html, f"story page {i + 1}: {filename}")
            if success:
                generated_count += 1
            else:
                print(f"   ✗ Failed to write {filename}")

        print(f"[LOG] Generated {generated_count}/{len(stories)} story pages")

        # Generate index page
        print("[LOG] Generating index.html...")
        index_html_path = os.path.join(output_dir, "index.html")
        old_index_info = get_file_info(index_html_path)
        if old_index_info["exists"]:
            print("[LOG] Existing index.html found:")
            print(f"   [LOG]   - Size: {old_index_info.get('size', 0)} bytes")
            print(f"   [LOG]   - Modified: {old_index_info.get('mtime', 'N/A')}")

        index_html = generate_index_html(stories, config)
        print(f"[LOG] Generated index HTML ({len(index_html)} characters)")

        success = log_file_write(index_html_path, index_html, "index.html")

        if not success:
            print("   ✗ Failed to write index.html")
            sys.exit(1)

        # Verify index.html was created
        new_index_info = get_file_info(index_html_path)
        if new_index_info["exists"]:
            print(f"   ✓ Generated {len(stories)} story pages and index.html")
            if old_index_info["exists"]:
                size_diff = new_index_info["size"] - old_index_info["size"]
                print(f"   [LOG] Index.html size change: {size_diff:+d} bytes")
        else:
            print("   ✗ ERROR: index.html was not created!")
            sys.exit(1)
    except Exception as e:
        print(f"   ✗ Failed to generate HTML pages: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # Final verification
    print(f"\n[LOG] Final directory contents in {output_dir}:")
    try:
        for item in sorted(os.listdir(output_dir)):
            item_path = os.path.join(output_dir, item)
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                mtime = datetime.fromtimestamp(os.path.getmtime(item_path)).isoformat()
                print(f"   [LOG]   - {item} ({size} bytes, modified: {mtime})")
            elif os.path.isdir(item_path):
                file_count = len([f for f in os.listdir(item_path) if os.path.isfile(os.path.join(item_path, f))])
                print(f"   [LOG]   - {item}/ (directory, {file_count} files)")
    except Exception as e:
        print(f"   [LOG]   Error listing directory: {e}")

    # Verify key files exist
    print("\n[LOG] Verifying key output files:")
    key_files = ["processed_stories.json", "feed.xml", "index.html"]
    all_exist = True
    for key_file in key_files:
        key_file_path = os.path.join(output_dir, key_file)
        exists = os.path.exists(key_file_path)
        if exists:
            size = os.path.getsize(key_file_path)
            print(f"   [LOG]   ✓ {key_file} exists ({size} bytes)")
        else:
            print(f"   [LOG]   ✗ {key_file} MISSING!")
            all_exist = False

    stories_dir_path = os.path.join(output_dir, "stories")
    if os.path.exists(stories_dir_path):
        story_files = [f for f in os.listdir(stories_dir_path) if f.endswith(".html")]
        print(f"   [LOG]   ✓ stories/ directory exists ({len(story_files)} HTML files)")
    else:
        print("   [LOG]   ✗ stories/ directory MISSING!")
        all_exist = False

    if not all_exist:
        print("\n[LOG] ⚠️  WARNING: Some key files are missing!")
        sys.exit(1)

    print("\n=== Processing Workflow Completed Successfully ===")
    print(f"[LOG] Workflow completed at: {datetime.now().isoformat()}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process Kite feeds and generate HTML/RSS output")
    parser.add_argument(
        "--output-dir",
        "-o",
        default=".",
        help="Directory where output files should be written (default: current directory)"
    )
    args = parser.parse_args()
    
    main(output_dir=args.output_dir)
