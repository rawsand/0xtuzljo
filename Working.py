import os
import sys
import requests
import re


def fetch_m3u_blocks_from_url(url):
    """Fetch playlist from URL and split into blocks (#EXTINF ...)."""
    response = requests.get(url)
    response.raise_for_status()
    lines = [line.strip() for line in response.text.splitlines() if line.strip()]
    return split_into_blocks(lines)


def fetch_m3u_blocks_from_file(file_path):
    """Read playlist from local file and split into blocks (#EXTINF ...)."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.read()
    return lines


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


def filter_m3u_blocks(
    urls,
    channel_names,
    exclude_channels,
    output_dir="output_blocks",
    output_file="fiaylist.m3u",
):
    all_blocks = []
    blocks_from_Github = ""

    # Fetch from URLs
    for url in urls:
        print(f"Fetching playlist from URL: {url}")
        all_blocks.extend(fetch_m3u_blocks_from_url(url))

    # Fetch from local file (hardcoded path)
    local_file = "8ive.m3u"  # 👈 change if needed
    if os.path.exists(local_file):
        print(f"Reading playlist from local file: {local_file}")
        # Note: fetch_m3u_blocks_from_file currently returns raw text, not a list of blocks
        # You may need to use split_into_blocks() on this result if you want it handled the same way
        blocks_from_Github = fetch_m3u_blocks_from_file(local_file)

    # Filter with include/exclude rules
    matched_blocks, seen_channels = [], set()
    for block in all_blocks:
        extinf_line = block.splitlines()[0]
        channel_name = extinf_line.split(",")[-1].strip()

        include_match = any(
            name.lower() in channel_name.lower() for name in channel_names
        )
        exclude_match = any(
            bad.lower() in channel_name.lower() for bad in exclude_channels
        )

        if include_match and not exclude_match:
            # if channel_name.lower() not in seen_channels:
            matched_blocks.append(block)
            seen_channels.add(channel_name.lower())
        # else:
        # print(f"Skipping duplicate: {channel_name}")
        elif exclude_match:
            print(f"Excluded unwanted channel: {channel_name}")

    # Find and replace text
    pattern = r'group-title=".*?"'
    replacement = r'group-title="General"'
    blocks_from_Github = re.sub(pattern, replacement, blocks_from_Github)
    for block in matched_blocks:
        blocks_from_Github = (
            blocks_from_Github + re.sub(pattern, replacement, block) + "\n\n"
        )

    # --- Duplicate Link Removal Logic (Corrected and applied to combined blocks) ---
    seen_links = set()
    unique_blocks_final = []

    # Regex pattern to capture the URL/link which is typically the second line of the block
    link_pattern = re.compile(r"^(http|https|ftp)://.*", re.IGNORECASE)

    # We now iterate over the `blocks_from_Github` string we built above
    # which contains all the filtered and modified blocks combined.
    lines = blocks_from_Github.strip().splitlines()
    i = 0
    while i < len(lines):
        current_line = lines[i].strip()

        # We only care about lines starting with #EXTINF (the metadata line)
        if current_line.startswith("#EXTINF"):
            # The link should be on the *next* line
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()

                # Check if the next line matches our link pattern
                if link_pattern.match(next_line):
                    potential_link = next_line

                    if potential_link not in seen_links:
                        # Link is unique! Add it to our set and store the block
                        seen_links.add(potential_link)
                        # Store the full block (metadata line + link line)
                        unique_blocks_final.append(
                            f"{current_line}\n{potential_link}\n\n"
                        )  # Added extra newline for spacing in final file
                    else:
                        # Link is a duplicate. Ignore this block.
                        print(f"Ignoring duplicate link: {potential_link}")

                # In either case (unique or duplicate), we must skip the link line
                # in the main loop to avoid processing it incorrectly later.
                i += 1
        i += 1

    # --- End Duplicate Link Removal Logic ---

    # Ensure output folder exists and write the final unique blocks
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_file)
    with open(output_path, "w", encoding="utf-8") as out:
        out.write("#EXTM3U\n\n")
        # Write the list of unique blocks joined together
        out.write("".join(unique_blocks_final))

    print(f"Saved {len(unique_blocks_final)} unique matched blocks into: {output_path}")
    # The return value below might be misleading now; it returns the final list of strings
    return unique_blocks_final


if __name__ == "__main__":
    # URLs passed as arguments
    urls = [arg for arg in sys.argv[1:] if arg.startswith("http")]

    # ✅ Channels you want
    channel_names = [
		"Zee Marathi",
		"Star Plus",
		"Star Pravah",
		"Set HD",
		"Sony HD",
		"Shemaroo Marathibana",
		"Sony TV HD"		
	    ]

    # ❌ Channels you don’t want (blacklist)
    exclude_channels = [
		"Thrills"
	    ]

    filter_m3u_blocks(urls, channel_names, exclude_channels)
