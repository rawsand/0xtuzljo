import requests

# ==============================
# PLAYLIST URLS (Replace with real URLs)
# ==============================
playlist_links = [
    #"https://rkdyiptv.pages.dev/Playlist/Cricket.m3u",
    "https://github.com/etcvai/zero_etcvai/blob/main/icc.m3u8",
    "https://github.com/etcvai/ExtenderMax/blob/main/iptv.m3u8",
    "https://github.com/atanuroy22/iptv/blob/main/output/sports.m3u"
]

# ==============================
# FILTER CONFIGURATION (Hardcoded per link)
# ==============================
filters = [
    {"type": "All"},  # Link 1 → All channels
    {"type": "All"},  # Link 2 → All channels
    {"type": "GroupTitle", "values": ["AI SPORTS", "EXTRAS"]},  # Link 3
    {"type": "ChannelName", "value": "STAR SPORTS"}  # Link 4 (partial match)
]

OUTPUT_FILE = "8b249zhj3vg65us_sports4.m3u"


# ==============================
# FUNCTION TO EXTRACT CHANNEL BLOCKS
# ==============================
def extract_channels(content):
    lines = content.splitlines()
    channels = []
    current_block = []

    for line in lines:
        if line.startswith("#EXTINF"):
            if current_block:
                channels.append(current_block)
                current_block = []
        if line.strip() != "":
            current_block.append(line)

    if current_block:
        channels.append(current_block)

    return channels


# ==============================
# FILTER FUNCTIONS
# ==============================
def filter_channels(channels, filter_config):
    filter_type = filter_config["type"]

    if filter_type == "All":
        return channels

    filtered = []

    for block in channels:
        extinf_line = block[0]

        if filter_type == "GroupTitle":
            for group in filter_config["values"]:
                if f'group-title="{group}"' in extinf_line:
                    filtered.append(block)
                    break

        elif filter_type == "ChannelName":
            channel_name = extinf_line.split(",")[-1]
            if filter_config["value"].lower() in channel_name.lower():
                filtered.append(block)

    return filtered


# ==============================
# MAIN PROCESS
# ==============================
all_filtered_channels = []

for index, url in enumerate(playlist_links):
    print(f"Processing Link {index + 1}...")

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch: {url}")
        continue

    content = response.text

    channels = extract_channels(content)
    filtered = filter_channels(channels, filters[index])

    all_filtered_channels.extend(filtered)


# ==============================
# WRITE OUTPUT FILE
# ==============================
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for block in all_filtered_channels:
        for line in block:
            f.write(line + "\n")

print(f"\nDone! Output saved to {OUTPUT_FILE}")
