import requests
import json
import time

# Subreddits to scrape
SUBREDDITS = ["animegifs", "Cinemagraphs", "Outrun", "Cyberpunk", "aesthetic", "LofiHipHop"]
LIMIT_PER_SUB = 10
OUTPUT_FILE = "featured.json"

# Reddit requires a custom User-Agent to avoid 429 errors
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}

def get_best_video_url(data):
    # 1. Check for native Reddit video
    if "media" in data and data["media"] and "reddit_video" in data["media"]:
        return data["media"]["reddit_video"]["fallback_url"]
    
    # 2. Check for Preview (often MP4s disguised as gifs)
    if "preview" in data and "reddit_video_preview" in data["preview"]:
        return data["preview"]["reddit_video_preview"]["fallback_url"]
        
    # 3. Check for direct .mp4 or .webm links
    url = data.get("url", "")
    if url.endswith(".mp4") or url.endswith(".webm") or url.endswith(".gifv"):
        # Convert Imgur .gifv to .mp4
        if "imgur.com" in url and url.endswith(".gifv"):
            return url.replace(".gifv", ".mp4")
        return url
    
    return None

def get_thumbnail(data):
    if "thumbnail" in data and data["thumbnail"].startswith("http"):
        return data["thumbnail"]
    # Fallback to preview image
    try:
        return data["preview"]["images"][0]["source"]["url"].replace("&amp;", "&")
    except:
        return ""

def scrape():
    results = []
    seen_ids = set()

    for sub in SUBREDDITS:
        print(f"Scraping r/{sub}...")
        try:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit={LIMIT_PER_SUB}"
            resp = requests.get(url, headers=HEADERS)
            
            if resp.status_code != 200:
                print(f"Failed to fetch {sub}: {resp.status_code}")
                continue
                
            posts = resp.json()["data"]["children"]
            
            for post in posts:
                data = post["data"]
                
                # Filter safe for work only?
                if data.get("over_18"):
                    continue
                    
                vid_url = get_best_video_url(data)
                
                if vid_url and data["id"] not in seen_ids:
                    item = {
                        "id": data["id"],
                        "title": data["title"],
                        "subreddit": sub,
                        "thumbnail": get_thumbnail(data),
                        "video_url": vid_url,
                        "permalink": f"https://reddit.com{data['permalink']}"
                    }
                    results.append(item)
                    seen_ids.add(data["id"])
                    
            time.sleep(2) # Be polite to API
            
        except Exception as e:
            print(f"Error scraping {sub}: {e}")

    # Shuffle or Sort? Let's sort by random to keep it fresh, 
    # but for now let's just reverse to show newest first
    # (Reddit hot is already sorted effectively)
    
    print(f"Found {len(results)} videos.")
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    scrape()
