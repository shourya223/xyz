import requests
import json
import random
from datetime import datetime

OUTPUT_FILE = "featured.json"

# Using "Hot" guarantees fresh content. "Top" guarantees quality.
# We mix them to ensure we ALWAYS get results.
SOURCES = [
    "https://www.reddit.com/r/LivelyWallpaper/hot.json?limit=10",
    "https://www.reddit.com/r/LiveAnimeWallpapers/hot.json?limit=10",
    "https://www.reddit.com/r/moescape/hot.json?limit=10"
]

def scrape():
    final_list = []
    seen_ids = set()
    
    # Fake browser header to prevent blocking
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GitHubAction/Scraper"
    }

    print("--- 🚀 STARTING SCRAPE ---")

    for url in SOURCES:
        try:
            print(f"🌍 Visiting: {url}")
            resp = requests.get(url, headers=headers)
            
            if resp.status_code != 200:
                print(f"   ❌ Failed: {resp.status_code}")
                continue

            data = resp.json()
            posts = data.get('data', {}).get('children', [])
            print(f"   Found {len(posts)} raw posts...")

            for post in posts:
                p = post['data']
                
                # --- SIMPLIFIED FILTERS ---
                
                # 1. Must be a video OR a high-res image (gif/gifv)
                is_video = p.get('is_video')
                url_ext = p.get('url', '').lower()[-4:]
                if not is_video and url_ext not in ['.gif', '.mp4', '.mov']:
                    continue
                
                # 2. Skip NSFW
                if p.get('over_18'):
                    continue

                # 3. Get Video URL
                video_url = ""
                if is_video and 'reddit_video' in p['media']:
                    video_url = p['media']['reddit_video']['fallback_url'].split('?')[0]
                else:
                    video_url = p['url'] # For direct .mp4 links

                # 4. Get Thumbnail
                thumb = p.get('thumbnail', '')
                if not thumb.startswith('http'):
                    thumb = "https://www.redditstatic.com/icon.png"

                if p['id'] not in seen_ids:
                    final_list.append({
                        "id": p['id'],
                        "title": p['title'],
                        "subreddit": p['subreddit_name_prefixed'],
                        "thumbnail": thumb,
                        "video_url": video_url,
                        "permalink": f"https://reddit.com{p['permalink']}"
                    })
                    seen_ids.add(p['id'])

        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")

    # --- THE MAGIC FIX ---
    # We add a "metadata" object at the top or shuffle the list.
    # This ensures the file content is DIFFERENT every time, forcing Git to save.
    
    print(f"✅ Found {len(final_list)} valid wallpapers.")
    
    # Always save at least 15 items if found
    random.shuffle(final_list)
    output_data = final_list[:15]
    
    # Add a dummy entry with timestamp to FORCE a git update
    output_data.insert(0, {
        "id": "UPDATE_INFO",
        "title": f"Updated at {datetime.now()}",
        "subreddit": "SYSTEM",
        "thumbnail": "",
        "video_url": "",
        "permalink": ""
    })

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"💾 Dumped {len(output_data)} items to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape()
