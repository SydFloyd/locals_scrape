import json
from pprint import pprint

def search_posts_with_keywords(file_path, author, keyword):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    matching_posts = [
        post for post in data
        if author.lower() in post.get('author', '').lower() and keyword.lower() in post.get('content', '').lower()
    ]
    
    return matching_posts

def search_posts_by_id(file_path, post_id):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    matching_posts = [
        post for post in data
        if post.get('post_id') == post_id
    ]
    
    return matching_posts

# Example usage
if __name__ == "__main__":
    file_path = 'assets/my_posts.json'
    # author = 'atommiller'
    # keyword = 'spotify'
    # results = search_posts_with_keywords(file_path, keyword, keyword)
    # for post in results:
    #     print(post)

    post_id = '3292201'
    results = search_posts_by_id(file_path, post_id)
    for post in results:
        pprint(post)

    # with open(file_path, 'r', encoding='utf-8') as file:
    #     data = json.load(file)
    # pprint(data[0])