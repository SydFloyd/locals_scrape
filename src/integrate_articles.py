from bs4 import BeautifulSoup
import json
import os


def extract_post_title_and_body(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract the main post title
    title_tag = soup.find('div', class_='title article-title-font-work-sans')
    title = title_tag.get_text(strip=True) if title_tag else None

    # Extract the post body
    body_div = soup.find('div', class_='mce-content-body article-body-font-work-sans')
    if body_div:
        # Get full text content, with paragraph breaks
        paragraphs = body_div.find_all('p')
        body_text = "\n\n".join(p.get_text(strip=True) for p in paragraphs)
    else:
        body_text = None

    return title, body_text

def main():
    # with open('assets/my_posts.json', 'r', encoding='utf-8') as f:
    #     my_posts = json.load(f)
    # print(f"Loaded {len(my_posts)} posts from my_posts.json")

    # collect and integrate articles
    for root, dirs, files in os.walk('assets/articles'):
        for file in files:
            post_id = file.split('.')[0]
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    title, body = extract_post_title_and_body(html_content)

                    if os.path.exists(f'posts/{post_id}.html'):
                        # copy the file to "new_posts" directory
                        new_post_path = os.path.join('new_posts', f'{post_id}.html')
                        os.makedirs('new_posts', exist_ok=True)
                        with open(new_post_path, 'w', encoding='utf-8') as new_f:
                            with open(f'posts/{post_id}.html', 'r', encoding='utf-8') as original_f:
                                new_f.write(original_f.read())
                        print(f"Copied {file} to new_posts/{post_id}.html")
                    
                    # print(f"Title: {title}")
                    # print(f"Body: {body[:100]}...")  # Print first 100 characters of body
                    print("-" * 40)  # Separator for readability
                    # Add the post to my_posts
                    # for post in my_posts:
                    #     if post['post_id'] == post_id:
                    #         print(f"Post with ID {post_id} exists in my_posts.json, updating...")
                    #         post['content'] = f"<h2>{title}</h2>\n\n{body}"

    # Save the updated my_posts.json
    # with open('assets/my_posts.json', 'w', encoding='utf-8') as f:
    #     json.dump(my_posts, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()