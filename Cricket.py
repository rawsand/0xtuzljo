import subprocess

m3u_url = "https://la.drmlive.net/tp/playlist"

output_file = "8b249zhj3vg65us_sports.m3u"

result = subprocess.run(
    ["curl", "-L", "-I", "https://la.drmlive.net/tp/playlist"],
    capture_output=True,
    text=True
)

with open(output_file, "w", encoding="utf-8") as f:
    f.write(result.stdout)

print(f"Saved M3U to {output_file}")
