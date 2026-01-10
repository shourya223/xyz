import requests
import json
import random
import os

OUTPUT_FILE = "featured.json"
API_KEY = os.environ.get("PEXELS_API_KEY") # We get this from GitHub Secrets

# What do you want to search for?
QUERIES = ["anime", "cyberpunk", "neon city", "space", "gaming"]

def get_best_video(video_files):
    # Find the highest resolution video that is MP4
    best_file = None
    max_width = 0
    
    for file in video_files:
        if file['file_type'] == 'video/mp4':
            if file['width'] > max_width:
                max_width = file['width']
                best_file = file
    return best_file

def scrape():
    if not API_KEY:
        print("❌ CRITICAL ERROR: PEXELS_API_KEY is missing!")
        return

    headers = {
        "Authorization": API_KEY
    }
    
    final_list = []
    seen_ids = set()

    print("--- 🚀 STARTING PEXELS FETCH ---")

    for query in QUERIES:
        print(f"🌍 Searching Pexels for: {query}...")
        
        # We ask for landscape videos (good for desktop). 
        # Change to 'portrait' if you want phone wallpapers.
        url = f"https://api.pexels.com/videos/search?query={query}&per_page=5&orientation=landscape"
        
        try:
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                print(f"   ❌ Failed: {resp.status_code}")
                continue
                
            data = resp.json()
            videos = data.get('videos', [])
            
            print(f"   Found {len(videos)} videos...")

            for v in videos:
                best_video = get_best_video(v['video_files'])
                
                if best_video:
                    # Pexels doesn't always have titles, so we make one
                    title = f"{query.title()} Wallpaper {v['id']}"
                    
                    if v['id'] not in seen_ids:
                        final_list.append({
                            "id": str(v['id']),
                            "title": title,
                            "subreddit": "Pexels",
                            "thumbnail": v['image'], # Pexels provides a thumbnail directly
                            "video_url": best_video['link'],
                            "permalink": v['url']
                        })
                        seen_ids.add(v['id'])

        except Exception as e:
            print(f"   ⚠️ Error: {e}")

    # FORCE SAVE
    if final_list:
        random.shuffle(final_list)
        # Save top 15
        with open(OUTPUT_FILE, "w") as f:
            json.dump(final_list[:15], f, indent=2)
        print(f"💾 SAVED {len(final_list)} PEXELS WALLPAPERS.")
    else:
        print("❌ No videos found. Check your API Key.")

if __name__ == "__main__":
    scrape()
