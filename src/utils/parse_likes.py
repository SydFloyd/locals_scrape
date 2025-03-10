def parse_likes(like_text):
    """Convert formatted like counts (e.g., '1.9k') to integers."""
    like_text = like_text.strip().lower()
    multiplier = 1
    
    if 'k' in like_text:
        multiplier = 1000
        like_text = like_text.replace('k', '')
    elif 'm' in like_text:
        multiplier = 1_000_000
        like_text = like_text.replace('m', '')
    
    try:
        return int(float(like_text) * multiplier)
    except ValueError:
        print(f"Encountered an error parsing likes value ['{like_text}']")
        return 0  # Default if parsing fails
    