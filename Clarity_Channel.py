import re
import requests

# ===============================
# PLAYLIST LINKS
# ===============================

playlist_links = {
    "Link 1": "https://clarity-tv.vercel.app/api/playlist/?id=ALLINONE"
}

# ===============================
# OUTPUT FILE
# ===============================

output_file = "8b249zhj3vg65us_so.m3u"

# ===============================
# RULES
# Format: Channel : Search Group : Replace Group
# ===============================

rules = [
    "SET HD SonyLiv : SonyLiv | Entertainment : JioTV+ | Entertainment"
]

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

open(output_file, "w", encoding="utf-8").close()

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

            parts = rule.split(":", 2)
            if len(parts) < 3:
                continue

            rule_channel = re.sub(r"\s+", " ", parts[0].strip().lower())
            rule_search = re.sub(r"\s+", " ", parts[1].strip().lower())
            rule_replace = parts[2].strip()

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

                block = block.replace(extinf_line, new_extinf)

                with open(output_file, "a", encoding="utf-8") as f:
                    f.write(block.strip() + "\n\n")

                break

print(f"Playlist written to {output_file}")
