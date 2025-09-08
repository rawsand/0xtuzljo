import requests

def create_m3u_from_url(url, output_filename="playlist.m3u"):
    """
    Reads content from a given URL and creates an M3U playlist file.

    Args:
        url (str): The URL of the file containing media paths or URLs.
        output_filename (str, optional): The name of the M3U file to create.
                                         Defaults to "playlist.m3u".
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        content = response.text

        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")  # M3U header
            f.write(content)

        print(f"M3U file '{output_filename}' created successfully from {url}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching content from URL: {e}")
    except IOError as e:
        print(f"Error writing to file: {e}")

# Example usage:
# Replace 'your_url_here' with the actual URL of your source file.
# This URL should ideally point to a plain text file where each line
# is a path or URL to a media file.
source_url = "https://github.com/rawsand/0xtuzljoN/raw/refs/heads/main/output_blocks/filtered_playlist_final.m3u"
create_m3u_from_url(source_url, "my_media_playlist.m3u")