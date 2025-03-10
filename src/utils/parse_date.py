from datetime import datetime, timedelta, timezone
import re

def parse_post_date(raw_time):
    """
    Parses the date from a post and returns absolute time formatted as ISO 8601 string.
    """
    now = datetime.now(timezone.utc)
    relative_match = re.match(r"(\d+)\s+(minutes?|hours?|days?)\s+ago", raw_time)
    
    if relative_match:
        num, unit = relative_match.groups()
        num = int(num)
        
        if "minute" in unit:
            absolute_time = now - timedelta(minutes=num)
        elif "hour" in unit:
            absolute_time = now - timedelta(hours=num)
        elif "day" in unit:
            absolute_time = now - timedelta(days=num)
        else:
            return None
        
        return absolute_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Check if it's an absolute date (e.g., "March 9, 2025")
    try:
        absolute_time = datetime.strptime(raw_time, "%B %d, %Y").replace(tzinfo=timezone.utc)
        return absolute_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        print(f"Couldn't parse date ['{raw_time}']")
        return None