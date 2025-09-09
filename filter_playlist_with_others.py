import os
import sys
import requests

def fetch_m3u_blocks_from_url(url):
    """Fetch playlist from URL and split into blocks (#EXTINF ...)."""
    response = requests.get(url)
    response.raise_for_status()
    lines = [line.strip() for line in response.text.splitlines() if line.strip()]
    return split_into_blocks(lines)

def fetch_m3u_blocks_from_file(file_path):
    """Read playlist from local file and split into blocks (#EXTINF ...)."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    return split_into_blocks(lines)

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

def filter_m3u_blocks(urls, local_file, channel_names, output_dir="output_blocks", output_file="filtered_playlist.m3u"):
    all_blocks = []

    # Fetch from URLs
    for url in urls:
        print(f"Fetching playlist from URL: {url}")
        all_blocks.extend(fetch_m3u_blocks_from_url(url))

    # Fetch from local file
    if local_file and os.path.exists(local_file):
        print(f"Reading playlist from local file: {local_file}")
        all_blocks.extend(fetch_m3u_blocks_from_file(local_file))

    # Filter and remove duplicates
    matched_blocks, seen_channels = [], set()
    for block in all_blocks:
        extinf_line = block.splitlines()[0]
        channel_name = extinf_line.split(",")[-1].strip()
        if any(name.lower() in channel_name.lower() for name in channel_names):
            if channel_name.lower() not in seen_channels:
                matched_blocks.append(block)
                seen_channels.add(channel_name.lower())

    # Ensure output folder exists
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_file)
    with open(output_path, "w", encoding="utf-8") as out:
        out.write("#EXTM3U\n\n")
        for block in matched_blocks:
            out.write(block + "\n\n")

    print(f"Saved {len(matched_blocks)} unique matched blocks into: {output_path}")
    return matched_blocks

if __name__ == "__main__":
    # URLs passed as arguments (can be 0, 1, or more)
    urls = [arg for arg in sys.argv[1:] if arg.startswith("http")]
    # Local file (if provided as an argument, e.g., local.m3u)
    local_file = "8b249zhj3vg65us_jiotvbe1_st_so_edit.m3u"
    channel_names = [
        "Disney Junior",
        "Star Gold HD",
        "Star Gold 2 Romance",
        "Sony Max 2",
        "Sony Max HD    
        ]

    filter_m3u_blocks(urls, local_file, channel_names)
