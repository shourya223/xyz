import cloudscraper
from bs4 import BeautifulSoup
import json
import random
import time
import re
import os

# --- CONFIG ---
OUTPUT_FILE = "featured.json"
CATEGORIES = [
    "https://mylivewallpapers.com/category/anime/",
    "https://mylivewallpapers.com/category/scifi/",
    "https://mylivewallpapers.com/category/fantasy/"
]

def scrape():
    final_list = []
    seen_ids = set()
    scraper = cloudscraper.create_scraper(browser='chrome')

    print("--- STARTING SCRAPE ---")

    for category_url in CATEGORIES:
        print(f"🌍 Visiting: {category_url}")
        try:
            resp = scraper.get(category_url)
            if resp.status_code != 200:
                print(f"❌ Failed to load category: {resp.status_code}")
                continue
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Select article links
            posts = soup.select('article a')
            
            # Filter clean links
            valid_posts = []
            for p in posts:
                href = p.get('href')
                if href and '/category/' not in href and '/page/' not in href:
                    if href not in valid_posts:
                        valid_posts.append(href)

            # Process top 4 from each category
            for link in valid_posts[:4]:
                try:
                    page_resp = scraper.get(link)
                    page_soup = BeautifulSoup(page_resp.text, 'html.parser')
                    
                    # Get Title
                    title = "Unknown"
                    h1 = page_soup.find('h1')
                    if h1: title = h1.get_text(strip=True)

                    # Get Video URL
                    video_url = None
                    # Method 1: Button
                    btn = page_soup.select_one('a.btn-download')
                    if btn: video_url = btn['href']
                    
                    # Method 2: Direct link
                    if not video_url:
                        mp4s = page_soup.find_all('a', href=re.compile(r'\.mp4$'))
                        if mp4s: video_url = mp4s[0]['href']

                    # Get Thumbnail
                    thumb_url = ""
                    meta_img = page_soup.find("meta", property="og:image")
                    if meta_img: thumb_url = meta_img["content"]

                    if video_url and thumb_url:
                        slug = link.strip("/").split("/")[-1]
                        if slug not in seen_ids:
                            final_list.append({
                                "id": slug,
                                "title": title,
                                "subreddit": "MyLiveWallpapers",
                                "thumbnail": thumb_url,
                                "video_url": video_url,
                                "permalink": link
                            })
                            seen_ids.add(slug)
                            print(f"   ✅ Found: {title[:20]}...")
                    
                    time.sleep(1)

                except Exception as e:
                    print(f"   ⚠️ Failed post: {e}")

        except Exception as e:
            print(f"⚠️ Category Error: {e}")

    # FORCE SAVE
    random.shuffle(final_list)
    if len(final_list) > 0:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(final_list, f, indent=2)
        print(f"💾 SUCCESSFULLY SAVED {len(final_list)} ITEMS TO {OUTPUT_FILE}")
    else:
        print("❌ NO WALLPAPERS FOUND - Check selectors")

if __name__ == "__main__":
    scrape()
