import json
from utils.generate_posts_html import generate_posts_html

# Load JSON data from files
with open("assets/my_posts.json", "r", encoding="utf-8") as f:
    raw_posts = json.load(f)

# add blank content to posts without

inputed_posts = []
for post in raw_posts:
    post_copy = post.copy()
    if not post_copy.get('content'):
        post_copy['content'] = ""
    post_copy['comment_data'] = []
    inputed_posts.append(post_copy)

posts = inputed_posts

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
        .image {{ max-width: 300px; max-height: 300px; height: auto; width: auto; object-fit: contain; display: block; }}
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
    <input type="text" id="postIdFilter" placeholder="Filter by Post ID">
    <input type="text" id="authorFilter" placeholder="Filter by Author">
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
        document.addEventListener("DOMContentLoaded", function () {{
            if (sessionStorage.getItem("returningFromPost") === "true") {{
                document.getElementById("search").value = sessionStorage.getItem("searchQuery") || "";
                document.getElementById("postIdFilter").value = sessionStorage.getItem("postIdFilter") || "";
                document.getElementById("authorFilter").value = sessionStorage.getItem("authorFilter") || "";
                document.getElementById("startDate").value = sessionStorage.getItem("startDate") || "";
                document.getElementById("endDate").value = sessionStorage.getItem("endDate") || "";
                document.getElementById("sortOrder").value = sessionStorage.getItem("sortOrder") || "newest";

                let savedPage = sessionStorage.getItem("currentPage");
                let savedScroll = sessionStorage.getItem("scrollPosition");

                if (savedPage) {{
                    currentPage = parseInt(savedPage, 10);
                }}

                filterPosts(false); // Don't reset page

                if (savedScroll) {{
                    setTimeout(() => window.scrollTo(0, savedScroll), 100);
                }}

                sessionStorage.removeItem("returningFromPost"); // Clear flag
            }} else {{
                filterPosts(); // Initial load
            }}
        }});


        document.getElementById("search").addEventListener("keydown", function (event) {{
            if (event.key === "Enter") {{
                event.preventDefault();  // Prevent form submission or accidental behavior
                filterPosts();
            }}
        }});

        document.getElementById("postIdFilter").addEventListener("keydown", function (event) {{
            if (event.key === "Enter") {{
                event.preventDefault();  // Prevent form submission or accidental behavior
                filterPosts();
            }}
        }});

        document.getElementById("authorFilter").addEventListener("keydown", function (event) {{
            if (event.key === "Enter") {{
                event.preventDefault();  // Prevent form submission or accidental behavior
                filterPosts();
            }}
        }});


        // Store scroll position and page when navigating to a post
        document.addEventListener("click", function (e) {{
            if (e.target.tagName === "A" && e.target.href.includes("posts/")) {{
                sessionStorage.setItem("scrollPosition", window.scrollY);
                sessionStorage.setItem("currentPage", currentPage);
                sessionStorage.setItem("searchQuery", document.getElementById("search").value);
                sessionStorage.setItem("postIdFilter", document.getElementById("postIdFilter").value);
                sessionStorage.setItem("authorFilter", document.getElementById("authorFilter").value);
                sessionStorage.setItem("startDate", document.getElementById("startDate").value);
                sessionStorage.setItem("endDate", document.getElementById("endDate").value);
                sessionStorage.setItem("sortOrder", document.getElementById("sortOrder").value);
                sessionStorage.setItem("returningFromPost", "true");
            }}
        }});

        let posts = {json.dumps(posts, indent=4)};

        let postsPerPage = 25;
        let currentPage = 1;
        let filteredPosts = [];

        function filterPosts(resetPage = true) {{
            if (resetPage) {{
                currentPage = 1;  // Reset to first page only if applying a new filter
            }}

            let searchQuery = document.getElementById("search").value.toLowerCase();
            let postIdFilter = document.getElementById("postIdFilter").value.toLowerCase();
            let authorFilter = document.getElementById("authorFilter").value.toLowerCase();
            let startDate = document.getElementById("startDate").value;
            let endDate = document.getElementById("endDate").value;
            let sortOrder = document.getElementById("sortOrder").value;

            filteredPosts = posts.filter(post => {{
                let matchesSearch = post.content.toLowerCase().includes(searchQuery) ||
                                    post.author.toLowerCase().includes(searchQuery);

                let matchesPostId = !postIdFilter || post.post_id.toString().toLowerCase().includes(postIdFilter);
                let matchesAuthor = !authorFilter || post.author.toLowerCase().includes(authorFilter);

                let postDate = new Date(post.date);
                let withinDateRange = (!startDate || postDate >= new Date(startDate)) && 
                                    (!endDate || postDate <= new Date(endDate));
                return matchesSearch && matchesPostId && matchesAuthor && withinDateRange;
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
                        <a href="posts/${{post.post_id}}.html">${{post.post_id}}</a>
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


generate_posts_html(raw_posts)
