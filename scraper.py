import requests
import json
import random
import os
import sys

OUTPUT_FILE = "featured.json"
API_KEY = os.environ.get("PEXELS_API_KEY")
MAX_ITEMS = 100  # <--- Change this to however many you want to keep total

QUERIES = ["anime", "cyberpunk", "neon", "space", "gaming", "lofi", "fantasy", "nature"]

def scrape():
    if not API_KEY:
        print("❌ ERROR: PEXELS_API_KEY is missing.")
        sys.exit(1)

    headers = {"Authorization": API_KEY}
    new_items = []
    
    print("--- 🚀 STARTING PEXELS SCRAPE ---")

    # 1. Fetch New Wallpapers
    for query in QUERIES:
        # Randomize page so we don't always get the same first 5 results
        page = random.randint(1, 10) 
        url = f"https://api.pexels.com/videos/search?query={query}&per_page=5&page={page}&orientation=landscape"
        
        try:
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200: continue

            data = resp.json()
            for v in data.get('videos', []):
                # Find best MP4
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

        except Exception:
            continue

    print(f"   ✨ Found {len(new_items)} new wallpapers.")

    # 2. Load Existing Wallpapers
    existing_items = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r") as f:
                existing_items = json.load(f)
                print(f"   📂 Loaded {len(existing_items)} existing wallpapers.")
        except json.JSONDecodeError:
            existing_items = []

    # 3. Merge and Remove Duplicates
    # We use a dictionary keyed by ID to ensure uniqueness
    combined = {}
    
    # Add old items first
    for item in existing_items:
        combined[item['id']] = item
        
    # Add new items (overwriting old ones if they exist, or just adding)
    for item in new_items:
        combined[item['id']] = item

    # Convert back to list
    final_list = list(combined.values())

    # 4. Limit the Size (Keep list fresh but not infinite)
    # Shuffle to mix old and new, then cut to MAX_ITEMS
    random.shuffle(final_list)
    if len(final_list) > MAX_ITEMS:
        final_list = final_list[:MAX_ITEMS]

    # 5. Save
    with open(OUTPUT_FILE, "w") as f:
        json.dump(final_list, f, indent=2)
    
    print(f"💾 SUCCESSFULLY SAVED {len(final_list)} TOTAL WALLPAPERS.")

if __name__ == "__main__":
    scrape()
