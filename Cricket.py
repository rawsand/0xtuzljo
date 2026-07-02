import os
import re
import requests

# URL where the channels text file is located
URL = "https://raw.githubusercontent.com/rawsand/telegram-github-bot/refs/heads/main/links.txt"

# URL containing channel-name / stream-url pairs
TEXT_FILE_URL = "https://raw.githubusercontent.com/rawsand/0xtuzljo/refs/heads/main/channels.txt"

# Output file
OUTPUT_FILE = "8b249zhj3vg65us_sports.m3u"

# --------------------------------------------------
# Part 1: Generate channels from source
# --------------------------------------------------

response = requests.get(URL, timeout=30)

if response.status_code != 200:
    raise Exception(f"Failed to fetch content. HTTP Status: {response.status_code}")

content = response.text

lines = [line.strip() for line in content.splitlines() if line.strip()]

titles = []
links = []

for i, line in enumerate(lines):
    if i % 2 == 0:
        titles.append(line)
    else:
        links.append(line)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

    f.write("#EXTM3U\n")

    tvg_id = 1

    for i in range(4, min(len(titles), len(links))):

        original_link = links[i]
        parts = original_link.split("|")

        mpd_url = parts[0].strip()
        license_key = ""

        if len(parts) > 1:
            match = re.search(r"drmLicense=([^&]+)", parts[1])
            if match:
                license_key = match.group(1).strip()

        f.write(
            f'#EXTINF:-1 tvg-id="{tvg_id}" group-title="Cricket" tvg-logo="", {titles[i]}\n'
        )
        f.write("#KODIPROP:inputstream.adaptive.license_type=clearkey\n")
        f.write(f"#KODIPROP:inputstream.adaptive.license_key={license_key}\n")
        f.write(f"{mpd_url}\n\n")

        tvg_id += 1

# --------------------------------------------------
# Part 2: Append channels from URL
# Format:
# Channel Name
# Stream URL
# --------------------------------------------------

try:
    response = requests.get(TEXT_FILE_URL, timeout=30)

    if response.status_code == 200:

        lines = [
            line.strip()
            for line in response.text.splitlines()
            if line.strip()
        ]

        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:

            for i in range(0, len(lines) - 1, 2):

                channel_name = lines[i]
                stream_url = lines[i + 1]

                f.write(
                    f'#EXTINF:-1 tvg-id="Cricket" tvg-logo="" group-title="Cricket" group-logo="", {channel_name}\n'
                )
                f.write(f"{stream_url}\n\n")

    else:
        print(
            f"Failed to fetch channel list. HTTP Status: {response.status_code}"
        )

except Exception as e:
    print(f"Error fetching channel list: {e}")

print(f"Playlist written to {OUTPUT_FILE}")


# MIX MERGED

# ===============================
# PLAYLIST LINKS
# ===============================

playlist_links = {
    "Link 8": os.environ["Rkd_Xtream_PLYLST_URL"],
    "Link 9": os.environ["Rkd_Mac_PLYLST_URL"]
}

# ===============================
# OUTPUT FILE
# ===============================

output_file = OUTPUT_FILE

# ===============================
# RULES FILE
# Format:
# Channel Name : Link to Search : Group to Search : New Group
# ===============================

rules_file = "allowed_channels.txt"

# ===============================
# FETCH PLAYLIST
# ===============================

def fetch_playlist(url):
    headers = {
        "User-Agent": "Mozilla/5.0 IPTV Parser"
    }
    r = requests.get(url, headers=headers, timeout=30)
    return r.text if r.status_code == 200 else ""

# ===============================
# SPLIT EXTINF BLOCKS
# ===============================

def split_blocks(content):
    return re.split(r'(?=#EXTINF)', content)

# ===============================
# START OUTPUT FILE
# ===============================

# ===============================
# LOAD RULES
# ===============================

with open(rules_file, "r", encoding="utf-8") as f:
    rules = [line.strip() for line in f if line.strip()]

# ===============================
# PROCESS
# ===============================
for link_name, url in playlist_links.items():

    playlist = fetch_playlist(url)
    if not playlist:
        continue

    blocks = split_blocks(playlist)

    for block in blocks:

        lines = block.strip().split("\n")
        if not lines:
            continue

        extinf_line = lines[0]
        if not extinf_line.startswith("#EXTINF"):
            continue

        # Extract channel name
        channel_name = extinf_line.split(",")[-1].strip().lower()
        channel_name = re.sub(r"\s+", " ", channel_name)

        # Extract group title
        group_title = ""
        match = re.search(r'group-title="([^"]+)"', extinf_line, re.IGNORECASE)
        if match:
            group_title = match.group(1).strip().lower()
            group_title = re.sub(r"\s+", " ", group_title)

        for rule in rules:

            parts = rule.split(":", 3)
            if len(parts) < 4:
                continue

            rule_channel = re.sub(r"\s+", " ", parts[0].strip().lower())
            rule_link = parts[1].strip()
            rule_search = re.sub(r"\s+", " ", parts[2].strip().lower())
            rule_replace = parts[3].strip()

            # Skip if rule belongs to another playlist
            if rule_link != link_name:
                continue

            if (
                (rule_channel in channel_name or channel_name in rule_channel)
                and
                rule_search in group_title
            ):

                new_extinf = re.sub(
                    r'group-title="[^"]*"',
                    f'group-title="{rule_replace}"',
                    extinf_line,
                    flags=re.IGNORECASE
                )

                # Add tvg-id only if missing
                if not re.search(r'tvg-id="[^"]*"', new_extinf, re.IGNORECASE):
                    new_extinf = new_extinf.replace(
                        "#EXTINF:-1",
                        f'#EXTINF:-1 tvg-id="{tvg_id}"',
                        1
                    )
                    tvg_id += 1
                    
                block = block.replace(extinf_line, new_extinf)

                with open(output_file, "a", encoding="utf-8") as f:
                    f.write(block.strip() + "\n\n")

                break

print(f"Playlist written to {output_file}")
