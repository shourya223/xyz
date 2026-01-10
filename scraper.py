import requests
import json
import random
import os
import sys

OUTPUT_FILE = "featured.json"
API_KEY = os.environ.get("PEXELS_API_KEY")
MAX_ITEMS = 200  # <--- Cap the list at 200 items

# We will fetch A LOT of videos now
QUERIES = ["anime", "cyberpunk", "neon city", "sci-fi", "gaming", "fantasy landscape", "lofi"]

def scrape():
    if not API_KEY:
        print("❌ ERROR: PEXELS_API_KEY is missing.")
        sys.exit(1)

    headers = {"Authorization": API_KEY}
    new_items = []
    
    print("--- 🚀 STARTING BULK FETCH ---")

    for query in QUERIES:
        # Request 40 videos per category (40 * 7 categories = ~280 potential videos)
        url = f"https://api.pexels.com/videos/search?query={query}&per_page=40&orientation=landscape"
        
        try:
            print(f"🌍 Fetching up to 40 videos for: {query}...")
            resp = requests.get(url, headers=headers)
            
            if resp.status_code != 200:
                print(f"   ⚠️ Failed: {resp.status_code}")
                continue

            data = resp.json()
            videos = data.get('videos', [])
            print(f"   ✅ Received {len(videos)} videos.")

            for v in videos:
                # Find best MP4 quality
                best_link = None
                max_w = 0
                for f in v['video_files']:
                    if f['file_type'] == 'video/mp4' and f['width'] > max_w:
                        max_w = f['width']
                        best_link = f['link']

                if best_link:
                    new_items.append({
                        "id": str(v['id']),
                        "title": f"{query.title()} Wallpaper {v['id']}",
                        "subreddit": "Pexels",
                        "thumbnail": v['image'],
                        "video_url": best_link,
                        "permalink": v['url']
                    })

        except Exception as e:
            print(f"   ⚠️ Error: {e}")

    # --- MERGE WITH EXISTING ---
    existing_items = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r") as f:
                existing_items = json.load(f)
        except:
            existing_items = []

    # Use a dictionary to remove duplicates by ID
    combined = {}
    for item in existing_items:
        combined[item['id']] = item
    for item in new_items:
        combined[item['id']] = item

    final_list = list(combined.values())
    
    # Shuffle and Clip
    random.shuffle(final_list)
    if len(final_list) > MAX_ITEMS:
        final_list = final_list[:MAX_ITEMS]

    # FORCE SAVE
    with open(OUTPUT_FILE, "w") as f:
        json.dump(final_list, f, indent=2)
    
    print("---------------------------------------------------")
    print(f"🎉 FINAL COUNT: {len(final_list)} WALLPAPERS SAVED.")
    print("---------------------------------------------------")

if __name__ == "__main__":
    scrape()
