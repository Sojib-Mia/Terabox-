import os
import re
import requests
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Create downloads folder
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# Terabox headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://www.terabox.com/"
}

async def download_video(url: str) -> str:
    try:
        response = requests.get(url, headers=HEADERS, stream=True, timeout=30)
        response.raise_for_status()
        
        filename = f"downloads/video_{len(os.listdir('downloads')) + 1}.mp4"
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
        return filename
    except Exception as e:
        print(f"Download Error: {e}")
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    video_urls = re.findall(r'https?://terabox[^\s]+', text)
    
    if not video_urls:
        await update.message.reply_text("❌ Invalid TeraBox Link!")
        return
    
    await update.message.reply_text("📥 Downloading... (10-30 seconds)")
    
    try:
        video_file = await download_video(video_urls[0])
        if not video_file:
            raise Exception("Download Failed")
        
        with open(video_file, 'rb') as video:
            await update.message.reply_video(
                video, 
                read_timeout=100, 
                write_timeout=100,
                caption="✅ Downloaded by @YourBotName"
            )
        
        os.remove(video_file)
    except Exception as e:
        await update.message.reply_text("😢 Failed to Download. Check Link or Try Later.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""🌟 Welcome to Terabox Downloader Bot!
Send any Terabox video link to download.""")

def main():
    # Create application without timezone (fix the error)
    application = Application.builder().token(TOKEN).build()
    
    # Set timezone for job queue (যদি Cron Job ব্যবহার করেন)
    application.job_queue.scheduler.configure(timezone=pytz.timezone("Asia/Dhaka"))
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start bot
    application.run_polling()

if __name__ == "__main__":
    main()
