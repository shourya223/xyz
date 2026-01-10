import json
import random
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIG ---
OUTPUT_FILE = "featured.json"
CATEGORIES = [
    "https://moewalls.com/category/anime/",
    "https://moewalls.com/category/cars/",
    "https://moewalls.com/category/cyberpunk/"
]

def get_driver():
    options = Options()
    options.add_argument("--headless=new") # Modern headless mode (less detectable)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    return driver

def scrape():
    final_list = []
    seen_ids = set()
    driver = get_driver()
    
    print("--- STARTING SELENIUM SCRAPE ---")

    try:
        for category_url in CATEGORIES:
            print(f"🌍 Visiting: {category_url}...")
            driver.get(category_url)
            
            # Wait for posts to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "entry-title"))
                )
            except:
                print("   ⚠️ Timeout waiting for posts. Moving on.")
                continue

            # Find posts
            posts = driver.find_elements(By.CSS_SELECTOR, "h2.entry-title a")
            post_links = [p.get_attribute("href") for p in posts[:5]] # Store links first to avoid stale elements
            
            print(f"   Found {len(post_links)} posts. Mining...")

            for link in post_links:
                if not link: continue
                
                try:
                    driver.get(link)
                    time.sleep(2) # Let JS load
                    
                    title = driver.title.replace(" Live Wallpaper - MoeWalls", "")
                    
                    # Strategy 1: Find Video Source directly
                    video_url = None
                    try:
                        video_tag = driver.find_element(By.CSS_SELECTOR, "source[type='video/mp4']")
                        video_url = video_tag.get_attribute("src")
                    except:
                        pass
                    
                    # Strategy 2: Look for 'file: "url"' pattern in page source (common in players)
                    if not video_url:
                        match = re.search(r'file:\s*"([^"]+\.mp4)"', driver.page_source)
                        if match:
                            video_url = match.group(1)

                    # Get Thumbnail
                    thumb_url = ""
                    try:
                        img_tag = driver.find_element(By.CLASS_NAME, "wp-post-image")
                        thumb_url = img_tag.get_attribute("data-src") or img_tag.get_attribute("src")
                    except:
                        pass

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
                            print(f"      ✅ Got: {title[:20]}...")

                except Exception as e:
                    print(f"      ⚠️ Failed post: {e}")

    except Exception as e:
        print(f"❌ Critical Error: {e}")
    finally:
        driver.quit()

    # Shuffle and Save
    random.shuffle(final_list)
    if len(final_list) > 0:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(final_list, f, indent=2)
        print(f"💾 Saved {len(final_list)} wallpapers to {OUTPUT_FILE}")
    else:
        print("⚠️ No wallpapers found. Cloudflare might still be blocking.")

if __name__ == "__main__":
    scrape()
