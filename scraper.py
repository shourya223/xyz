import cloudscraper
from bs4 import BeautifulSoup
import json
import random
import time
import os

OUTPUT_FILE = "featured.json"

# MotionBGS is often less protected than MoeWalls
CATEGORIES = [
    "https://www.motionbgs.com/category/anime/",
    "https://www.motionbgs.com/category/games/",
    "https://www.motionbgs.com/category/sci-fi/"
]

def scrape():
    final_list = []
    seen_ids = set()
    
    # Create a scraper that looks exactly like a real Chrome browser
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    print("--- 🚀 STARTING MOTIONBGS SCRAPE ---")

    for category_url in CATEGORIES:
        print(f"🌍 Visiting: {category_url}")
        
        try:
            resp = scraper.get(category_url)
            
            # DEBUG: Check if we are blocked
            if resp.status_code == 403 or "Just a moment" in resp.text:
                print(f"   ❌ BLOCKED by Cloudflare on {category_url}")
                continue

            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Find posts (MotionBGS structure)
            posts = soup.select('div.post-thumbnail a')
            
            if not posts:
                print("   ⚠️ No posts found. CSS selectors might differ or page failed to load.")
                continue

            print(f"   Found {len(posts)} posts. Mining top 3...")

            for post_link in posts[:3]:
                link = post_link.get('href')
                if not link: continue

                try:
                    # Visit the wallpaper page
                    page_resp = scraper.get(link)
                    page_soup = BeautifulSoup(page_resp.text, 'html.parser')
                    
                    # 1. Get Title
                    title = "Unknown"
                    h1 = page_soup.find('h1')
                    if h1: title = h1.get_text(strip=True)

                    # 2. Get Video URL
                    video_url = None
                    # Look for the specific download button
                    btn = page_soup.find('a', id='download_button')
                    if btn: 
                        video_url = btn['href']
                    
                    # Fallback: Look for <source> tag
                    if not video_url:
                        video_tag = page_soup.find('source', type='video/mp4')
                        if video_tag: video_url = video_tag['src']

                    # 3. Get Thumbnail
                    thumb_url = ""
                    # MotionBGS usually puts the main image in a specific div
                    img_div = page_soup.find('div', class_='post-thumbnail')
                    if img_div and img_div.find('img'):
                        thumb_url = img_div.find('img')['src']

                    if video_url and thumb_url:
                        slug = link.strip("/").split("/")[-1]
                        
                        if slug not in seen_ids:
                            final_list.append({
                                "id": slug,
                                "title": title,
                                "subreddit": "MotionBGS",
                                "thumbnail": thumb_url,
                                "video_url": video_url,
                                "permalink": link
                            })
                            seen_ids.add(slug)
                            print(f"      ✅ Got: {title[:20]}...")
                    
                    time.sleep(2) # Sleep to avoid getting banned

                except Exception as e:
                    print(f"      ⚠️ Failed post: {e}")

        except Exception as e:
            print(f"   ⚠️ Category failed: {e}")

    # SAFETY CHECK: Only save if we actually found something
    if len(final_list) > 0:
        random.shuffle(final_list)
        with open(OUTPUT_FILE, "w") as f:
            json.dump(final_list, f, indent=2)
        print(f"💾 SUCCESSFULLY SAVED {len(final_list)} WALLPAPERS.")
    else:
        print("❌ SCRAPE FAILED: List is empty. Not overwriting file.")
        # Create a dummy file if one doesn't exist so the workflow doesn't crash
        if not os.path.exists(OUTPUT_FILE):
             with open(OUTPUT_FILE, "w") as f:
                json.dump([], f)

if __name__ == "__main__":
    scrape()
