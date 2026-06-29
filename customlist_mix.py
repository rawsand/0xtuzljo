import os
import re
import requests

# ===============================
# PLAYLIST LINKS
# ===============================

playlist_links = {
    "Link 1": os.environ["EXTDERM_PLYLST_URL"],
    "Link 2": os.environ["CLR_PLYLST_URL"],
    "Link 3": os.environ["VaTh_PLYLST_URL"]
}

# ===============================
# OUTPUT FILE
# ===============================

output_file = "8b249zhj3vg65us_mix.m3u"

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

with open(output_file, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")

# ===============================
# LOAD RULES
# ===============================

with open(rules_file, "r", encoding="utf-8") as f:
    rules = [line.strip() for line in f if line.strip()]

# ===============================
# PROCESS
# ===============================
tvg_id = 1
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
                channel_name == rule_channel and
                rule_search in group_title
            ):

                new_extinf = re.sub(
                    r'group-title="[^"]*"',
                    f'group-title="{rule_replace}"',
                    extinf_line,
                    flags=re.IGNORECASE
                )

                # Add/replace tvg-id
                if re.search(r'tvg-id="[^"]*"', new_extinf, re.IGNORECASE):
                    new_extinf = re.sub(
                        r'tvg-id="[^"]*"',
                        f'tvg-id="{tvg_id}"',
                        new_extinf,
                        flags=re.IGNORECASE
                    )
                else:
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
