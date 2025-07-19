import os
import shutil
import re
from urllib.parse import urlparse
from config import TEMP_DIR, SUPPORTED_PLATFORMS, logger

def setup_temp_directory():
    """Create temporary directory for downloads if it doesn't exist."""
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
        logger.info(f"Created temporary directory: {TEMP_DIR}")

def cleanup_temp_files():
    """Clean up all files in the temporary directory."""
    try:
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
            os.makedirs(TEMP_DIR)
            logger.info("Cleaned up temporary files")
    except Exception as e:
        logger.error(f"Error cleaning up temp files: {e}")

def cleanup_file(file_path):
    """Clean up a specific file."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up file: {file_path}")
    except Exception as e:
        logger.error(f"Error cleaning up file {file_path}: {e}")

def is_valid_url(url):
    """Check if the provided string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def is_supported_platform(url):
    """Check if the URL is from a supported platform."""
    try:
        domain = urlparse(url).netloc.lower()
        # Remove 'www.' prefix if present
        domain = re.sub(r'^www\.', '', domain)
        
        for platform in SUPPORTED_PLATFORMS:
            if platform in domain:
                return True
        return False
    except:
        return False

def format_file_size(size_bytes):
    """Convert bytes to human readable format."""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f}{size_names[i]}"

def sanitize_filename(filename):
    """Sanitize filename for safe file system operations."""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200-len(ext)] + ext
    return filename
