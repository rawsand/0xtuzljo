import re
import requests

# URL where the channels text file is located
URL = "https://raw.githubusercontent.com/rawsand/telegram-github-bot/refs/heads/main/links.txt"

# URL containing channel-name / stream-url pairs
TEXT_FILE_URL = https://raw.githubusercontent.com/rawsand/0xtuzljo/refs/heads/main/channels.txt"

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
