# Telegram Video Downloader Bot

A powerful Telegram bot that downloads videos from various platforms and sends them directly to users. Built with Python, this bot supports multiple video platforms and is ready for deployment on free cloud servers.

## Features

- 🎬 **Multi-platform Support**: YouTube, Twitter/X, Instagram, TikTok, Vimeo, Facebook, Reddit, Twitch, and more
- 📱 **Easy to Use**: Just send a video link to the bot
- ⚡ **Fast Downloads**: Asynchronous processing for quick responses
- 📏 **Smart Limits**: Automatic file size (200MB) and duration (30min) validation
- 🛡️ **Error Handling**: Comprehensive error management and user feedback
- 🧹 **Clean Storage**: Automatic cleanup of temporary files
- 🚀 **Production Ready**: Optimized for deployment on free cloud platforms

## Supported Platforms

- YouTube (youtube.com, youtu.be)
- Twitter/X (twitter.com, x.com)
- Instagram (instagram.com)
- TikTok (tiktok.com)
- Vimeo (vimeo.com)
- Dailymotion (dailymotion.com)
- Facebook (facebook.com)
- Reddit (reddit.com)
- Twitch (twitch.tv)
- And many more supported by yt-dlp!

## Quick Start

### 1. Get Your Bot Token
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow the instructions
3. Save your bot token (format: `123456789:ABCdef1234ghIkl-zyx57W2v1u123ew11`)

### 2. Deploy on Free Cloud Platforms

#### Option A: AWS Free Tier
```bash
# Clone and setup
git clone <your-repo>
cd telegram-video-bot
pip install python-telegram-bot==21.9 yt-dlp

# Set your bot token
export BOT_TOKEN="your_bot_token_here"

# Run the bot
python bot.py
```

#### Option B: Google Cloud Platform (Free Tier)
```bash
# Same steps as AWS
pip install python-telegram-bot==21.9 yt-dlp
export BOT_TOKEN="your_bot_token_here"
python bot.py
```

#### Option C: Railway, Render, or Similar
1. Fork this repository
2. Connect your Git repo to the platform
3. Set environment variable: `BOT_TOKEN=your_token_here`
4. Deploy!

### 3. Using the Bot

1. Start a chat with your bot on Telegram
2. Send `/start` to see the welcome message
3. Send any supported video link
4. The bot will download and send the video back to you

## Commands

- `/start` - Show welcome message and instructions
- `/help` - Same as start command
- Just send a video link - Download and get the video

## Technical Details

### Requirements
- Python 3.7+
- python-telegram-bot==21.9
- yt-dlp

### Configuration
- Maximum file size: 200MB
- Maximum video duration: 30 minutes
- Download timeout: 5 minutes
- Concurrent downloads: 2 maximum

### File Structure
```
telegram-video-bot/
├── bot.py              # Main bot file (production ready)
├── main.py             # Modular version (alternative)
├── bot_handlers.py     # Handler functions (modular version)
├── video_downloader.py # Download logic (modular version)
├── utils.py            # Utility functions (modular version)
├── config.py           # Configuration (modular version)
├── run.py              # Entry point (modular version)
└── README.md           # This file
```

## Environment Variables

- `BOT_TOKEN` - Your Telegram bot token (required)
- `WEBHOOK_URL` - For webhook mode deployment (optional)
- `PORT` - Port for webhook mode (default: 8000)

## Deployment Notes

### For Free Cloud Platforms:
1. **Memory**: The bot uses minimal memory (~50-100MB)
2. **Storage**: Temporary files are cleaned automatically
3. **Network**: Uses standard HTTP/HTTPS for downloads
4. **Scaling**: Handles concurrent users efficiently

### Production Recommendations:
- Set up health checks on `/healthz` endpoint (if needed)
- Use webhook mode for production deployments
- Monitor logs for download failures
- Consider rate limiting for heavy usage

## Troubleshooting

### Common Issues:

1. **Bot not responding**: Check if BOT_TOKEN is set correctly
2. **"Platform not supported"**: The video platform might not be in the supported list
3. **"File too large"**: Video exceeds 50MB limit
4. **"Video too long"**: Video exceeds 30-minute limit
5. **Download failures**: Network issues or video might be private/restricted

### Logs:
The bot provides detailed logging. Check console output for:
- Download progress
- Error messages
- User activity

## License

This project is open source. Feel free to modify and use for your needs.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Ensure your bot token is correct
4. Verify the video URL is from a supported platform

---

**Ready to deploy!** This bot is production-ready and has been tested with all major video platforms.