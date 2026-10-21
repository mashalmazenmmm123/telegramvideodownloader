#!/usr/bin/env python3
"""
Telegram Video Downloader Bot - Professional Edition
Advanced bot with admin system, user management, and premium features
Production-ready for deployment on free cloud platforms
"""

import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
import yt_dlp
from concurrent.futures import ThreadPoolExecutor
import shutil
from urllib.parse import urlparse, unquote
import re
import requests
import urllib3
from datetime import datetime

# Disable SSL warnings for file hosting services with certificate issues
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Import database models and admin handlers
from models import init_db, get_db, User, Download, AdminLog
from admin_handlers import (
    ensure_user_exists, is_admin, admin_panel, add_admin_command,
    grant_premium_command, ban_user_command, unban_user_command,
    stats_command, user_info_command, my_status_command, handle_admin_callback
)

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "8601428470:AAGRq2X72f9RTu77ou8j1ioHHRwkQ9r1Khc")
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB
DOWNLOAD_TIMEOUT = 300  # 5 minutes
TEMP_DIR = "temp_downloads"

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Supported platforms
SUPPORTED_PLATFORMS = [
    'youtube.com', 'youtu.be', 'twitter.com', 'x.com', 'instagram.com',
    'tiktok.com', 'vimeo.com', 'dailymotion.com', 'facebook.com',
    'reddit.com', 'twitch.tv'
]

# Global executor for downloads
executor = ThreadPoolExecutor(max_workers=2)

def setup_temp_directory():
    """Create temporary directory for downloads if it doesn't exist."""
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
        logger.info(f"Created temporary directory: {TEMP_DIR}")

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

def is_direct_video_link(url):
    """Check if URL is a direct video file link."""
    try:
        parsed = urlparse(url)
        path = parsed.path.lower()
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
        return any(path.endswith(ext) for ext in video_extensions)
    except:
        return False

def is_supported_platform(url):
    """Check if the URL is from a supported platform or direct video link."""
    try:
        # Check for direct video links first
        if is_direct_video_link(url):
            return True
            
        domain = urlparse(url).netloc.lower()
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

def download_direct_video(url, user_id):
    """Download direct video file with improved error handling."""
    import requests
    import tempfile
    from urllib.parse import unquote
    import time
    
    user_dir = os.path.join(TEMP_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    
    # Get filename from URL
    parsed_url = urlparse(url)
    filename = os.path.basename(unquote(parsed_url.path))
    if not filename or '.' not in filename:
        filename = "video.mp4"
    
    file_path = os.path.join(user_dir, filename)
    
    # Download headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'identity',
        'Connection': 'keep-alive',
    }
    
    # Retry logic for different scenarios
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Try with SSL verification first, then without
            verify_ssl = attempt == 0
            
            response = requests.get(
                url, 
                headers=headers, 
                stream=True, 
                timeout=30, 
                verify=verify_ssl,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Check content length
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > MAX_FILE_SIZE:
                raise Exception(f"Video file too large ({format_file_size(int(content_length))}). Maximum allowed: {format_file_size(MAX_FILE_SIZE)}")
            
            # Download file
            with open(file_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Check size limit during download
                        if downloaded > MAX_FILE_SIZE:
                            raise Exception(f"Video file too large. Maximum allowed: {format_file_size(MAX_FILE_SIZE)}")
            
            file_size = os.path.getsize(file_path)
            
            # Validate file was downloaded properly
            if file_size == 0:
                raise Exception("Downloaded file is empty")
            
            return {
                'file_path': file_path,
                'title': os.path.splitext(filename)[0],
                'size': file_size,
                'duration': 0  # Can't determine duration for direct downloads
            }
            
        except requests.exceptions.SSLError as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            raise Exception(f"SSL connection failed: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            raise Exception(f"Connection failed: {str(e)}")
        except requests.exceptions.Timeout as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            raise Exception(f"Download timeout: {str(e)}")
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            raise e
    
    raise Exception("Download failed after multiple attempts")

def download_video_sync(url, user_id):
    """Synchronous download function."""
    # Check if it's a direct video link
    if is_direct_video_link(url):
        return download_direct_video(url, user_id)
    
    # Use yt-dlp for platform videos
    user_dir = os.path.join(TEMP_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    
    output_template = os.path.join(user_dir, '%(title)s.%(ext)s')
    
    ydl_opts = {
        'outtmpl': output_template,
        'format': 'best[height<=720]/best',
        'noplaylist': True,
        'extract_flat': False,
        'writethumbnail': True,
        'writeinfojson': False,
        'quiet': True,
        'no_warnings': True,
        'restrictfilenames': True,
        'ignoreerrors': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Get video info first
        info = ydl.extract_info(url, download=False)
        
        if not info:
            raise Exception("Could not extract video information")
        
        title = info.get('title', 'Unknown')
        duration = info.get('duration', 0)
        
        # Check if video is too long (> 30 minutes)
        if duration and duration > 1800:
            raise Exception(f"Video is too long ({duration//60} minutes). Maximum allowed: 30 minutes")
        
        # Download the video
        ydl.download([url])
        
        # Find the downloaded file
        downloaded_files = []
        for file in os.listdir(user_dir):
            file_path = os.path.join(user_dir, file)
            if os.path.isfile(file_path):
                downloaded_files.append(file_path)
        
        if not downloaded_files:
            raise Exception("No file was downloaded")
        
        # Get the most recent file
        video_file = max(downloaded_files, key=os.path.getctime)
        
        # Check file size
        file_size = os.path.getsize(video_file)
        if file_size > MAX_FILE_SIZE:
            raise Exception(f"Video file too large ({format_file_size(file_size)}). Maximum allowed: {format_file_size(MAX_FILE_SIZE)}")
        
        # Find thumbnail file
        thumbnail_path = None
        base_name = os.path.splitext(video_file)[0]
        for ext in ['.jpg', '.jpeg', '.png', '.webp']:
            thumb_file = base_name + ext
            if os.path.exists(thumb_file):
                thumbnail_path = thumb_file
                break
        
        return {
            'file_path': video_file,
            'title': title,
            'size': file_size,
            'duration': duration,
            'thumbnail': thumbnail_path
        }

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with user management"""
    user_id = str(update.effective_user.id)
    username = update.effective_user.username
    first_name = update.effective_user.first_name
    last_name = update.effective_user.last_name
    
    # Ensure user exists in database
    user = await ensure_user_exists(user_id, username, first_name, last_name)
    
    is_admin_user = await is_admin(user_id)
    
    welcome_text = f"""
🎬 **Video Downloader Bot - Professional Edition**

**Your Account:** {'⭐ Admin' if is_admin_user else '💎 Premium' if user.is_premium() else '👤 Normal User'}

I can download videos from various platforms and send them directly to you.

**Supported platforms:**
• YouTube, Twitter/X, Instagram, TikTok
• Vimeo, Facebook, Reddit, Twitch
• Direct video file links (.mp4, .avi, .mov, etc.)

**Your Limits:**
{'• Unlimited downloads' if is_admin_user or user.is_premium() else '• 10 downloads per day'}
{'• No cooldown' if is_admin_user or user.is_premium() else '• 3 minutes between downloads'}

**Commands:**
/start - Show this welcome message
/help - Get help and usage instructions
/status - Check your account status and limits
/info <url> - Get video information without downloading
{'🔧 /admin - Admin control panel' if is_admin_user else ''}

Ready to download some videos? Send me a link! 🚀
"""
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages (video links) with rate limiting."""
    message_text = update.message.text.strip()
    user_id = str(update.effective_user.id)
    username = update.effective_user.username
    first_name = update.effective_user.first_name
    last_name = update.effective_user.last_name
    user_name = first_name or "User"
    
    # Ensure user exists in database
    user = await ensure_user_exists(user_id, username, first_name, last_name)
    
    # Check if message contains a URL
    if not is_valid_url(message_text):
        await update.message.reply_text(
            "Please send me a valid video link. Use /start to see supported platforms."
        )
        return
    
    # Check if platform is supported
    if not is_supported_platform(message_text):
        await update.message.reply_text(
            "❌ This platform is not currently supported.\n"
            "Use /start to see the list of supported platforms."
        )
        return
    
    # Check user permissions and rate limits
    db = get_db()
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        
        can_download, reason = user.can_download()
        if not can_download:
            await update.message.reply_text(f"❌ {reason}")
            return
        
        logger.info(f"Processing download request from {user_name} (ID: {user_id}): {message_text}")
        
        # Send initial processing message
        status_msg = await update.message.reply_text("🔄 Processing your request...")
        
        # Update status
        await status_msg.edit_text("📥 Downloading video...")
        
        # Download the video in thread pool
        loop = asyncio.get_event_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(executor, download_video_sync, message_text, user_id),
            timeout=DOWNLOAD_TIMEOUT
        )
        
        # Update status
        await status_msg.edit_text("📤 Uploading video...")
        
        # Get file info
        file_path = result['file_path']
        title = result['title']
        file_size = result['size']
        duration = result.get('duration', 0)
        
        # Prepare caption
        duration_str = f"{duration//60}:{duration%60:02d}" if duration else "Unknown"
        caption = f"🎬 *{title}*\n📏 Size: {format_file_size(file_size)}\n⏱ Duration: {duration_str}"
        
        # Check if there's a thumbnail and send video with it
        thumbnail_path = result.get('thumbnail')
        
        with open(file_path, 'rb') as video_file:
            if thumbnail_path and os.path.exists(thumbnail_path):
                try:
                    with open(thumbnail_path, 'rb') as thumb_file:
                        await update.message.reply_video(
                            video=video_file,
                            thumbnail=thumb_file,
                            caption=caption,
                            parse_mode=ParseMode.MARKDOWN,
                            supports_streaming=True
                        )
                except Exception:
                    # If thumbnail fails, send without thumbnail
                    await update.message.reply_video(
                        video=video_file,
                        caption=caption,
                        parse_mode=ParseMode.MARKDOWN,
                        supports_streaming=True
                    )
            else:
                await update.message.reply_video(
                    video=video_file,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN,
                    supports_streaming=True
                )
        
        # Record successful download
        user.record_download()
        download_record = Download(
            user_id=user_id,
            url=message_text,
            title=title,
            file_size=file_size / (1024 * 1024),  # Convert to MB
            download_type='platform' if not is_direct_video_link(message_text) else 'direct',
            status='success'
        )
        db.add(download_record)
        db.commit()
        
        # Delete status message
        await status_msg.delete()
        
        # Clean up the downloaded files
        cleanup_file(file_path)
        if thumbnail_path and os.path.exists(thumbnail_path):
            cleanup_file(thumbnail_path)
        
        logger.info(f"Successfully processed request for user {user_id}")
        
    except asyncio.TimeoutError:
        # Record failed download
        download_record = Download(
            user_id=user_id,
            url=message_text,
            download_type='platform' if not is_direct_video_link(message_text) else 'direct',
            status='failed',
            error_message='Download timeout'
        )
        db.add(download_record)
        db.commit()
        logger.error(f"Download timeout for user {user_id}: {message_text}")
        await status_msg.edit_text("❌ Download timed out. The video might be too large or the connection is slow.")
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error processing request for user {user_id}: {error_message}")
        
        # Record failed download
        download_record = Download(
            user_id=user_id,
            url=message_text,
            download_type='platform' if not is_direct_video_link(message_text) else 'direct',
            status='failed',
            error_message=error_message
        )
        db.add(download_record)
        db.commit()
        
        # Clean up any remaining files
        try:
            user_dir = os.path.join(TEMP_DIR, str(user_id))
            if os.path.exists(user_dir):
                shutil.rmtree(user_dir)
        except:
            pass
        
        await status_msg.edit_text(f"❌ {error_message}")
    finally:
        db.close()

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ An unexpected error occurred. Please try again later."
        )

def main():
    """Main function to run the bot."""
    setup_temp_directory()
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add basic handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", start_command))
    application.add_handler(CommandHandler("status", my_status_command))
    
    # Add admin handlers
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CommandHandler("addadmin", add_admin_command))
    application.add_handler(CommandHandler("premium", grant_premium_command))
    application.add_handler(CommandHandler("ban", ban_user_command))
    application.add_handler(CommandHandler("unban", unban_user_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("userinfo", user_info_command))
    
    # Add callback handler for admin buttons
    application.add_handler(CallbackQueryHandler(handle_admin_callback))
    
    # Add message handler for video links
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    logger.info("🤖 Starting Telegram Video Downloader Bot - Professional Edition...")
    logger.info("📊 Mode: Polling")
    
    # Run the bot
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
