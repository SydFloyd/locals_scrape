import os

def generate_posts_html(posts):
    # Ensure 'posts' directory exists
    os.makedirs("posts", exist_ok=True)

    post_template = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Post Details - {post_id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            .post {{ border: 1px solid #ccc; padding: 15px; margin-bottom: 20px; }}
            .comment {{ border-left: 3px solid #ddd; padding: 10px; margin: 10px 0; }}
            .reply {{ border-left: 3px solid #bbb; padding: 8px; margin-left: 20px; }}
            .post-meta {{ color: grey; font-size: 0.9em; }}
            .back-link {{ display: block; margin-top: 20px; text-decoration: none; font-size: 1.2em; }}
        </style>
    </head>
    <body>
        <a href="../index.html" class="back-link">&larr; Back to Post Archive</a>
        <div class="post">
            <h2>Post by {author}</h2>
            <p><strong>Date:</strong> {date}</p>
            <p>{content}</p>
            {images}
            {videos}
            {youtube_links}
            <p class="post-meta">&#10084; {likes} | &#128172; {comments}</p>
        </div>

        <h3>Comments ({comments})</h3>
        {comment_section}

        <a href="../index.html" class="back-link">&larr; Back to Post Archive</a>
    </body>
    </html>"""

    for post in posts:
        post_id = post["post_id"]
        author = post["author"]
        date = post["date"].split("T")[0]
        content = post["content"]
        likes = post["likes"]
        comments = post["comments"]

        # Images
        images = (
            '<div class="images-container">'
            + "".join(f'<img src="{img}" class="image">' for img in post.get("images", []))
            + "</div>"
            if post.get("images")
            else ""
        )

        # Video
        videos = (
            f'<div class="video-container"><video controls width="400"><source src="{post["video_path"]}" type="video/mp4"></video></div>'
            if "video_path" in post and post["video_path"]
            else ""
        )

        # YouTube Links
        youtube_links = (
            '<div class="youtube-container">'
            + "".join(f'<iframe width="400" height="225" src="{yt}" frameborder="0" allowfullscreen></iframe>' for yt in post.get("youtube_links", []))
            + "</div>"
            if post.get("youtube_links")
            else ""
        )

        # Comments Section (Using content_html when available)
        comment_section = ""
        if post.get("comment_data"):
            for comment in post["comment_data"]:
                comment_content = comment.get("content_html", comment["content"])  # Use content_html if available
                comment_section += f"""
                <div class="comment">
                    <p><strong>{comment['author']}</strong> ({comment['date'].split('T')[0]}):</p>
                    <div>{comment_content}</div>
                    <p class="post-meta">&#10084; {comment['likes']}</p>
                """

                if "replies" in comment and comment["replies"]:
                    for reply in comment["replies"]:
                        reply_content = reply.get("content_html", reply["content"])  # Use content_html if available
                        comment_section += f"""
                        <div class="reply">
                            <p><strong>{reply['author']}</strong>:</p>
                            <div>{reply_content}</div>
                            <p class="post-meta">&#10084; {reply['likes']}</p>
                        </div>
                        """
                comment_section += "</div>"

        else:
            comment_section = "<p>No comments yet.</p>"

        # Generate HTML file
        post_html = post_template.format(
            post_id=post_id,
            author=author,
            date=date,
            content=content,
            likes=likes,
            comments=comments,
            images=images,
            videos=videos,
            youtube_links=youtube_links,
            comment_section=comment_section,
        )

        with open(f"posts/{post_id}.html", "w", encoding="utf-8") as f:
            f.write(post_html)
