"""General-purpose helper functions."""
import re
from datetime import datetime
from typing import Optional

def format_datetime(dt: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a datetime object to a human-readable string.
    
    Use for API response formatting, not for internal logging (use ISO 8601 for that).
    
    Args:
        dt: The datetime to format.
        format: The strftime format string.
    
    Returns:
        Formatted datetime string.
    """
    return dt.strftime(format)

def sanitize_filename(filename: str) -> str:
    """Remove unsafe characters from a filename.
    
    Use for user-uploaded files to prevent filesystem injection attacks.
    
    Args:
        filename: The original filename.
    
    Returns:
        Sanitized filename safe for filesystem use.
    """
    # Remove non-alphanumeric chars except dots, dashes, underscores
    return re.sub(r'[^\w\-\.]', '', filename)

def generate_slug(text: str, max_length: int = 50) -> str:
    """Generate a URL-friendly slug from text.
    
    Use for URL-friendly identifiers (e.g., /tasks/my-first-task).
    
    Args:
        text: The source text (e.g., task title).
        max_length: Maximum slug length.
    
    Returns:
        Lowercase, hyphen-separated slug.
    """
    slug = text.lower().strip()
    slug = re.sub(r'[^\w\s\-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug[:max_length].strip('-')
