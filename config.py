import os
import logging

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "7595834627:AAGM5tBOG7z-FyCqYU7rZV2XV1Y27eF-a2Y")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB - Telegram's limit for bots
DOWNLOAD_TIMEOUT = 300  # 5 minutes
TEMP_DIR = "temp_downloads"

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

# Video quality preferences
VIDEO_QUALITY = 'best[height<=720]/best'  # Prefer 720p or lower to reduce file size
