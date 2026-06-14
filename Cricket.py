import requests

url = "https://la.drmlive.net/tp/playlist"

r = requests.get(url, timeout=30)

with open("8b249zhj3vg65us_sports.m3u", "w", encoding="utf-8") as f:
    f.write(f"Status: {r.status_code}\n")
    f.write(f"Content-Type: {r.headers.get('Content-Type')}\n")
    f.write(f"Content-Length: {len(r.text)}\n\n")
    f.write(r.text)

print("Output saved to response.txt")
