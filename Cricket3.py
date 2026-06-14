import requests

url = "https://la.drmlive.net/tp/playlist"

headers = {
    "User-Agent": "OTT Navigator"
}

r = requests.get(url, headers=headers, timeout=30)

with open("8b249zhj3vg65us_sports1.m3u", "w", encoding="utf-8") as f:
    f.write(f"Status: {r.status_code}\n")
    f.write(f"Content-Type: {r.headers.get('Content-Type')}\n")
    f.write(f"Final URL: {r.url}\n\n")
    f.write(r.text)

print("Saved to ott_response.txt")
