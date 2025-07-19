# Deployment Guide

## Quick Deployment Instructions

### Required Dependencies
```bash
pip install python-telegram-bot==21.9 yt-dlp
```

### Environment Variables
```bash
export BOT_TOKEN="your_telegram_bot_token_here"
```

### Run the Bot
```bash
python bot.py
```

## Platform-Specific Deployment

### AWS EC2 Free Tier
1. Launch t2.micro instance with Ubuntu
2. Install Python 3 and pip
3. Clone repository and install dependencies
4. Set BOT_TOKEN environment variable
5. Run: `python bot.py`

### Railway
1. Connect GitHub repository
2. Set environment variable: `BOT_TOKEN`
3. Deploy automatically

### Render
1. Connect GitHub repository  
2. Set environment variable: `BOT_TOKEN`
3. Deploy as web service

### Google Cloud Platform
1. Create free tier compute instance
2. Follow same steps as AWS

## Production Notes
- Bot runs in polling mode by default
- Webhook mode available for production (set WEBHOOK_URL)
- Memory usage: ~50-100MB
- Automatic file cleanup
- Handles concurrent users

## Success Confirmation
When running correctly, you'll see:
```
🤖 Starting Telegram Video Downloader Bot...
📊 Mode: Polling
Application started
```

Your bot is now ready to download videos!