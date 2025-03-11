import json

# Load JSON data from files
with open("assets/my_posts.json", "r", encoding="utf-8") as f:
    posts = json.load(f)


# HTML template with JSON data embedded
html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Post Archive</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        input, select, button {{ margin: 5px; padding: 5px; }}
        .post {{ border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; }}
        .images-container, .youtube-container {{ display: flex; gap: 10px; overflow-x: auto; padding: 5px; }}
        .image {{ max-width: 300px; height: auto; display: block; }}
        .video-container {{ margin-top: 10px; }}
        .comments {{ margin-top: 10px; padding-left: 15px; border-left: 2px solid #ddd; display: none; }}
        .toggle-button {{ background-color: #008CBA; color: white; border: none; padding: 5px; cursor: pointer; }}
        .post-footer {{ display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }}
        .post-likes-comments {{ margin: 0; }}
        .post-date {{ color: grey; font-size: 0.9em; font-style: italic; margin: 0; }}
    </style>
</head>
<body>
    <h1>Phetasy</h1>
    <input type="text" id="search" placeholder="Search posts...">
    <input type="date" id="startDate">
    <input type="date" id="endDate">
    <button onclick="filterPosts()">Filter</button>
    <select id="sortOrder" onchange="filterPosts()">
        <option value="newest">Newest First</option>
        <option value="oldest">Oldest First</option>
        <option value="most_liked">Most Liked</option>
    </select>
    <div id="posts"></div>
    <div id="pagination" style="text-align: center; margin-top: 20px;"></div>

    <script>
        let posts = {json.dumps(posts, indent=4)};

        let postsPerPage = 25;
        let currentPage = 1;
        let filteredPosts = [];

        function filterPosts(resetPage = true) {{
            if (resetPage) {{
                currentPage = 1;  // Reset to first page only if applying a new filter
            }}

            let searchQuery = document.getElementById("search").value.toLowerCase();
            let startDate = document.getElementById("startDate").value;
            let endDate = document.getElementById("endDate").value;
            let sortOrder = document.getElementById("sortOrder").value;

            filteredPosts = posts.filter(post => {{
                let matchesSearch = post.content.toLowerCase().includes(searchQuery) ||
                                    post.author.toLowerCase().includes(searchQuery);
                let postDate = new Date(post.date);
                let withinDateRange = (!startDate || postDate >= new Date(startDate)) && 
                                    (!endDate || postDate <= new Date(endDate));
                return matchesSearch && withinDateRange;
            }});

            if (sortOrder === "newest") {{
                filteredPosts.sort((a, b) => new Date(b.date) - new Date(a.date));
            }} else if (sortOrder === "oldest") {{
                filteredPosts.sort((a, b) => new Date(a.date) - new Date(b.date));
            }} else if (sortOrder === "most_liked") {{
                filteredPosts.sort((a, b) => b.likes - a.likes);
            }}

            displayPosts();
        }}

        function displayPosts() {{
            let postContainer = document.getElementById("posts");
            postContainer.innerHTML = "";

            let startIndex = (currentPage - 1) * postsPerPage;
            let endIndex = startIndex + postsPerPage;
            let paginatedPosts = filteredPosts.slice(startIndex, endIndex);

            paginatedPosts.forEach(post => {{
                let postDiv = document.createElement("div");
                postDiv.className = "post";
                postDiv.innerHTML = `
                    <h3>
                        <a href='${{post.post_url}}' target="_blank">${{post.post_id}}</a>
                        ${{post.is_premium ? " 🔒" : ""}}
                    </h3>
                    <p><strong>Author:</strong> ${{post.author}}</p>
                    <p>${{post.content}}</p>
                `;
                
                if (post.images.length) {{
                    postDiv.innerHTML += `<div class='images-container'>${{post.images.map(img => `<img src='${{img}}' class='image'>`).join('')}}</div>`;
                }}
                
                if (post.video_path) {{
                    postDiv.innerHTML += `
                    <div class='video-container'>
                        <video controls width="400">
                            <source src="${{post.video_path}}" type="video/mp4">
                        </video>
                    </div>`;
                }}
                
                if (post.youtube_links.length) {{
                    postDiv.innerHTML += `<div class='youtube-container'>${{post.youtube_links.map(link => `<iframe width="400" height="225" src="${{link}}" frameborder="0" allowfullscreen></iframe>`).join('')}}</div>`;
                }}

                postDiv.innerHTML += `
                    <div class="post-footer">
                        <p class="post-likes-comments">
                            <strong>&#10084;</strong> ${{post.likes}} | 
                            <strong>&#128172;</strong> 
                            ${{
                                post.comments > 0 
                                ? `<a href="posts/${{post.post_id}}.html">${{post.comments}}</a>` 
                                : post.comments
                            }}
                        </p>
                        <p class="post-date">${{new Date(post.date).toLocaleDateString()}}</p>
                    </div>
                `;

                postContainer.appendChild(postDiv);
            }});

            updatePaginationControls(filteredPosts.length);
        }}

        function updatePaginationControls(totalPosts) {{
            let paginationContainer = document.getElementById("pagination");
            paginationContainer.innerHTML = `
                <button onclick="prevPage()" ${{currentPage === 1 ? "disabled" : ""}}>Previous</button>
                <span> Page ${{currentPage}} of ${{Math.ceil(totalPosts / postsPerPage)}} </span>
                <button onclick="nextPage()" ${{currentPage * postsPerPage >= totalPosts ? "disabled" : ""}}>Next</button>
            `;
        }}

        function nextPage() {{
            if (currentPage * postsPerPage < filteredPosts.length) {{
                currentPage++;
                displayPosts();
                window.scrollTo({{ top: 0, behavior: "smooth" }});  // Scroll to top
            }}
        }}

        function prevPage() {{
            if (currentPage > 1) {{
                currentPage--;
                displayPosts();
                window.scrollTo({{ top: 0, behavior: "smooth" }});  // Scroll to top
            }}
        }}

        filterPosts();

    </script>
</body>
</html>
"""

# Write the HTML file
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print("HTML file generated: index.html")


import os

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

    # Comments Section
    comment_section = ""
    if post.get("comment_data"):
        for comment in post["comment_data"]:
            comment_section += f"""
            <div class="comment">
                <p><strong>{comment['author']}</strong> ({comment['date'].split('T')[0]}):</p>
                <p>{comment['content']}</p>
                <p class="post-meta">&#10084; {comment['likes']}</p>
            """
            if "replies" in comment and comment["replies"]:
                for reply in comment["replies"]:
                    comment_section += f"""
                    <div class="reply">
                        <p><strong>{reply['author']}</strong>:</p>
                        <p>{reply['content']}</p>
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

print("Individual post pages generated in 'posts/' directory.")
