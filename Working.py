import os
import sys
import requests
import re

# (Keep fetch_m3u_blocks_from_url, fetch_m3u_blocks_from_file, and split_into_blocks functions the same)

def fetch_m3u_blocks_from_url(url):
    """Fetch playlist from URL and split into blocks (#EXTINF ...)."""
    response = requests.get(url)
    response.raise_for_status()
    lines = [line.strip() for line in response.text.splitlines() if line.strip()]
    return split_into_blocks(lines)

def fetch_m3u_blocks_from_file(file_path):
    """Read playlist from local file and split into blocks (#EXTINF ...)."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.read()
    # Return blocks here, not raw text, so we can process them consistently
    raw_lines = [line.strip() for line in lines.splitlines() if line.strip()]
    return split_into_blocks(raw_lines)

def split_into_blocks(lines):
    """Split M3U content into blocks starting with #EXTINF."""
    blocks = []
    current_block = []
    for line in lines:
        if line.startswith("#EXTINF"):
            if current_block:
                blocks.append("\n".join(current_block))
                current_block = []
        current_block.append(line)
    if current_block:
        blocks.append("\n".join(current_block))
    return blocks

def filter_m3u_blocks(urls, channel_names, exclude_channels, output_dir="output_blocks", output_file="filtered_playlist.m3u"):
    all_blocks = []

    # Fetch from URLs
    for url in urls:
        print(f"Fetching playlist from URL: {url}")
        all_blocks.extend(fetch_m3u_blocks_from_url(url))

    # Fetch from local file (hardcoded path) and add to all_blocks
    local_file = "8b249zhj3vg65us_st_so_zfive.m3u"   # 👈 change if needed
    if os.path.exists(local_file):
        print(f"Reading playlist from local file: {local_file}")
        all_blocks.extend(fetch_m3u_blocks_from_file(local_file))

    # Define patterns for filtering and modifying
    group_title_pattern = r'group-title=".*?"'
    group_title_replacement = r'group-title="General"'
    link_pattern = re.compile(r'^(http|https|ftp)://.*', re.IGNORECASE)

    matched_blocks = []
    seen_channels = set()
    seen_links = set()

    for block in all_blocks:
        lines = block.strip().splitlines()
        extinf_line = None
        stream_url = None

        # Iterate through the lines in the block to find the #EXTINF and the URL
        for line in lines:
            if line.startswith("#EXTINF"):
                extinf_line = line
            elif link_pattern.match(line):
                stream_url = line
                # Break once the URL is found
                break

        if extinf_line and stream_url:
            channel_name = extinf_line.split(",")[-1].strip()

            include_match = any(name.lower() in channel_name.lower() for name in channel_names)
            exclude_match = any(bad.lower() in channel_name.lower() for bad in exclude_channels)

            if include_match and not exclude_match:
                if stream_url not in seen_links:
                    # Apply find and replace (group-title) modification
                    modified_block = re.sub(group_title_pattern, group_title_replacement, block)
                    matched_blocks.append(modified_block + "\n\n") # Add extra newlines for spacing
                    seen_links.add(stream_url)
                    # seen_channels is now less important as we are tracking by unique URL
                else:
                    print(f"Skipping duplicate URL for channel: {channel_name}")
            elif exclude_match:
                print(f"Excluded unwanted channel: {channel_name}")

    # Ensure output folder exists and write the final unique blocks
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_file)
    with open(output_path, "w", encoding="utf-8") as out:
        out.write("#EXTM3U\n\n")
        # Write the list of unique blocks joined together
        out.write("".join(matched_blocks))

    print(f"Saved {len(matched_blocks)} unique matched blocks into: {output_path}")
    return matched_blocks

# (Keep __main__ block the same)

if __name__ == "__main__":
    # URLs passed as arguments
    urls = [arg for arg in sys.argv[1:] if arg.startswith("http")]

    # ✅ Channels you want
    channel_names = [
        "Zee Marathi",
        "Star Plus",
        "Star Pravah",
        "Set HD",
        "Sony HD",
        "Shemaroo Marathibana",
        "Sony TV HD"
        ]

    # ❌ Channels you don’t want (blacklist)
    exclude_channels = [
        "STAR PLUS HD USA",    # Example
        "STAR PLUS USA",    # Example
        "STAR PRAVAH MOVIES",           
        "STAR PRAVAH US",
        "ZEE MARATHI USA",
        "SONY TV HD | UK",
        "Star Gold Thrills"
    ]

    filter_m3u_blocks(urls, channel_names, exclude_channels)
