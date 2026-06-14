import re
import requests
import subprocess

# URL where the text file is located
URL = "https://raw.githubusercontent.com/rawsand/telegram-github-bot/refs/heads/main/links.txt"  # Change this
m3u_url = "https://la.drmlive.net/tp/playlist"

# Output file
OUTPUT_FILE = "8b249zhj3vg65us_sports.m3u"

# Fetch content from URL
response = requests.get(URL, timeout=30)

if response.status_code != 200:
    raise Exception(f"Failed to fetch content. HTTP Status: {response.status_code}")

content = response.text

# Convert content into lines
lines = [line.strip() for line in content.splitlines() if line.strip()]

# Separate titles and links
titles = []
links = []

for i, line in enumerate(lines):
    if i % 2 == 0:
        titles.append(line)
    else:
        links.append(line)

# Write main output file
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
            f'#EXTINF:-1 tvg-id="{tvg_id}" group-title="JioTV+ | Sports" tvg-logo="", {titles[i]}\n'
        )

        f.write("#KODIPROP:inputstream.adaptive.license_type=clearkey\n")
        f.write(f"#KODIPROP:inputstream.adaptive.license_key={license_key}\n")
        f.write(f"{mpd_url}\n\n")

        tvg_id += 1

print(f"Playlist written to {OUTPUT_FILE}")

# Fetch M3U using curl
result = subprocess.run(
    ["curl", "-L", "-s", "-A", "OTT Navigator", m3u_url],
    capture_output=True,
    text=True,
    check=True
)

content = result.stdout
lines = content.splitlines()

with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
    i = 0

    while i < len(lines):

        line = lines[i]

        if line.startswith("#EXTINF") and 'group-title="Cricket"' in line:

            j = i + 1
            metadata = []

            while j < len(lines) and lines[j].startswith("#"):
                metadata.append(lines[j])
                j += 1

            if j < len(lines):
                stream_url = lines[j]
            else:
                break

            f.write("#KODIPROP:inputstream.adaptive.license_type=clearkey\n")

            for m in metadata:
                f.write(m + "\n")

            f.write(line + "\n")
            f.write(stream_url + "\n\n")

            i = j

        i += 1
