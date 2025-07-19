import asyncio
import sys
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN, logger
from bot_handlers import start_command, help_command, info_command, handle_message, error_handler
from utils import setup_temp_directory, cleanup_temp_files

class TelegramVideoBot:
    def __init__(self):
        self.application = None
        
    async def setup(self):
        """Set up the bot application."""
        # Create application
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", start_command))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(CommandHandler("info", info_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Add error handler
        self.application.add_error_handler(error_handler)
        
        # Setup temp directory
        setup_temp_directory()
        
        logger.info("Bot setup completed")
    
    async def start_polling(self):
        """Start the bot with polling."""
        if not self.application:
            await self.setup()
        
        logger.info("Starting bot with polling...")
        await self.application.run_polling(
            drop_pending_updates=True,
            allowed_updates=['message', 'callback_query']
        )
    
    async def start_webhook(self, webhook_url, port=8000):
        """Start the bot with webhook (for deployment)."""
        if not self.application:
            await self.setup()
        
        logger.info(f"Starting bot with webhook: {webhook_url}")
        await self.application.run_webhook(
            listen="0.0.0.0",
            port=port,
            webhook_url=webhook_url,
            drop_pending_updates=True
        )
    
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up bot resources...")
        cleanup_temp_files()
        
        if self.application:
            await self.application.stop()

# Global bot instance
bot = TelegramVideoBot()

async def main():
    """Main function to run the bot."""
    import os
    
    # Check if webhook URL is provided (for deployment)
    webhook_url = os.getenv("WEBHOOK_URL")
    port = int(os.getenv("PORT", 8000))
    
    if webhook_url:
        logger.info("Running in webhook mode")
        await bot.start_webhook(webhook_url, port)
    else:
        logger.info("Running in polling mode")
        await bot.start_polling()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
