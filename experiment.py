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

def filter_m3u_blocks(urls, channel_names, exclude_channels, output_dir="output_blocks", output_file="filtered_playlist.m3u"):
    all_blocks = []

    # Fetch from URLs
    for url in urls:
        print(f"Fetching playlist from URL: {url}")
        all_blocks.extend(fetch_m3u_blocks_from_url(url))

    # Fetch from local file (hardcoded path)
    local_file = "local.m3u"   # 👈 change if needed
    if os.path.exists(local_file):
        print(f"Reading playlist from local file: {local_file}")
        all_blocks.extend(fetch_m3u_blocks_from_file(local_file))

    # Filter with include/exclude rules
    matched_blocks, seen_channels = [], set()
    for block in all_blocks:
        extinf_line = block.splitlines()[0]
        channel_name = extinf_line.split(",")[-1].strip()

        include_match = any(name.lower() in channel_name.lower() for name in channel_names)
        exclude_match = any(bad.lower() in channel_name.lower() for bad in exclude_channels)

        if include_match and not exclude_match:
            if channel_name.lower() not in seen_channels:
                matched_blocks.append(block)
                seen_channels.add(channel_name.lower())
            else:
                print(f"Skipping duplicate: {channel_name}")
        elif exclude_match:
            print(f"Excluded unwanted channel: {channel_name}")

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
    # URLs passed as arguments
    urls = [arg for arg in sys.argv[1:] if arg.startswith("http")]

    # ✅ Channels you want
    channel_names = [
        "Star Utsav Movies",
        "Star Gold HD",
        "Star Gold",
        "Star Gold 2",
        "Star Gold 2 HD",
        "Star Gold Select",
        "Star Gold Select HD",
        "Star Movies HD",
        "Star Movies",
        "Star Movies Select HD",
        "Star Sports 1",
        "Star Sports 1 Hindi HD", 
        "&Pictures HD",
        "&Pictures",
        "&xplorHD",
        "Zee Action",
        "Colors Cineplex HD",
        "Colors Cineplex",
        "Colors Cineplex Superhit",
        "Colors Cineplex Bollywood",
        "Zee Anmol Cinema",
        "Zee Anmol Cinema 2",
        "Zee Bollywood",
        "Zee Cinema HD",
        "Zee Cinema",
        "Zee Classic",
        "Zee Talkies HD",
        "Zee Talkies",
        "Aaj Tak",
        "News 18 India",
        "ABP News India",
        "India Today",
        "Zee Bharat",
        "Zee News",
        "India TV",
        "Lokshahi News",
        "Zee 24 Taas",
        "9X Jalwa",
        "9XM",
        "MTV",
        "MTV HD Plus",
        "Music India",
        "Colors HD",
        "Colors Marathi HD",
        "Zee TV HD",
        "Zee Yuva",
        "Zee Marathi HD",
        "Zing",
        "Zee Zest HD",
        "Food Food",
        "GOOD TiMES",
        "Foodxp",
        "Epic",
        "TLC English",
        "TLC Hindi",
        "Travelxp HD",
        "Travelxp HD Hindi",
        "Zee Business",
        "CNBC Tv 18",
        "ET Now",
        "NDTV Profit",
        "Animal Planet HD World",
        "Animal Planet Hindi",
        "Animal Planet English",
        "Discovery Channel Hindi",
        "History TV18 HD Hindi"
        "Sony Max 2",
        "Sony Max HD",
        "STAR GOLD ROMANCE b1g",
        "HINDI HITS",
        "IN | ZOOM MUSIC HD",
        "T Play Music",
        "Star Gold Romance CA",
        "SET HD",
        "Sony MAX",
        "Sony WAH",
        "Sony PIX HD",
        "NDTV Marathi",
        "News18 Lokmat",
        "TV9 Marathi",
        "Abp Majha",
        "NDTV India",
        "NDTV 24x7",
        "Discovery Kids 2"
    ]

    # ❌ Channels you don’t want (blacklist)
    exclude_channels = [
        "Zee Cinemalu",    # Example
        "Zee Cinemalu HD",    # Example
        "MTV Beats HD",           
        "MTV Beats SD",
        "Zee News Uttar Pradesh Uttrakhand"
    ]

    filter_m3u_blocks(urls, channel_names, exclude_channels)
