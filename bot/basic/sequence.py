import re
from typing import Any, List, Tuple

def sequence(messages) -> List[Tuple[Any, int]]:
    result: List[Tuple[int, Any, int]] = []  # (sort_episode, message, episode)

    for msg in messages:
        # Extract filename and caption
        name = (
            getattr(msg.document, "file_name", None)
            if hasattr(msg, "document")
            else msg.get("document", {}).get("file_name")
        )
        caption = (
            getattr(msg, "caption", None)
            if hasattr(msg, "caption")
            else msg.get("caption")
        )
        
        episode = 99999  # Default for sorting unidentified episodes
        
        # Search in filename first, then caption
        for text_to_search in [name, caption]:
            if not text_to_search:
                continue
            
            episode = extract_episode_number(text_to_search)
            if episode != 99999:
                break

        # Add to result for sorting
        result.append((episode, msg, episode))

    # Sort by episode number
    result.sort(key=lambda x: x[0])

    # Return only (message, episode_number) tuples
    return [(item[1], item[2]) for item in result]


def extract_episode_number(text: str) -> int:
    """
    Extract episode number with priority-based matching.
    Returns 99999 if no episode number found.
    """
    if not text:
        return 99999
    
    # Priority 1: Explicit episode markers (highest priority)
    explicit_patterns = [
        # E/EP with numbers (E97, EP08, E-07, EP 123, etc.)
        r"(?:^|\s|_|-|\[|\()(?:EP|E)(?:pisode)?\s*[-_\s]*0*(\d+)(?=\s|_|-|\]|\)|$|\.)",
        # Season + Episode (S01E05, S1EP12, Season 2 Episode 15)
        r"(?:S(?:eason)?\s*\d{1,2})\s*(?:_|\s|-)*(?:EP|E)(?:pisode)?\s*[-_\s]*0*(\d+)",
        # Episode/Part keywords (Episode 97, Part 08, etc.)
        r"(?:episode|part)\s*[-_\s]*0*(\d+)(?=\s|_|-|\]|\)|$|\.)",
        # Bracketed episode markers ([E05], (EP12), {Episode 7})
        r"[\[\({](?:EP|E)(?:pisode)?\s*[-_\s]*0*(\d+)[\]\)}]",
    ]
    
    for pattern in explicit_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except (ValueError, IndexError):
                continue
    
    # Priority 2: Season + Episode without explicit E marker (S01 05, S1-12)
    season_ep_pattern = r"(?:S(?:eason)?\s*\d{1,2})\s*(?:_|-|\s){1,3}0*(\d+)(?=\s|_|-|\.|\]|\)|$)"
    match = re.search(season_ep_pattern, text, re.IGNORECASE)
    if match:
        try:
            return int(match.group(1))
        except (ValueError, IndexError):
            pass
    
    # Priority 3: x of y format (5 of 12, 07/24)
    x_of_y_pattern = r"(?:^|\s)0*(\d+)\s*(?:of|/)\s*\d+(?=\s|_|-|\.|\]|\)|$)"
    match = re.search(x_of_y_pattern, text, re.IGNORECASE)
    if match:
        try:
            return int(match.group(1))
        except (ValueError, IndexError):
            pass
    
    # Priority 4: Dash prefixed numbers (- 05, -97)
    dash_pattern = r"(?:^|\s)-\s*0*(\d+)(?=\s|_|-|\.|\]|\)|$)"
    match = re.search(dash_pattern, text, re.IGNORECASE)
    if match:
        try:
            ep_num = int(match.group(1))
            # Avoid years and large numbers that are likely not episodes
            if ep_num < 2000:
                return ep_num
        except (ValueError, IndexError):
            pass
    
    # Priority 5: Numbers in brackets/parens ([05], (12))
    bracket_pattern = r"[\[\(]0*(\d+)[\]\)]"
    matches = re.findall(bracket_pattern, text)
    if matches:
        for match in matches:
            try:
                ep_num = int(match)
                # Prefer smaller numbers that are more likely episodes
                if ep_num < 2000:
                    return ep_num
            except ValueError:
                continue
    
    # Priority 6: Numbers at end of filename (common format like "filename 05.mkv")
    end_pattern = r"(?:_|-|\s)0*(\d+)(?=\.|$)"
    match = re.search(end_pattern, text)
    if match:
        try:
            ep_num = int(match.group(1))
            if ep_num < 2000:  # Avoid years
                return ep_num
        except (ValueError, IndexError):
            pass
    
    # Priority 7: Blacklist check and fallback to common numbers
    blacklist_pattern = re.compile(
        r"(?:no\.?\s*\d+|"           # "No.8", "No 8"
        r"\d{3,4}\s*days?|"          # "365 days", "1000 day"
        r"20\d{2}(?:\s|$)|"          # Years like "2024", "2023"
        r"\b\d+\s*(?:am|pm)\b|"      # Times like "8 AM"
        r"\d+\s*(?:mb|gb|kb|tb)|"    # File sizes
        r"\d+p(?:\s|$)|"             # Video quality like "720p"
        r"\d+\s*(?:fps|hz)\b)",      # Frame rates
        re.IGNORECASE
    )
    
    # If no blacklisted patterns, try to find any reasonable number
    if not blacklist_pattern.search(text):
        # Look for standalone numbers (2-4 digits, but avoid obvious non-episodes)
        standalone_pattern = r"(?:^|\s|_|-|\[|\()0*(\d{1,4})(?=\s|_|-|\]|\)|$|\.)"
        matches = re.findall(standalone_pattern, text)
        
        if matches:
            # Prefer smaller numbers and avoid common non-episode numbers
            for match in matches:
                try:
                    ep_num = int(match)
                    # Reasonable episode number range
                    if 1 <= ep_num <= 9999 and ep_num not in [720, 1080, 2160]:  # Avoid common video qualities
                        return ep_num
                except ValueError:
                    continue
    
    return 99999  # No episode number found
