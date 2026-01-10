import requests
import json
import random

# --- CONFIG ---
OUTPUT_FILE = "featured.json"
# The exact vibe you want
SEARCH_TERMS = [
    "anime scenery",
    "jdm drift car",
    "cyberpunk city loop",
    "initial d drift",
    "vaporwave aesthetic",
    "pixel art city rain"
]

# Tenor Public Client Key (Replace with your own if this hits limits)
# Get one here: https://developers.google.com/tenor/guides/quickstart
API_KEY = "LIVDSRZULELA" 
CLIENT_KEY = "WallpaperEngineScraper"

def fetch_tenor():
    final_list = []
    seen_ids = set()
    
    print("--- STARTING TENOR API FETCH ---")
    
    for term in SEARCH_TERMS:
        print(f"🔍 Searching: {term}...")
        
        # We ask for 10 items per term, MP4 format
        url = f"https://g.tenor.com/v1/search?q={term}&key={API_KEY}&limit=10&media_filter=minimal"
        
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                print(f"   ❌ Error: {resp.status_code}")
                continue
                
            data = resp.json()
            results = data.get("results", [])
            
            for item in results:
                # Tenor items have a "media" list. We want the MP4 version.
                # "mediumgif" or "nanogif" usually contains the mp4 url too for efficiency
                media_collection = item.get("media", [])[0]
                
                # We specifically want MP4 because AVPlayer loves it.
                if "mp4" in media_collection:
                    video_url = media_collection["mp4"]["url"]
                    thumb_url = media_collection["mp4"]["preview"] # Preview image
                    
                    # Clean Title (Tenor titles are often empty or messy)
                    title = item.get("content_description", term.title())
                    if not title: title = term.title()

                    if video_url not in seen_ids:
                        final_list.append({
                            "id": item["id"],
                            "title": title,
                            "subreddit": "Tenor API", # Keeping field name for compatibility
                            "thumbnail": thumb_url,
                            "video_url": video_url,
                            "permalink": item["itemurl"]
                        })
                        seen_ids.add(video_url)
                        
            print(f"   ✅ Added {len(results)} loops")

        except Exception as e:
            print(f"   ⚠️ Exception: {e}")

    # Shuffle for variety
    random.shuffle(final_list)
    final_list = final_list[:50] # Keep 50 fresh loops
    
    print(f"--- FETCH FINISHED. Total: {len(final_list)} ---")
    
    if len(final_list) > 0:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(final_list, f, indent=2)
        print("💾 featured.json updated.")
    else:
        print("⚠️ No videos found.")

if __name__ == "__main__":
    fetch_tenor()
