import requests
import json
import time
import random

# --- CONFIG ---
OUTPUT_FILE = "featured.json"
SUBREDDITS = ["animegifs", "Cinemagraphs", "Outrun", "Cyberpunk", "Rain", "CityPorn"]

# --- BACKUP LIST (Used if Reddit blocks us) ---
# These links are reliable static video files.
BACKUP_VIDEOS = [
    {
        "id": "backup_1",
        "title": "Cyberpunk Rainy City",
        "subreddit": "backup",
        "thumbnail": "https://images.wallpapersden.com/image/download/cyberpunk-city-art_bGZraWaUmZqaraWkpJRmbmdlrWZlbWU.jpg",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
        "permalink": "https://github.com"
    },
    {
        "id": "backup_2",
        "title": "Big Buck Bunny (Nature Test)",
        "subreddit": "backup",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Big_buck_bunny_poster_big.jpg/800px-Big_buck_bunny_poster_big.jpg",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "permalink": "https://github.com"
    },
    {
        "id": "backup_3",
        "title": "Sintel (Fantasy/Action)",
        "subreddit": "backup",
        "thumbnail": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Sintel_poster.jpg/800px-Sintel_poster.jpg",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
        "permalink": "https://github.com"
    }
]

# Browser Identity
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}

def get_video_url(data):
    url = data.get("url", "")
    if url.endswith(".mp4") or url.endswith(".webm"): return url
    if url.endswith(".gifv"): return url.replace(".gifv", ".mp4")
    if data.get("is_video") and data.get("media"): return data["media"]["reddit_video"]["fallback_url"]
    try: return data["preview"]["reddit_video_preview"]["fallback_url"]
    except: return None

def scrape():
    final_list = []
    seen_ids = set()

    print("--- STARTING SCRAPE ---")

    for sub in SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/top.json?t=week&limit=10"
        try:
            print(f"Checking r/{sub}...")
            resp = requests.get(url, headers=HEADERS, timeout=10)
            
            if resp.status_code != 200:
                print(f"❌ Blocked: {resp.status_code}")
                continue

            posts = resp.json().get("data", {}).get("children", [])
            for post in posts:
                d = post["data"]
                vid = get_video_url(d)
                
                # Get thumbnail safely
                thumb = d.get("thumbnail", "")
                if not thumb.startswith("http"):
                    try: thumb = d["preview"]["images"][0]["source"]["url"].replace("&amp;", "&")
                    except: thumb = ""

                if vid and thumb and d["id"] not in seen_ids:
                    final_list.append({
                        "id": d["id"],
                        "title": d["title"],
                        "subreddit": sub,
                        "thumbnail": thumb,
                        "video_url": vid,
                        "permalink": f"https://reddit.com{d['permalink']}"
                    })
                    seen_ids.add(d["id"])
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ Error: {e}")

    # --- DECISION TIME ---
    if len(final_list) > 0:
        print(f"✅ SUCCESS: Found {len(final_list)} videos from Reddit.")
        save_json(final_list)
    else:
        print("⚠️ WARNING: Reddit scrape failed (0 videos). Using BACKUP list.")
        save_json(BACKUP_VIDEOS)

def save_json(data):
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print("💾 File saved.")

if __name__ == "__main__":
    scrape()
