import cloudscraper
from bs4 import BeautifulSoup
import json
import random
import time
import re

# --- CONFIG ---
OUTPUT_FILE = "featured.json"

CATEGORIES = [
    "https://moewalls.com/category/anime/",
    "https://moewalls.com/category/cars/",
    "https://moewalls.com/category/cyberpunk/"
]

def scrape():
    final_list = []
    seen_ids = set()

    # Initialize Cloudscraper to bypass Cloudflare
    scraper = cloudscraper.create_scraper(browser='chrome')
    
    print("--- STARTING MOEWALLS SCRAPE ---")

    for category_url in CATEGORIES:
        print(f"🌍 Visiting: {category_url}...")
        
        try:
            # use scraper.get instead of requests.get
            resp = scraper.get(category_url, timeout=15)
            
            if resp.status_code != 200:
                print(f"   ❌ Failed: {resp.status_code}")
                continue
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # MoeWalls posts are usually in h2.entry-title > a
            posts = soup.find_all('h2', class_='entry-title')
            
            if not posts:
                print("   ⚠️ No posts found. CSS selectors might have changed.")
                continue

            print(f"   Found {len(posts)} posts. Mining top 5...")
            
            # Process top 5
            for post in posts[:5]:
                try:
                    link_tag = post.find('a')
                    if not link_tag: continue
                    
                    link = link_tag['href']
                    title = post.get_text(strip=True)
                    
                    # --- DEEP DIVE ---
                    # scraper.get maintains cookies/session from the main page visit
                    page_resp = scraper.get(link, timeout=10)
                    page_soup = BeautifulSoup(page_resp.text, 'html.parser')
                    
                    video_url = None
                    
                    # Strategy 1: Direct <source> tag
                    video_tag = page_soup.find('source', type='video/mp4')
                    if video_tag:
                        video_url = video_tag['src']
                    
                    # Strategy 2: Download Button
                    if not video_url:
                        # MoeWalls often uses a specific class for the download button
                        download_btn = page_soup.find('a', class_='download-link')
                        if download_btn:
                            video_url = download_btn['href']

                    # Strategy 3: Regex search in scripts (Fallback)
                    # sometimes the video is inside a script variable like "file": "..."
                    if not video_url:
                        match = re.search(r'file:\s*"([^"]+\.mp4)"', page_resp.text)
                        if match:
                            video_url = match.group(1)

                    # Get Thumbnail
                    thumb_url = ""
                    img_tag = page_soup.find('img', class_='wp-post-image')
                    if img_tag:
                        # Handle lazy loaded images
                        thumb_url = img_tag.get('data-src') or img_tag.get('src') or ""

                    if video_url and thumb_url:
                        slug = link.strip("/").split("/")[-1]
                        
                        if slug not in seen_ids:
                            final_list.append({
                                "id": slug,
                                "title": title,
                                "subreddit": "MoeWalls",
                                "thumbnail": thumb_url,
                                "video_url": video_url,
                                "permalink": link
                            })
                            seen_ids.add(slug)
                            print(f"      ✅ Got: {title[:30]}...")
                    
                    # Politeness sleep
                    time.sleep(1.5)

                except Exception as e:
                    print(f"      ⚠️ Failed individual post: {e}")
                    continue

        except Exception as e:
            print(f"   ⚠️ Category failed: {e}")

    # Shuffle results
    random.shuffle(final_list)
    
    # Save
    if len(final_list) > 0:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(final_list, f, indent=2)
        print(f"💾 {OUTPUT_FILE} updated with {len(final_list)} wallpapers.")
    else:
        print("⚠️ No wallpapers found. Double-check selectors or Cloudflare level.")

if __name__ == "__main__":
    scrape()
