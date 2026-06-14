import subprocess

m3u_url = "https://la.drmlive.net/tp/playlist"

output_file = "8b249zhj3vg65us_sports.m3u"

result = subprocess.run(
    ["curl", "-L", "-s", m3u_url],
    capture_output=True,
    text=True,
    check=True
)

with open(output_file, "w", encoding="utf-8") as f:
    f.write(result.stdout)

print(f"Saved M3U to {output_file}")
