
import os
import re
import sys
import urllib.request
from pathlib import Path


# ============================================================
# CONFIGURATION: REPLACE THESE SAMPLE CHANNEL NAMES
#
# Format:
# Playlist number, Channel Name
#
# 1 = Search in PLAYLIST_URL_1 only
# 2 = Search in PLAYLIST_URL_2 only
#
# ALL MATCHED CHANNELS WILL HAVE group-title="News 1"
# ============================================================

CHANNEL_LIST = """
1, News9Live
1, Mirror Now
2, Zee 24 Taas
2, Republic TV
2, Republic Bharat
2, India Today


# All channels will be assigned to this group.
GROUP_TITLE = "News 1"

# Output playlist file.
OUTPUT_FILE = "matched_channels.m3u"


# ============================================================
# FETCH PLAYLIST
# ============================================================

def fetch_playlist(url):
    """Download an M3U playlist and return its lines."""

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        content = response.read().decode(
            "utf-8-sig",
            errors="replace"
        )

    return content.splitlines()


# ============================================================
# NORMALIZE CHANNEL NAMES
# ============================================================

def normalize(text):
    """Normalize names for case-insensitive matching."""

    return re.sub(r"\s+", " ", text).strip().casefold()


# ============================================================
# EXTRACT STREAM URL
# ============================================================

def extract_url(line):
    """Extract a URL from a playlist line."""

    line = line.strip()

    # Handle Markdown-formatted links if present.
    match = re.match(
        r"^\[(https?://[^\]]+)\]\((https?://.*)\)$",
        line
    )

    if match:
        return match.group(1).strip()

    return line


# ============================================================
# EXTRACT CHANNEL NAMES FROM EXTINF
# ============================================================

def get_channel_names(extinf):
    """
    Extract tvg-name and display name from an EXTINF line.

    For example:
    tvg-name="News9Live",188 News9Live

    Recognizes:
    News9Live
    188 News9Live
    """

    names = set()

    # Extract tvg-name.
    tvg_match = re.search(
        r'\btvg-name="([^"]*)"',
        extinf
    )

    if tvg_match:
        names.add(normalize(tvg_match.group(1)))

    # Find the first comma outside quotation marks.
    quoted = False
    comma_index = -1

    for index, char in enumerate(extinf):
        if char == '"':
            quoted = not quoted

        elif char == "," and not quoted:
            comma_index = index
            break

    if comma_index >= 0:
        display_name = extinf[comma_index + 1:].strip()

        names.add(normalize(display_name))

        # Also recognize display names prefixed by a channel number.
        display_without_number = re.sub(
            r"^\d+\s+",
            "",
            display_name
        ).strip()

        names.add(normalize(display_without_number))

    return names


# ============================================================
# UPDATE GROUP TITLE
# ============================================================

def update_group_title(extinf):
    """
    Set group-title="News 1" for every matched channel.

    Replace an existing group-title if present.
    Otherwise, add it before the display-name comma.
    """

    if re.search(r'\bgroup-title="[^"]*"', extinf):
        return re.sub(
            r'\bgroup-title="[^"]*"',
            f'group-title="{GROUP_TITLE}"',
            extinf,
            count=1
        )

    quoted = False

    for index, char in enumerate(extinf):
        if char == '"':
            quoted = not quoted

        elif char == "," and not quoted:
            return (
                extinf[:index]
                + f' group-title="{GROUP_TITLE}"'
                + extinf[index:]
            )

    # Return unchanged if no display-name comma exists.
    return extinf


# ============================================================
# PARSE M3U PLAYLIST
# ============================================================

def parse_playlist(lines):
    """
    Extract pairs of:
    (#EXTINF line, stream URL)

    Preserve the original channel metadata and stream URL.
    """

    entries = []
    index = 0

    while index < len(lines):
        line = lines[index].strip()

        if not line.startswith("#EXTINF:"):
            index += 1
            continue

        extinf = line
        index += 1

        # Find the stream URL following this EXTINF line.
        while index < len(lines):
            candidate = lines[index].strip()
            index += 1

            if not candidate or candidate.startswith("#"):
                continue

            stream_url = extract_url(candidate)

            if stream_url.startswith(("http://", "https://")):
                entries.append((extinf, stream_url))

            break

    return entries


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    # Playlist URLs are stored in GitHub Secrets.
    playlist_urls = {
        1: os.environ.get("PLAYLIST_URL_1", "").strip(),
        2: os.environ.get("PLAYLIST_URL_2", "").strip(),
    }

    # Validate both secrets.
    for playlist_number, url in playlist_urls.items():
        if not url:
            sys.exit(
                f"Error: PLAYLIST_URL_{playlist_number} "
                "GitHub Secret is missing or empty."
            )

    # Parse the channel list embedded in this Python file.
    requested = {
        1: set(),
        2: set(),
    }

    for line_number, line in enumerate(
        CHANNEL_LIST.strip().splitlines(),
        start=1
    ):

        line = line.strip()

        if not line or line.startswith("#"):
            continue

        try:
            playlist_number, channel_name = line.split(",", 1)

            playlist_number = int(playlist_number.strip())
            channel_name = normalize(channel_name)

        except ValueError:
            sys.exit(
                f"Invalid CHANNEL_LIST entry on line "
                f"{line_number}: {line}"
            )

        if playlist_number not in playlist_urls:
            sys.exit(
                f"Invalid playlist number on line {line_number}. "
                "Use 1 or 2."
            )

        if not channel_name:
            sys.exit(
                f"Missing channel name on line {line_number}."
            )

        requested[playlist_number].add(channel_name)

    # Fetch and search each assigned playlist.
    matches = []
    missing = []

    for playlist_number, url in playlist_urls.items():

        channel_names = requested[playlist_number]

        if not channel_names:
            print(
                f"Playlist {playlist_number}: "
                "No channels requested. Skipping."
            )
            continue

        print(f"Fetching playlist {playlist_number}...")

        try:
            lines = fetch_playlist(url)
            entries = parse_playlist(lines)

        except Exception as error:
            sys.exit(
                f"Failed to fetch playlist {playlist_number}: "
                f"{type(error).__name__}: {error}"
            )

        print(
            f"Playlist {playlist_number}: "
            f"{len(entries)} entries loaded."
        )

        found = set()

        for extinf, stream_url in entries:

            available_names = get_channel_names(extinf)

            matched_names = channel_names.intersection(
                available_names
            )

            if matched_names:
                # Every matched channel gets the same group title.
                updated_extinf = update_group_title(extinf)

                matches.append((updated_extinf, stream_url))
                found.update(matched_names)

        # Record channels that were not found.
        for name in sorted(channel_names - found):
            missing.append((playlist_number, name))

    # Generate the output M3U file.
    output_lines = ["#EXTM3U"]

    for extinf, stream_url in matches:
        output_lines.append(extinf)
        output_lines.append(stream_url)

    Path(OUTPUT_FILE).write_text(
        "\n".join(output_lines) + "\n",
        encoding="utf-8"
    )

    # Display the result summary.
    print()
    print("========== RESULTS ==========")
    print(f"Matched channel entries: {len(matches)}")
    print(f"Group title: {GROUP_TITLE}")
    print(f"Output file: {OUTPUT_FILE}")

    if missing:
        print()
        print("Channels not found:")

        for playlist_number, name in missing:
            print(f"- Playlist {playlist_number}: {name}")

    else:
        print("All requested channels were found.")

    print("=============================")


if __name__ == "__main__":
    main()
