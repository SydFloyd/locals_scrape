from bs4 import BeautifulSoup
from time import sleep, time
import requests
import asyncio
import aiohttp
import json
import os
import re

from config import cfg
from utils.ffmpeg_download import async_ffmpeg_download, async_direct_video_download
from utils.parse_likes import parse_likes
from utils.parse_date import parse_date
from utils.get_comments import get_comments

MEMBER = "atommiller" # mstranczek
SCAPE_USER_OR_ALL = "all" # "user" or "all"
SCRAPE_COMMENTS = True

# Hypothetical login URL and form fields – adapt to match Locals’ actual login flow
LOGIN_URL = "https://phetasy.locals.com/ajax/ajax.login.php"

session = requests.Session()

# Get the login page (useful for extracting hidden form fields)
response = session.get(LOGIN_URL)
soup = BeautifulSoup(response.text, "html.parser")

# Extract hidden inputs if needed (e.g., CSRF token)
csrf_token = soup.find("input", {"name": "csrf_token"})
csrf_token = csrf_token["value"] if csrf_token else None

# Your credentials
payload = {
    "username": cfg.locals_username,
    "password": cfg.locals_password
}

# Include CSRF token if required
if csrf_token:
    payload["token"] = csrf_token

# Attempt to log in
headers = {"User-Agent": "Mozilla/5.0"}
login_response = session.post(LOGIN_URL, data=payload, headers=headers)
if "Invalid" in login_response.text or login_response.status_code != 200:
    print("Login failed!")
    exit(1)
else:
    print("Login successful!", flush=True)

# Extract session cookies as a string for ffmpeg
cookies_str = "; ".join([f"{key}={value}" for key, value in session.cookies.items()])

# Directories for images and videos
IMAGE_DIR = "assets/images"
VIDEO_DIR = "assets/videos"
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

# Get already scraped post ids
if os.path.exists("assets/my_posts.json"):
    with open("assets/my_posts.json", "r", encoding="utf-8") as f:
        all_posts = json.load(f)
all_post_ids = {post["post_id"] for post in all_posts} if all_posts else set()
print("Already scraped post IDs:", len(all_post_ids))

if os.path.exists("assets/page_number.txt"):
    with open("assets/page_number.txt", "r") as f:
        page = int(f.read().strip()) - 2
else:
    page = 1
print("Starting from page:", page)
video_tasks = []

PAUSE_INTERVAL = 2

try:
    while True:
        # initialize the page number
        t0 = time()
        cached_count = 0

        if SCAPE_USER_OR_ALL == "user":
            PROTECTED_URL = f"https://phetasy.locals.com/member/{MEMBER}/posts?page={page}"
            posts_class = "wcontainer profilepost post"
        else:  
            PROTECTED_URL = f"https://phetasy.locals.com/newsfeed/all/recent?page={page}"
            posts_class = "wcontainer post"
        protected_page = session.get(PROTECTED_URL, headers=headers)
        soup = BeautifulSoup(protected_page.text, "html.parser")
        posts = soup.find_all("div", class_=posts_class)
        if not posts:
            print("No more posts found!")
            break

        for post in posts:
            print(".", end="", flush=True)
            post_data = {}

            post_id = post.get("data-id")
            post_data["post_id"] = post_id

            # Check if the post is already cached
            if post_id in all_post_ids:
                continue

            post_data["author"] = post.get("data-author")

            post_url = post.find("div", {"data-post-url": True})
            post_data["post_url"] = post_url["data-post-url"] if post_url else None

            post_text = post.select_one(".formatted.read-more-limited-inner")
            post_data["content"] = post_text.encode_contents().decode("utf-8")  # Extracts raw inner HTML

            like_span = post.select_one(".ilikebutton .text")
            post_data["likes"] = parse_likes(like_span.text)

            comment_link = post.select_one(".comments-btn")
            post_data["comments"] = int(comment_link.text.strip()) if comment_link and comment_link.text.strip().isdigit() else 0

            # Check for premium post tag
            premium_tag = post.find(string=lambda text: text and "This is a premium post - thanks for your support!" in text)
            post_data["is_premium"] = premium_tag is not None


            # Extracting the post date
            post_date_div = post.select_one(".info")
            post_data["date"] = None  # Default value

            if post_date_div:
                raw_time = post_date_div.get_text(strip=True)
                post_data["date"] = parse_date(raw_time)
            
            # Extract multiple image URLs
            post_data["images"] = []
            image_tags = post.select("a.photo, a[data-fancybox]")
            for idx, image_tag in enumerate(image_tags):
                if image_tag and image_tag.has_attr("href"):
                    image_url = image_tag["href"]
                    image_filename = f"{post_id}_{idx}.jpg"
                    image_path = os.path.join(IMAGE_DIR, image_filename)
                    if os.path.exists(image_path):
                        post_data["images"].append(image_path)
                        cached_count += 1
                    else:
                        try:
                            img_response = session.get(image_url, headers=headers, stream=True)
                            if img_response.status_code == 200:
                                with open(image_path, "wb") as img_file:
                                    for chunk in img_response.iter_content(1024):
                                        img_file.write(chunk)
                                post_data["images"].append(image_path)
                        except Exception as e:
                            print(f"Error downloading image for post {post_id}: {e}")
            
            # Extract youtube URL(s)
            post_data["youtube_links"] = []
            
            # Check for embedded YouTube video in data-src
            youtube_embed = post.select_one("div[data-src*='youtube.com/embed/']")
            if youtube_embed and youtube_embed.has_attr("data-src"):
                post_data["youtube_links"].append(youtube_embed["data-src"])

            # Check for YouTube links in the share data-url attribute
            share_link = post.select_one("span.item-share")
            if share_link and share_link.has_attr("data-url"):
                youtube_match = re.findall(r"(https?:\/\/(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)[\w-]+)", share_link["data-url"])
                post_data["youtube_links"].extend(youtube_match)

            # Remove duplicates
            post_data["youtube_links"] = list(set(post_data["youtube_links"]))
            
            # Extract videos
            video_tag = post.select_one("video source[data-src]")
            video_container = post.select_one("video")
            if video_tag:
                post_url = video_container.get("data-post-url", "")
    
                # Skip videos with "dumpster-fire-" in the post URL
                if "dumpster-fire-" in post_url:
                    print("🔥", end="", flush=True)
                    post_data["video_path"] = "dumpster-fire"
                else:
                    video_url = "https://phetasy.locals.com" + video_tag["data-src"]
                    video_filename = f"{post_id}.mp4"
                    video_path = os.path.join(VIDEO_DIR, video_filename)
                    post_data["video_path"] = video_path

                    if not os.path.exists(video_path):
                        if video_url.endswith(".m3u8"):
                            video_tasks.append(asyncio.create_task(async_ffmpeg_download(video_url, video_path, cookies_str)))
                            print(f"Added ffmpeg download task for: {video_path}")
                        else:
                            video_tasks.append(asyncio.create_task(async_direct_video_download(video_url, video_path, session)))  # aiohttp session
                            print(f"Added direct download task for: {video_path}")
                    else:
                        cached_count += 1

            if SCRAPE_COMMENTS:
                post_data["comment_data"] = get_comments(session, post_data["post_url"])
                sleep(PAUSE_INTERVAL)
            
            all_posts.append(post_data)

        print(f"\nScraped page {page} ({len(posts)} posts - {cached_count} cached) in {time() - t0:.2f} seconds")
        # pickle the page number
        with open("assets/page_number.txt", "w") as f:
            f.write(str(page))
        page += 1
        sleep(PAUSE_INTERVAL)
except Exception as e:
    print(f"Encountered error: {e}")
    raise e
finally:
    with open("assets/page_number.txt", "w") as f:
        f.write(str(page))

    with open("assets/my_posts.json", "w", encoding="utf-8") as f:
        json.dump(all_posts, f, indent=4)
    print("\nAll posts saved!")

    if len(video_tasks) > 0:
        print("Running video tasks...")
         # Run video tasks

        async def run_video_tasks():
            async with aiohttp.ClientSession(cookies=session.cookies.get_dict(), headers=headers) as aio_sess:
                await asyncio.gather(*(task if "aiohttp" in str(task) else task for task in video_tasks))

        asyncio.run(run_video_tasks())