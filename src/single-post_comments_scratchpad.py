from bs4 import BeautifulSoup
import requests
import json
import os
import re

from config import cfg
from utils.get_comments import get_comments

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

out = get_comments(session, "https://phetasy.locals.com/post/6740690/after-a-couple-hours-of-messing-around-my-son-figured-out-how-to-save-off-all-my-posts-from-locals")

from pprint import pprint
pprint(out)