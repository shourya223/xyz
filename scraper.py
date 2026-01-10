import requests
import json
import random

# --- CONFIG ---
OUTPUT_FILE = "featured.json"

# The specific flavor you asked for
SUBREDDITS = [
    "initiald",         # Classic JDM/Drift
    "jdm",              # General JDM cars
    "Outrun",           # Cyberpunk/Synthwave cars
    "Cyberpunk",        # Futuristic/Anime vibe
    "Cinemagraphs",     # High quality loops
    "animegifs"         # Anime clips
]

def scrape():
    final_list = []
    seen_ids = set()
    
    print("--- STARTING PROXY SCRAPE ---")

    for sub in SUBREDDITS:
        # We ask the Proxy API for 10 posts from each subreddit
        # This bypasses Reddit's API blocking completely.
        url = f"https://meme-api.com/gimme/{sub}/10"
        
        try:
            print(f"🔗 Connecting to r/{sub} via Proxy...")
            resp = requests.get(url, timeout=15)
            
            if resp.status_code != 200:
                print(f"   ❌ API Error: {resp.status_code}")
                continue
            
            data = resp.json()
            posts = data.get("memes", [])
            
            for post in posts:
                # We want high quality images/gifs that can act as wallpapers
                media_url = post.get("url", "")
                
                # FILTER: Ensure it's not a tiny thumbnail or broken link
                if not media_url.startswith("http"):
                    continue
                
                # TRICK: Convert .gif to .mp4 for better performance if hosted on Imgur/Reddit
                # (AVPlayer handles mp4 much better than heavy gifs)
                if "imgur" in media_url and media_url.endswith(".gif"):
                    media_url = media_url.replace(".gif", ".mp4")
                elif "i.redd.it" in media_url and media_url.endswith(".gif"):
                    # Reddit hosted gifs often don't have direct mp4 swaps easily accessible
                    # without the raw preview link, but AVPlayer usually handles GIFs okay.
                    pass

                # We accept JPG/PNG (Images) AND MP4/GIF (Videos)
                # Your engine can handle both now.
                
                if post["postLink"] not in seen_ids:
                    # Use the highest res preview as thumbnail
                    thumb = post["preview"][-1] if post.get("preview") else media_url
                    
                    item = {
                        "id": post["postLink"].split("/")[-1], # Unique ID from URL
                        "title": post["title"],
                        "subreddit": sub,
                        "thumbnail": thumb,
                        "video_url": media_url, # Might be an image, engine handles it
                        "permalink": post["postLink"]
                    }
                    
                    final_list.append(item)
                    seen_ids.add(post["postLink"])
                    print(f"   ✅ Found: {post['title'][:20]}...")

        except Exception as e:
            print(f"   ⚠️ Exception: {e}")

    # Shuffle for variety
    random.shuffle(final_list)
    
    # Keep the best 30
    final_list = final_list[:30]

    print(f"--- SCRAPE FINISHED. Total Items: {len(final_list)} ---")
    
    if len(final_list) > 0:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(final_list, f, indent=2)
        print("💾 featured.json updated.")
    else:
        print("⚠️ No items found.")

if __name__ == "__main__":
    scrape()
