import cloudscraper
from bs4 import BeautifulSoup
import json
import random
import time
import re

OUTPUT_FILE = "featured.json"

# MyLiveWallpapers is easier to scrape than MoeWalls
CATEGORIES = [
    "https://mylivewallpapers.com/category/anime/",
    "https://mylivewallpapers.com/category/scifi/",
    "https://mylivewallpapers.com/category/fantasy/"
]

def scrape():
    print("🚀 STARTING SCRAPER...")
    final_list = []
    
    # Cloudscraper bypasses basic protection
    scraper = cloudscraper.create_scraper(browser='chrome')

    for url in CATEGORIES:
        print(f"🌍 Checking: {url}")
        try:
            resp = scraper.get(url)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Find all links inside <article> tags
            links = []
            for article in soup.find_all('article'):
                a_tag = article.find('a')
                if a_tag:
                    links.append(a_tag['href'])

            # Grab top 3 from each category
            print(f"   Found {len(links)} posts. Grabbing top 3...")
            
            for link in links[:3]:
                try:
                    # Go to the wallpaper page
                    page = scraper.get(link)
                    page_soup = BeautifulSoup(page.text, 'html.parser')

                    # 1. Get Title
                    title = page_soup.find('h1').get_text(strip=True)

                    # 2. Get Video URL (Look for .mp4 link)
                    video_url = None
                    # Try finding the big download button
                    btn = page_soup.select_one('a.btn-download')
                    if btn:
                        video_url = btn['href']
                    else:
                        # Fallback: Find any link ending in .mp4
                        for a in page_soup.find_all('a', href=True):
                            if a['href'].endswith('.mp4'):
                                video_url = a['href']
                                break

                    # 3. Get Thumbnail
                    thumb_url = ""
                    meta_img = page_soup.find('meta', property='og:image')
                    if meta_img:
                        thumb_url = meta_img['content']

                    if video_url and thumb_url:
                        item = {
                            "id": link.split('/')[-2], # Use slug as ID
                            "title": title,
                            "subreddit": "MyLiveWallpapers",
                            "thumbnail": thumb_url,
                            "video_url": video_url,
                            "permalink": link
                        }
                        final_list.append(item)
                        print(f"   ✅ Got: {title[:20]}...")
                    
                    time.sleep(1) # Sleep to avoid ban

                except Exception as e:
                    print(f"   ⚠️ Skipping post: {e}")

        except Exception as e:
            print(f"❌ Category failed: {e}")

    # FORCE SAVE EVEN IF EMPTY (For debugging)
    print(f"💾 Saving {len(final_list)} items to {OUTPUT_FILE}...")
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(final_list, f, indent=2)
    
    print("🎉 DONE.")

if __name__ == "__main__":
    scrape()
