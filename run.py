#!/usr/bin/env python3
"""
Telegram Video Downloader Bot
Entry point for running the bot
"""

import asyncio
import sys
import os
from main import main

def check_dependencies():
    """Check if all required dependencies are available."""
    required_modules = ['telegram', 'yt_dlp']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("❌ Missing required dependencies:")
        for module in missing_modules:
            if module == 'telegram':
                print(f"  - {module} (install with: pip install python-telegram-bot)")
            else:
                print(f"  - {module} (install with: pip install {module})")
        print("\nPlease install the missing dependencies and try again.")
        return False
    
    return True

def check_bot_token():
    """Check if bot token is configured."""
    from config import BOT_TOKEN
    
    if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here":
        print("❌ Bot token not configured!")
        print("Please set the BOT_TOKEN environment variable or update config.py")
        print("Example: export BOT_TOKEN='your_actual_bot_token'")
        return False
    
    return True

if __name__ == "__main__":
    print("🤖 Telegram Video Downloader Bot")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check bot token
    if not check_bot_token():
        sys.exit(1)
    
    # Print configuration info
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        port = os.getenv("PORT", 8000)
        print(f"🌐 Mode: Webhook")
        print(f"🔗 Webhook URL: {webhook_url}")
        print(f"🚪 Port: {port}")
    else:
        print(f"📊 Mode: Polling")
    
    print(f"📁 Temp directory: temp_downloads")
    print("=" * 40)
    
    try:
        # Run the bot
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped gracefully")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
