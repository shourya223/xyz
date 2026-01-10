import requests
import json
import time
import random

# Reliable subreddits for wallpaper-style content
SUBREDDITS = ["animegifs", "Cinemagraphs", "Outrun", "Cyberpunk", "Rain", "CityPorn"]
OUTPUT_FILE = "featured.json"

# A list of fake "Real Browser" identities to fool Reddit
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
]

def get_video_url(data):
    # 1. Direct MP4/WebM
    url = data.get("url", "")
    if url.endswith(".mp4") or url.endswith(".webm"):
        return url
    if url.endswith(".gifv"):
        return url.replace(".gifv", ".mp4")
        
    # 2. Reddit Native Video
    if data.get("is_video") and data.get("media"):
        return data["media"]["reddit_video"]["fallback_url"]
        
    # 3. Preview Video (Common for gifs)
    try:
        return data["preview"]["reddit_video_preview"]["fallback_url"]
    except:
        pass
        
    return None

def scrape():
    final_list = []
    seen_ids = set()

    print("--- STARTING STEALTH SCRAPE ---")

    for sub in SUBREDDITS:
        # Use 'top' of the week to ensure high quality and valid links
        url = f"https://www.reddit.com/r/{sub}/top.json?t=week&limit=15"
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        
        try:
            print(f"🕵️‍♂️ Checking r/{sub}...")
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code != 200:
                print(f"❌ Blocked/Error {resp.status_code} on {sub}")
                continue
                
            posts = resp.json().get("data", {}).get("children", [])
            
            found_count = 0
            for post in posts:
                d = post["data"]
                
                # Must be video-like
                vid_url = get_video_url(d)
                
                # Must have thumbnail
                thumb = d.get("thumbnail", "")
                if not thumb.startswith("http"):
                    try:
                        thumb = d["preview"]["images"][0]["source"]["url"].replace("&amp;", "&")
                    except:
                        continue 

                if vid_url and d["id"] not in seen_ids:
                    final_list.append({
                        "id": d["id"],
                        "title": d["title"],
                        "subreddit": sub,
                        "thumbnail": thumb,
                        "video_url": vid_url,
                        "permalink": f"https://reddit.com{d['permalink']}"
                    })
                    seen_ids.add(d["id"])
                    found_count += 1
            
            print(f"   ✅ Added {found_count} videos")
            time.sleep(3) # Wait 3 seconds between requests to look human
            
        except Exception as e:
            print(f"   ⚠️ Exception: {e}")

    print(f"--- SCRAPE FINISHED. Total: {len(final_list)} ---")
    
    # SAFETY CHECK: If we found nothing, DON'T overwrite the manual file!
    if len(final_list) > 0:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(final_list, f, indent=2)
        print("💾 featured.json updated successfully.")
    else:
        print("⚠️ No videos found. Keeping old file to prevent blank screen.")

if __name__ == "__main__":
    scrape()
