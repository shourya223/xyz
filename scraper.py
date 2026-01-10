import requests
from bs4 import BeautifulSoup
import json
import random
import time
import re

# --- CONFIG ---
OUTPUT_FILE = "featured.json"

# We target the exact categories you want
# MoeWalls is perfect for this.
CATEGORIES = [
    "https://moewalls.com/category/anime/",
    "https://moewalls.com/category/cars/",
    "https://moewalls.com/category/cyberpunk/"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def scrape():
    final_list = []
    seen_ids = set()
    
    print("--- STARTING MOEWALLS SCRAPE ---")

    for category_url in CATEGORIES:
        print(f"🌍 Visiting: {category_url}...")
        
        try:
            resp = requests.get(category_url, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                print(f"   ❌ Failed: {resp.status_code}")
                continue
            
            # Parse the Category Page
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Find all individual wallpaper posts
            # (MoeWalls usually puts them in <h2 class="entry-title"><a>...</a></h2>)
            posts = soup.find_all('h2', class_='entry-title')
            
            print(f"   Found {len(posts)} posts. Mining videos...")
            
            # Limit to top 5 posts per category to keep it fast
            for post in posts[:5]:
                link = post.find('a')['href']
                title = post.get_text()
                
                # --- DEEP DIVE: Visit the actual wallpaper page ---
                # We need to go INSIDE the post to find the download link
                try:
                    page_resp = requests.get(link, headers=HEADERS, timeout=10)
                    page_soup = BeautifulSoup(page_resp.text, 'html.parser')
                    
                    # MoeWalls usually has a "Download" button linking to the file
                    # OR a <video> tag. Let's look for the MP4 directly.
                    
                    # Strategy 1: Look for the <source> tag in the video player
                    video_url = None
                    video_tag = page_soup.find('source', type='video/mp4')
                    if video_tag:
                        video_url = video_tag['src']
                        
                    # Strategy 2: Look for the "Download" button if Strategy 1 fails
                    if not video_url:
                        download_btn = page_soup.find('a', class_='download-link')
                        if download_btn:
                            video_url = download_btn['href']
                            
                    # Get Thumbnail (standard WordPress feature image)
                    thumb_url = ""
                    img_tag = page_soup.find('img', class_='wp-post-image')
                    if img_tag:
                        thumb_url = img_tag['data-src'] if 'data-src' in img_tag.attrs else img_tag['src']
                        
                    if video_url and thumb_url:
                        # Clean up the ID
                        slug = link.strip("/").split("/")[-1]
                        
                        if slug not in seen_ids:
                            final_list.append({
                                "id": slug,
                                "title": title,
                                "subreddit": "MoeWalls", # Keeping field name for app compatibility
                                "thumbnail": thumb_url,
                                "video_url": video_url,
                                "permalink": link
                            })
                            seen_ids.add(slug)
                            print(f"      ✅ Got: {title[:20]}...")
                            
                    # Be polite to their server
                    time.sleep(1) 
                    
                except Exception as e:
                    print(f"      ⚠️ Failed to parse post: {e}")

        except Exception as e:
            print(f"   ⚠️ Category failed: {e}")

    # Shuffle results
    random.shuffle(final_list)
    
    # Save
    if len(final_list) > 0:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(final_list, f, indent=2)
        print(f"💾 featured.json updated with {len(final_list)} High-Quality Wallpapers.")
    else:
        print("⚠️ No wallpapers found. Cloudflare might be blocking requests.")

if __name__ == "__main__":
    scrape()
