import requests
import json
import random

OUTPUT_FILE = "featured.json"

# Using "Hot" instead of "Top" ensures there is always fresh content
SOURCES = [
    "https://www.reddit.com/r/LivelyWallpaper/hot.json?limit=10",
    "https://www.reddit.com/r/LiveAnimeWallpapers/hot.json?limit=10"
]

def scrape():
    final_list = []
    seen_ids = set()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GitHubAction/1.0"
    }

    print("--- 🚀 STARTING SCRAPE ---")

    for url in SOURCES:
        try:
            print(f"🌍 Visiting: {url}")
            resp = requests.get(url, headers=headers)
            data = resp.json()
            posts = data.get('data', {}).get('children', [])
            
            print(f"   found {len(posts)} posts...")

            for post in posts:
                p = post['data']
                
                # 1. MUST be a video
                if not p.get('is_video'):
                    continue
                
                # 2. Get the video URL
                try:
                    video_url = p['media']['reddit_video']['fallback_url'].split('?')[0]
                except:
                    continue

                # 3. Get Thumbnail (Fallback logic)
                thumb = p.get('thumbnail', '')
                if not thumb.startswith('http'):
                    # Try to get preview image if thumbnail is invalid
                    try:
                        thumb = p['preview']['images'][0]['source']['url'].replace('&amp;', '&')
                    except:
                        thumb = "https://www.redditstatic.com/icon.png" # Fallback icon

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

    # FORCE SAVE (Even if list is small)
    if final_list:
        random.shuffle(final_list)
        # Always take top 10
        output_data = final_list[:10]
        
        with open(OUTPUT_FILE, "w") as f:
            json.dump(output_data, f, indent=2)
        
        print(f"✅ SUCCESS: Dumped {len(output_data)} items to {OUTPUT_FILE}")
    else:
        print("⚠️ WARNING: No items found. Reddit might be blocking IP.")

if __name__ == "__main__":
    scrape()
