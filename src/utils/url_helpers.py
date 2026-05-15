"""URL parsing and validation utilities."""
import re
from src.core.exceptions import ValidationError


def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from URL.
    
    Args:
        url: YouTube URL (youtube.com or youtu.be format)
        
    Returns:
        11-character video ID
        
    Raises:
        ValidationError: If video ID cannot be extracted
    """
    pattern = r'(?:v=|/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    
    if not match:
        raise ValidationError(f"Could not extract video ID from URL: {url}")
    
    return match.group(1)
