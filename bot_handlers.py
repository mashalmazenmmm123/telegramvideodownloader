import os
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import logger
from utils import is_valid_url, is_supported_platform, cleanup_file, format_file_size
from video_downloader import downloader

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    welcome_message = """
🎬 *Video Downloader Bot*

Welcome! I can download videos from various platforms and send them to you.

*Supported platforms:*
• YouTube
• Twitter/X
• Instagram
• TikTok
• Vimeo
• Facebook
• Reddit
• Twitch
• And many more!

*How to use:*
1. Send me a video link
2. I'll download and send it back to you
3. Maximum file size: 50MB
4. Maximum duration: 30 minutes

*Commands:*
/help - Show this help message
/info <link> - Get video information without downloading

Just send me a link to get started! 🚀
    """
    
    await update.message.reply_text(
        welcome_message,
        parse_mode=ParseMode.MARKDOWN
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    await start_command(update, context)

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /info command."""
    if not context.args:
        await update.message.reply_text(
            "Please provide a video URL after the /info command.\n"
            "Example: `/info https://youtube.com/watch?v=...`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    url = context.args[0]
    
    if not is_valid_url(url):
        await update.message.reply_text(
            "❌ Invalid URL format. Please provide a valid video link."
        )
        return
    
    if not is_supported_platform(url):
        await update.message.reply_text(
            "❌ This platform is not supported. Please check /help for supported platforms."
        )
        return
    
    # Send processing message
    processing_msg = await update.message.reply_text("🔍 Getting video information...")
    
    try:
        info = await downloader.get_video_info(url)
        
        if not info:
            await processing_msg.edit_text("❌ Could not get video information.")
            return
        
        duration_str = f"{info['duration']//60}:{info['duration']%60:02d}" if info['duration'] else "Unknown"
        view_count_str = f"{info['view_count']:,}" if info['view_count'] else "Unknown"
        
        info_message = f"""
📹 *Video Information*

*Title:* {info['title']}
*Uploader:* {info['uploader']}
*Duration:* {duration_str}
*Views:* {view_count_str}

*Description:*
{info['description']}

To download this video, just send me the link!
        """
        
        await processing_msg.edit_text(
            info_message,
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Error in info command: {e}")
        await processing_msg.edit_text(
            f"❌ Error getting video information: {str(e)}"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages (video links)."""
    message_text = update.message.text.strip()
    
    # Check if message contains a URL
    if not is_valid_url(message_text):
        await update.message.reply_text(
            "Please send me a valid video link. Use /help to see supported platforms."
        )
        return
    
    # Check if platform is supported
    if not is_supported_platform(message_text):
        await update.message.reply_text(
            "❌ This platform is not currently supported.\n"
            "Use /help to see the list of supported platforms."
        )
        return
    
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "User"
    
    logger.info(f"Processing download request from {user_name} (ID: {user_id}): {message_text}")
    
    # Send initial processing message
    status_msg = await update.message.reply_text("🔄 Processing your request...")
    
    try:
        # Update status
        await status_msg.edit_text("📥 Downloading video...")
        
        # Download the video
        result = await downloader.download_video(message_text, user_id)
        
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
        
        # Send the video
        with open(file_path, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN,
                supports_streaming=True
            )
        
        # Delete status message
        await status_msg.delete()
        
        # Clean up the downloaded file
        cleanup_file(file_path)
        
        logger.info(f"Successfully processed request for user {user_id}")
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error processing request for user {user_id}: {error_message}")
        
        # Clean up any remaining files
        try:
            user_dir = os.path.join("temp_downloads", str(user_id))
            if os.path.exists(user_dir):
                import shutil
                shutil.rmtree(user_dir)
        except:
            pass
        
        await status_msg.edit_text(f"❌ {error_message}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ An unexpected error occurred. Please try again later."
        )
