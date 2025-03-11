import json
import requests
from bs4 import BeautifulSoup
import os
import time
from config import cfg  # Your credentials stored in config.py

# Login URL (Adjust if necessary)
LOGIN_URL = "https://phetasy.locals.com/ajax/ajax.login.php"

# Start a session to maintain authentication
session = requests.Session()

# Get the login page (useful for extracting hidden form fields like CSRF token)
response = session.get(LOGIN_URL)
soup = BeautifulSoup(response.text, "html.parser")

# Extract CSRF token if required
csrf_token = soup.find("input", {"name": "csrf_token"})
csrf_token = csrf_token["value"] if csrf_token else None

# Your credentials from config.py
payload = {
    "username": cfg.locals_username,
    "password": cfg.locals_password
}

# Include CSRF token if required
if csrf_token:
    payload["token"] = csrf_token

# Perform login
headers = {"User-Agent": "Mozilla/5.0"}
login_response = session.post(LOGIN_URL, data=payload, headers=headers)

# Check if login was successful
if "Invalid" in login_response.text or login_response.status_code != 200:
    print("Login failed!")
    exit(1)
else:
    print("Login successful!")

# Load posts JSON
with open("assets/my_posts.json", "r", encoding="utf-8") as file:
    posts_data = json.load(file)

comments_data = []  # List to store extracted comments

# Loop through each post
for post in posts_data:
    post_url = post.get("post_url")
    post_id = post.get("post_id")

    if not post_url:
        print(f"Skipping post {post_id} (no URL found)")
        continue

    print(f"Scraping comments for post: {post_id}")

    try:
        # Request the page while maintaining login session
        response = session.get(post_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract comments
        comment_blocks = soup.find_all("div", class_="post answer wcontainer hascomments")

        if len(comment_blocks) == 0:
            continue

        print(f"Found {len(comment_blocks)} comments for post {post_id}")

        post_comments = []
        for comment in comment_blocks:
            # Extract comment ID
            comment_id = comment.get("id", "").replace("answer-block-", "").strip()
            
            # Extract author
            author_span = comment.find("span", class_="username")
            author = author_span.text.strip() if author_span else "Unknown"

            # Extract date
            date_div = comment.find("div", class_="info")
            date = date_div.text.strip() if date_div else "Unknown"

            # Extract comment content
            content_div = comment.find("div", class_="answer-content")
            content = content_div.get_text("<br>", strip=True) if content_div else ""

            # Extract likes
            like_span = comment.find("span", class_="text")
            likes = like_span.text.strip() if like_span else "0"

            # Extract replies (if any)
            replies = []
            reply_blocks = comment.find_all("div", class_="answer-comment")

            for reply in reply_blocks:
                reply_id = reply.get("data-comment-id")
                reply_author_span = reply.find("div", class_="author")
                reply_author = reply_author_span.text.strip() if reply_author_span else "Unknown"
                reply_content_span = reply.find("span", class_="comment-text")
                reply_content = reply_content_span.get_text("<br>", strip=True) if reply_content_span else ""
                reply_likes_span = reply.find("span", class_="text")
                reply_likes = reply_likes_span.text.strip() if reply_likes_span else "0"

                replies.append({
                    "reply_id": reply_id,
                    "author": reply_author,
                    "content": reply_content,
                    "likes": reply_likes
                })

            # Append extracted comment
            post_comments.append({
                "comment_id": comment_id,
                "author": author,
                "date": date,
                "content": content,
                "likes": likes,
                "replies": replies
            })

        # Append comments to main list
        comments_data.append({"post_id": post_id, "post_url": post_url, "comments": post_comments})

        # Sleep to avoid getting blocked
        time.sleep(0.1)
    except Exception as e:
        print(f"Error scraping {post_id}: {e}")

# Save comments to a JSON file
with open("assets/comments_data.json", "w", encoding="utf-8") as f:
    json.dump(comments_data, f, indent=4)

print("Scraping complete. Comments saved to 'comments_data.json'.")
