from fastapi import FastAPI

app = FastAPI(title="Telegram Video Downloader", version="1.0.0")


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "telegram-video-downloader",
        "message": "This is the Vercel-compatible status page. The actual Telegram bot runs on Render/Railway/VPS, not in Vercel's serverless environment.",
        "backend": "Render or Railway recommended",
    }


@app.get("/health")
async def health():
    return {
        "ok": True,
        "status": "healthy",
        "service": "telegram-video-downloader",
        "mode": "vercel-wrapper",
    }


@app.get("/status")
async def status():
    return {
        "app": "Telegram Video Downloader",
        "runtime": "Vercel Python wrapper",
        "bot_runtime": "Render/Railway recommended",
        "note": "The long-running Telegram bot requires a persistent environment that is not suitable for Vercel's free serverless plan.",
    }
