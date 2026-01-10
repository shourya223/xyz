import requests
import json
import random

# --- CONFIG ---
OUTPUT_FILE = "featured.json"

# THESE ARE THE HIGH-RES SUBREDDITS (No memes allowed here)
SUBREDDITS = [
    "Moescape",           # High-Res Anime Scenery (Best for wallpapers)
    "Cinemagraphs",       # High-Quality Frozen Loops
    "Rain",               # Atmospheric Rain
    "Cyberpunk",          # Neon Cities
    "ImaginarySliceOfLife" # Chill Anime Vibes
]

def scrape():
    final_list = []
    seen_ids = set()
    
    print("--- STARTING HIGH-RES PROXY SCRAPE ---")

    for sub in SUBREDDITS:
        # Use Meme-API (Proxy) to bypass Reddit blocks
        url = f"https://meme-api.com/gimme/{sub}/50"
        
        try:
            print(f"💎 Mining r/{sub}...")
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200: continue
            
            posts = resp.json().get("memes", [])
            
            for post in posts:
                # FILTER: Only keep posts with HIGH upvotes (Filters out garbage)
                if post["ups"] < 300: continue
                
                # FILTER: Must be a valid image/video URL
                url = post["url"]
                if not url.startswith("http"): continue

                # CLEANUP: Convert Imgur GIFs to MP4 for better quality
                if "imgur" in url and url.endswith(".gif"):
                    url = url.replace(".gif", ".mp4")
                
                if post["postLink"] not in seen_ids:
                    # Use highest res preview
                    thumb = post["preview"][-1] if post.get("preview") else url
                    
                    final_list.append({
                        "id": post["postLink"].split("/")[-1],
                        "title": post["title"],
                        "subreddit": sub,
                        "thumbnail": thumb,
                        "video_url": url,
                        "permalink": post["postLink"]
                    })
                    seen_ids.add(post["postLink"])

        except Exception as e:
            print(f"⚠️ Error: {e}")

    random.shuffle(final_list)
    final_list = final_list[:40] # Keep top 40

    if len(final_list) > 0:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(final_list, f, indent=2)
        print(f"💾 featured.json updated with {len(final_list)} High-Res items.")

if __name__ == "__main__":
    scrape()
