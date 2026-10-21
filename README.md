# Telegram Video Downloader Bot

This repository contains:
- the original long-running Python Telegram bot in the root files
- a small Vercel-compatible wrapper in `api/index.py`

Important: The Telegram bot itself cannot run reliably on Vercel's free/serverless plan because it must stay alive continuously and write temporary media files locally.

Recommended setup:
- Bot runtime: Render / Railway / VPS
- Frontend/health page: Vercel

## Vercel deployment

Vercel will deploy the wrapper in `api/index.py` and expose:
- `/` for the status page
- `/health` for health checks
- `/status` for service metadata

## Production bot deployment

Set these environment variables in your bot host (Render/Railway/VPS):
- `BOT_TOKEN`
- `TEMP_DIR=temp_downloads`
- `PORT=8000`

Then start the bot with:

```bash
python run.py
```

Important:
- do not hardcode the Telegram token in source files
- do not push secrets to GitHub
