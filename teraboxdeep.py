import os
import re
import requests
from telegram import Bot, Update
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)
from dotenv import load_dotenv

# .env ফাইল থেকে টোকেন লোড করুন
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# ডাউনলোড ফোল্ডার তৈরি করুন
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# টেরাবক্সের জন্য হেডার
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
        
        # ভিডিও সেন্ড করুন
        with open(video_file, 'rb') as video:
            await update.message.reply_video(video, read_timeout=100, write_timeout=100)
        
        # ফাইল ডিলিট করুন
        os.remove(video_file)
        await update.message.reply_text("✅ Video Sent Successfully!")
    except Exception as e:
        await update.message.reply_text("😢 Failed to Download. Check Link or Try Later.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me a TeraBox link to download.")

def main():
    # বট অ্যাপ্লিকেশন তৈরি করুন
    application = Application.builder().token(TOKEN).build()
    
    # মেসেজ হ্যান্ডলার
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # স্টার্ট কমান্ড
    application.add_handler(CommandHandler("start", start))
    
    # বট চালু করুন
    application.run_polling()

if __name__ == "__main__":
    main()
