import json

# Load JSON data from files
with open("assets/my_posts.json", "r", encoding="utf-8") as f:
    posts = json.load(f)

with open("assets/comments_data.json", "r", encoding="utf-8") as f:
    comments_list = json.load(f)

# Convert comments into a dictionary format
comments_dict = {c["post_id"]: c["comments"] for c in comments_list}

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

    <script>
        let posts = {json.dumps(posts, indent=4)};
        let comments = {json.dumps(comments_dict, indent=4)};

        function filterPosts() {{
            let searchQuery = document.getElementById("search").value.toLowerCase();
            let startDate = document.getElementById("startDate").value;
            let endDate = document.getElementById("endDate").value;
            let sortOrder = document.getElementById("sortOrder").value;

            let filteredPosts = posts.filter(post => {{
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

            displayPosts(filteredPosts);
        }}

        function displayPosts(filteredPosts) {{
            let postContainer = document.getElementById("posts");
            postContainer.innerHTML = "";
            filteredPosts.forEach(post => {{
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
                            <strong>&#10084;</strong> ${{post.likes}} | <strong>&#128172;</strong> ${{post.comments}}
                        </p>
                        <p class="post-date">${{new Date(post.date).toLocaleDateString()}}</p>
                    </div>
                `;
                
                if (comments[post.post_id]) {{
                    postDiv.innerHTML += `
                    <button class='toggle-button' onclick='toggleComments("${{post.post_id}}")'>Show Comments</button>
                    <div id='comments-${{post.post_id}}' class='comments'>
                        <h4>Comments:</h4>
                        ${{comments[post.post_id].map(c => `
                        <div class='comment'>
                            <p><strong>${{c.author}}</strong> (${{c.date}}):</p>
                            <p>${{c.content}}</p>
                            <p><strong>&#10084;</strong> ${{c.likes}}</p>
                        </div>`).join('')}}
                    </div>`;
                }}
                postContainer.appendChild(postDiv);
            }});
        }}

        function toggleComments(postId) {{
            var commentsSection = document.getElementById('comments-' + postId);
            commentsSection.style.display = commentsSection.style.display === 'none' ? 'block' : 'none';
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
