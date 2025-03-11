from bs4 import BeautifulSoup

def get_comments(session, post_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = session.get(post_url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract comments
    comment_blocks = soup.find_all("div", class_="post answer wcontainer hascomments")

    if not comment_blocks:
        return []

    post_comments = []
    for comment in comment_blocks:
        comment_id = comment.get("id", "").replace("answer-block-", "").strip()

        # Extract author
        author_span = comment.find("span", class_="username")
        author = author_span.get_text(strip=True) if author_span else "Unknown"

        # Extract date
        date_div = comment.find("div", class_="info")
        date = date_div.get_text(strip=True) if date_div else "Unknown"

        # Extract comment content (plain text)
        content_div = comment.find("div", class_="text formatted")
        content = content_div.get_text("<br>", strip=True) if content_div else ""

        # Extract comment raw HTML
        content_html = str(content_div) if content_div else ""

        # Extract likes
        like_span = comment.find("span", class_="text")
        likes = like_span.get_text(strip=True) if like_span else "0"

        # Extract replies
        replies = []
        reply_container = soup.find("div", class_=f"comment-block-{comment_id}")  # Find the correct reply block

        if reply_container:
            reply_blocks = reply_container.find_all("div", class_="answer-comment")

            for reply in reply_blocks:
                reply_id = reply.get("data-comment-id", "").strip()

                # Extract reply author
                reply_author_span = reply.find("div", class_="author")
                reply_author = reply_author_span.get_text(strip=True) if reply_author_span else "Unknown"

                # Extract reply content (plain text)
                reply_content_span = reply.find("span", class_=f"comment-text formatted comment-holder-{reply_id}")
                reply_content = reply_content_span.get_text("<br>", strip=True) if reply_content_span else ""

                # Extract reply raw HTML
                reply_content_html = str(reply_content_span) if reply_content_span else ""

                # Extract reply likes
                reply_likes_span = reply.find("span", class_="text")
                reply_likes = reply_likes_span.get_text(strip=True) if reply_likes_span else "0"

                replies.append({
                    "reply_id": reply_id,
                    "author": reply_author,
                    "content": reply_content,
                    "content_html": reply_content_html,  # Raw HTML
                    "likes": reply_likes
                })

        post_comments.append({
            "comment_id": comment_id,
            "author": author,
            "date": date,
            "content": content,
            "content_html": content_html,  # Raw HTML
            "likes": likes,
            "replies": replies
        })

    return post_comments
