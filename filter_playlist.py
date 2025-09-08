import os
import sys
import requests

def fetch_m3u_blocks(url):
    response = requests.get(url)
    response.raise_for_status()
    lines = [line.strip() for line in response.text.splitlines() if line.strip()]

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

def filter_m3u_blocks_from_urls(urls, channel_names, output_dir="output_blocks", output_file="filtered_playlist.m3u"):
    all_blocks = []
    for url in urls:
        print(f"Fetching playlist: {url}")
        all_blocks.extend(fetch_m3u_blocks(url))

    matched_blocks, seen_channels = [], set()
    for block in all_blocks:
        extinf_line = block.splitlines()[0]
        channel_name = extinf_line.split(",")[-1].strip()
        if any(name.lower() in channel_name.lower() for name in channel_names):
            if channel_name.lower() not in seen_channels:
                matched_blocks.append(block)
                seen_channels.add(channel_name.lower())

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_file)
    with open(output_path, "w", encoding="utf-8") as out:
        out.write("#EXTM3U\n\n")
        for block in matched_blocks:
            out.write(block + "\n\n")

    print(f"Saved {len(matched_blocks)} unique matched blocks into: {output_path}")

if __name__ == "__main__":
    urls = sys.argv[1:]  # URLs passed from workflow
    channel_names = ["Disney Junior", "Star Gold HD", "Star Gold 2 Romance, "Zee Marathi HD"]
    filter_m3u_blocks_from_urls(urls, channel_names)
