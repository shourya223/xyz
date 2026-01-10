import requests
import json
import random

# --- CONFIG ---
OUTPUT_FILE = "featured.json"

# A curated list of "High Aesthetic" subreddits
# We removed r/jdm because it has too many memes/text posts.
SUBREDDITS = [
    "Moescape",         # High-quality Anime Scenery (The best for backgrounds)
    "AnimeGifs",        # Actual anime clips
    "Outrun",           # Synthwave/Neon cars
    "Kyousaya",         # Specific high-quality anime art style
    "CityPorn",         # High-res city nightscapes
    "CarPorn",          # High-res car photography (No memes)
    "Cinemagraphs",     # Professional loops
    "ImaginarySliceOfLife" # Chill anime vibes
]

def scrape():
    final_list = []
    seen_ids = set()
    
    print("--- STARTING HIGH-QUALITY SCRAPE ---")

    for sub in SUBREDDITS:
        # Fetch 50 posts (Meme-API limit) so we have a pool to filter from
        url = f"https://meme-api.com/gimme/{sub}/50"
        
        try:
            print(f"💎 Mining r/{sub}...")
            resp = requests.get(url, timeout=15)
            
            if resp.status_code != 200:
                print(f"   ❌ API Error: {resp.status_code}")
                continue
            
            data = resp.json()
            posts = data.get("memes", [])
            
            # --- QUALITY FILTER ---
            filtered_posts = []
            for post in posts:
                # 1. REMOVE NSFW (Just in case)
                if post.get("nsfw", False):
                    continue

                # 2. UPVOTE THRESHOLD (The "Shitpost Filter")
                # If a post has less than 300 upvotes, it's probably low quality or a random question.
                if post.get("ups", 0) < 300:
                    continue

                # 3. URL CHECK
                media_url = post.get("url", "")
                if not media_url.startswith("http"):
                    continue

                filtered_posts.append(post)

            # Sort by upvotes (Best content first)
            filtered_posts.sort(key=lambda x: x["ups"], reverse=True)

            # Take the top 5 BEST items from this subreddit
            top_picks = filtered_posts[:5]

            for post in top_picks:
                # Fix Imgur/Reddit GIF links to MP4 where possible for performance
                media_url = post["url"]
                if "imgur" in media_url and media_url.endswith(".gif"):
                    media_url = media_url.replace(".gif", ".mp4")
                
                # Deduplicate
                if post["postLink"] not in seen_ids:
                    # Use high-res preview if available
                    thumb = post["preview"][-1] if post.get("preview") else media_url
                    
                    item = {
                        "id": post["postLink"].split("/")[-1],
                        "title": post["title"],
                        "subreddit": sub,
                        "thumbnail": thumb,
                        "video_url": media_url,
                        "permalink": post["postLink"],
                        "score": post["ups"] # Just for debugging
                    }
                    
                    final_list.append(item)
                    seen_ids.add(post["postLink"])
                    print(f"   ✨ Added: {post['title'][:20]}... ({post['ups']} upvotes)")

        except Exception as e:
            print(f"   ⚠️ Exception: {e}")

    # Shuffle the final mix so it's not sorted by subreddit
    random.shuffle(final_list)
    
    # Cap at 40 high-quality items
    final_list = final_list[:40]

    print(f"--- SCRAPE FINISHED. Total Gems: {len(final_list)} ---")
    
    if len(final_list) > 0:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(final_list, f, indent=2)
        print("💾 featured.json updated.")
    else:
        print("⚠️ No items found after filtering.")

if __name__ == "__main__":
    scrape()
