from bs4 import BeautifulSoup

def get_comments(session, post_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = session.get(post_url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract comments
    comment_blocks = soup.find_all("div", class_="post answer wcontainer hascomments")

    if len(comment_blocks) == 0:
        return []

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

    return post_comments