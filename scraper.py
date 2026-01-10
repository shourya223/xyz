import requests
import json
import random
import time

OUTPUT_FILE = "featured.json"

# We check multiple sources. 
# "t=all" means we look at Top posts of all time (Highest Quality), not new memes.
SOURCES = [
    "https://www.reddit.com/r/LivelyWallpaper/search.json?q=flair:Anime&restrict_sr=1&sort=top&t=all&limit=100",
    "https://www.reddit.com/r/LiveAnimeWallpapers/top.json?t=all&limit=50"
]

def scrape():
    final_list = []
    seen_ids = set()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) WallpaperBot/2.0"
    }

    print("--- 🚀 STARTING MEME-PROOF SCRAPE ---")

    for url in SOURCES:
        print(f"🌍 Mining: {url.split('/r/')[1].split('/')[0]}...")
        
        try:
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                print(f"   ❌ Failed: {resp.status_code}")
                continue

            data = resp.json()
            posts = data.get('data', {}).get('children', [])

            for post in posts:
                p = post['data']

                # --- FILTERS (The Anti-Meme Logic) ---
                
                # 1. Must be a Reddit-hosted video
                if not p.get('is_video'):
                    continue
                
                # 2. Skip NSFW if you want clean wallpapers
                if p.get('over_18'):
                    continue

                # 3. Must be high resolution (720p+)
                # We check the width/height if available
                w = p.get('media', {}).get('reddit_video', {}).get('width', 0)
                if w < 1080: # Force 1080p or higher quality
                    continue

                # 4. Filter out common meme titles if necessary
                title = p['title'].lower()
                if "meme" in title or "discussion" in title or "help" in title:
                    continue

                try:
                    # Get the clean MP4 url
                    video_url = p['media']['reddit_video']['fallback_url']
                    video_url = video_url.split('?')[0] # Remove query params

                    # Get thumbnail
                    thumb_url = p['thumbnail']
                    if not thumb_url.startswith("http"):
                        # Fallback to preview image if thumbnail is "default"
                        try:
                            thumb_url = p['preview']['images'][0]['source']['url'].replace('&amp;', '&')
                        except:
                            continue

                    # Unique ID check
                    if p['id'] not in seen_ids:
                        final_list.append({
                            "id": p['id'],
                            "title": p['title'],
                            "subreddit": p['subreddit_name_prefixed'],
                            "thumbnail": thumb_url,
                            "video_url": video_url,
                            "permalink": f"https://reddit.com{p['permalink']}"
                        })
                        seen_ids.add(p['id'])

                except Exception as e:
                    continue
        
        except Exception as e:
            print(f"   ⚠️ Source failed: {e}")

    # Final Randomization
    if final_list:
        # Pick 10 random ones from the top quality list so it rotates
        random.shuffle(final_list)
        final_output = final_list[:20] 
        
        with open(OUTPUT_FILE, "w") as f:
            json.dump(final_output, f, indent=2)
        print(f"💾 SAVED {len(final_output)} HIGH-QUALITY WALLPAPERS.")
    else:
        print("❌ No valid wallpapers found. (Check filters)")

if __name__ == "__main__":
    scrape()
