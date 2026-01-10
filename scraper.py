import requests
import json
import re
import random

# --- CONFIG ---
OUTPUT_FILE = "featured.json"
# We will scrape these categories for variety
URLS = [
    "https://mixkit.co/free-stock-video/abstract/",
    "https://mixkit.co/free-stock-video/nature/",
    "https://mixkit.co/free-stock-video/technology/"
]

# Browser Identity (Standard Chrome)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def scrape():
    final_list = []
    seen_ids = set()
    
    print("--- STARTING MIXKIT SCRAPE ---")

    for url in URLS:
        print(f"🌍 Fetching page: {url}")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                print(f"   ❌ Failed: {resp.status_code}")
                continue

            html = resp.text
            
            # Mixkit HTML Structure (Regex is faster than importing BeautifulSoup)
            # We look for the video item containers
            # Pattern: Finds the video title and the preview URL
            # Note: Mixkit puts the video URL in a <video> tag or data attribute
            
            # 1. Find all video entries
            # This regex looks for the JSON data Mixkit embeds in the page for each video
            matches = re.findall(r'window\.__NUXT__=(.*?);', html)
            
            if matches:
                # If they use NUXT (modern JS framework), extracting is hard without parsing JS.
                # Let's use a simpler "dumb" regex to find .mp4 links in the raw HTML.
                
                # Find all .mp4 URLs (Low res previews are good for thumbnails, High res for video)
                # Mixkit often separates them. Let's find the "download" page links.
                pass
            
            # FALLBACK STRATEGY: Simple Regex for video tags
            # Mixkit provides a nice MP4 preview for every item.
            video_urls = re.findall(r'src="(https://assets.mixkit.co/videos/preview/mixkit-.*?\.mp4)"', html)
            
            for vid_url in video_urls:
                # Create a unique ID from the filename
                # url example: .../mixkit-red-and-blue-lights-345.mp4
                slug = vid_url.split("/")[-1].replace(".mp4", "")
                
                if slug not in seen_ids:
                    # Construct a nice title
                    # "mixkit-red-and-blue-lights-345" -> "Red And Blue Lights"
                    title_parts = slug.split("-")[1:-1] # Skip 'mixkit' and the number
                    title = " ".join(title_parts).title()
                    
                    # Generate a thumbnail URL (Mixkit thumbnails follow a pattern)
                    # Video: .../preview/mixkit-name-123.mp4
                    # Thumb: .../thumb/mixkit-name-123.jpg (Guessing, but safer to use a placeholder or the video itself)
                    
                    # Since we are lazy, we will use the VIDEO URL as the thumb URL too. 
                    # Your App's ThumbnailGenerator handles this perfectly!
                    
                    item = {
                        "id": slug,
                        "title": title,
                        "subreddit": "Mixkit", # Keeping the field name compatible
                        "thumbnail": vid_url,  # Your app generates thumbs from video URLs anyway!
                        "video_url": vid_url,
                        "permalink": "https://mixkit.co"
                    }
                    
                    final_list.append(item)
                    seen_ids.add(slug)
                    print(f"   ✅ Found: {title}")

        except Exception as e:
            print(f"   ⚠️ Exception: {e}")

    # Randomize the list so it's not the same order every day
    random.shuffle(final_list)
    
    # Keep top 20
    final_list = final_list[:20]

    print(f"--- SCRAPE FINISHED. Total Videos: {len(final_list)} ---")
    
    if len(final_list) > 0:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(final_list, f, indent=2)
        print("💾 featured.json updated.")
    else:
        print("⚠️ No videos found. Is the regex broken?")

if __name__ == "__main__":
    scrape()
