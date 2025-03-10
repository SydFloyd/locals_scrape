from bs4 import BeautifulSoup
import requests
import os

from config import cfg
from utils.ffmpeg_download import ffmpeg_download

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
    print("Login successful!")

# Extract session cookies as a string for ffmpeg
cookies_str = "; ".join([f"{key}={value}" for key, value in session.cookies.items()])

# Directories for images and videos
IMAGE_DIR = "images"
VIDEO_DIR = "videos"
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

page = 3300
all_posts = []

try:
    while True:
        PROTECTED_URL = f"https://phetasy.locals.com/newsfeed/all/recent?page={page}"
        protected_page = session.get(PROTECTED_URL, headers=headers)
        soup = BeautifulSoup(protected_page.text, "html.parser")
        posts = soup.find_all("div", class_="wcontainer post")
        if not posts:
            print("No more posts found!")
            break
        page += 1
    print(f"Found {page} pages.")
except Exception as e:
    print(f"Encountered error: {e}")