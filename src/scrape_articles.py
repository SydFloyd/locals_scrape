from bs4 import BeautifulSoup
from time import sleep, time
import requests
import asyncio
import aiohttp
import json
import os
import re

from config import cfg

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

async def main():

    # Extract session cookies as a string for ffmpeg
    cookies_str = "; ".join([f"{key}={value}" for key, value in session.cookies.items()])

    async with aiohttp.ClientSession(cookies=session.cookies.get_dict(), headers=headers) as aio_sess:
        video_tasks = []

        # Directories for images and videos
        IMAGE_DIR = "assets/images"
        VIDEO_DIR = "assets/videos"
        os.makedirs(IMAGE_DIR, exist_ok=True)
        os.makedirs(VIDEO_DIR, exist_ok=True)

        PAUSE_INTERVAL = 3

        def get_post_ids():
            with open("src/articles_dump.txt", "r", encoding="utf-8") as f:
                articles_dump = f.read()
            # post ids appear in 'href="/phetasy/feed?post=4105294"'
            post_ids = re.findall(r'href="/phetasy/feed\?post=(\d+)"', articles_dump)
            return set(post_ids)
        
        with open("assets/my_posts.json", "r") as f:
            all_posts = json.load(f)
        
        os.makedirs("assets/articles", exist_ok=True)

        for post_id in get_post_ids():
            
            post_data = [post for post in all_posts if post.get("post_id") == post_id]
            if len(post_data) == 0:
                print(f"Post ID {post_id} not found in my_posts.json, skipping.")
                continue
            if len(post_data) > 1:
                print(f"Multiple entries found for Post ID {post_id}, using the first one.")
            post_data = post_data[0]
            post_url = post_data.get("post_url")
            if not post_url:
                print(f"No post URL found for Post ID {post_id}, skipping.")
                continue

            protected_page = session.get(post_url, headers=headers)
            # soup = BeautifulSoup(protected_page.text, "html.parser")
            with open(f"assets/articles/{post_id}.html", "w", encoding="utf-8") as f:
                f.write(protected_page.text)
            print(f"Saved article {post_id} to assets/articles/{post_id}.html")
            sleep(PAUSE_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
    print("Done scraping articles.")