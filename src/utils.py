"""
Utility functions for Video Remix Studio.
"""
import hashlib
import time
from pathlib import Path
from typing import Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_unique_id(prefix: str = "") -> str:
    """
    Generate a unique ID based on timestamp and hash.
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        Unique identifier string
    """
    timestamp = str(time.time())
    hash_obj = hashlib.md5(timestamp.encode())
    unique_hash = hash_obj.hexdigest()[:8]
    
    if prefix:
        return f"{prefix}_{int(time.time())}_{unique_hash}"
    return f"{int(time.time())}_{unique_hash}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def get_file_size(file_path: Path) -> Optional[int]:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes or None if file doesn't exist
    """
    try:
        if file_path.exists():
            return file_path.stat().st_size
    except Exception as e:
        logger.error(f"Error getting file size for {file_path}: {e}")
    return None


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to MM:SS format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def validate_video_file(file_path: Path, max_size_mb: int = 100) -> tuple[bool, str]:
    """
    Validate a video file.
    
    Args:
        file_path: Path to video file
        max_size_mb: Maximum allowed file size in MB
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path.exists():
        return False, "File does not exist"
    
    file_size_mb = get_file_size(file_path) / (1024 * 1024) if get_file_size(file_path) else 0
    
    if file_size_mb > max_size_mb:
        return False, f"File size ({file_size_mb:.1f}MB) exceeds maximum ({max_size_mb}MB)"
    
    valid_extensions = ['.mp4', '.mov', '.avi', '.mkv']
    if file_path.suffix.lower() not in valid_extensions:
        return False, f"Invalid file format. Supported: {', '.join(valid_extensions)}"
    
    return True, ""
