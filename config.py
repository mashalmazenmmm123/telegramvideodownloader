import os
import logging

# Bot configuration
# NEVER hardcode Telegram tokens in source files. Store them as environment variables.
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB to keep resource usage low and avoid free-plan overload
DOWNLOAD_TIMEOUT = 150  # 2.5 minutes per download
TEMP_DIR = os.getenv("TEMP_DIR", "temp_downloads")

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Supported platforms (yt-dlp supports many more)
SUPPORTED_PLATFORMS = [
    'youtube.com', 'youtu.be', 'twitter.com', 'x.com', 'instagram.com',
    'tiktok.com', 'vimeo.com', 'dailymotion.com', 'facebook.com',
    'reddit.com', 'twitch.tv'
]

# Video quality preferences - lower quality to reduce file size and server usage
VIDEO_QUALITY = 'best[height<=480]/best'
