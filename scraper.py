import cloudscraper
from bs4 import BeautifulSoup
import json
import random
import time
import re

# --- CONFIG ---
OUTPUT_FILE = "featured.json"

# MyLiveWallpapers Categories
CATEGORIES = [
    "https://mylivewallpapers.com/category/anime/",
    "https://mylivewallpapers.com/category/scifi/",
    "https://mylivewallpapers.com/category/fantasy/"
]

def scrape():
    final_list = []
    seen_ids = set()
    
    # Cloudscraper is essential to bypass "Checking your browser" screens
    scraper = cloudscraper.create_scraper(browser='chrome')

    print("--- STARTING MYLIVEWALLPAPERS SCRAPE ---")

    for category_url in CATEGORIES:
        print(f"🌍 Visiting: {category_url}...")
        
        try:
            resp = scraper.get(category_url)
            if resp.status_code != 200:
                print(f"   ❌ Failed: {resp.status_code}")
                continue
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Find post links (MyLiveWallpapers structure)
            # Usually in <h3> or <a> tags inside an <article>
            posts = soup.select('article a')
            
            # Filter valid post links (exclude comments/categories)
            valid_posts = []
            for p in posts:
                href = p.get('href')
                if href and '/category/' not in href and '/page/' not in href and href not in valid_posts:
                     valid_posts.append(href)

            # Limit to top 5 per category
            valid_posts = valid_posts[:5]
            print(f"   Found {len(valid_posts)} posts. Mining...")

            for link in valid_posts:
                try:
                    # Visit the wallpaper page
                    page_resp = scraper.get(link)
                    page_soup = BeautifulSoup(page_resp.text, 'html.parser')
                    
                    title_tag = page_soup.find('h1')
                    title = title_tag.get_text(strip=True) if title_tag else "Unknown Title"

                    # 1. Find the Video URL
                    # They usually have a button: <a href="..." class="btn-download">Download</a>
                    video_url = None
                    
                    # Method A: Look for the specific download button class
                    download_btn = page_soup.select_one('a.btn-download')
                    if download_btn:
                        video_url = download_btn['href']
                    
                    # Method B: Look for any link ending in .mp4
                    if not video_url:
                        mp4_links = page_soup.find_all('a', href=re.compile(r'\.mp4$'))
                        if mp4_links:
                            video_url = mp4_links[0]['href']

                    # 2. Find the Thumbnail
                    thumb_url = ""
                    # Often in meta property="og:image"
                    meta_img = page_soup.find("meta", property="og:image")
                    if meta_img:
                        thumb_url = meta_img["content"]

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
                            print(f"      ✅ Got: {title[:25]}...")
                    
                    time.sleep(1) # Be polite

                except Exception as e:
                    print(f"      ⚠️ Failed post: {e}")
                    continue

        except Exception as e:
            print(f"   ⚠️ Category failed: {e}")

    # Shuffle and Save
    random.shuffle(final_list)
    if final_list:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(final_list, f, indent=2)
        print(f"💾 Saved {len(final_list)} wallpapers to {OUTPUT_FILE}")
    else:
        print("⚠️ No wallpapers found.")

if __name__ == "__main__":
    scrape()
