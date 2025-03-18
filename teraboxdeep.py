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

# .env ফাইল থেকে টোকেন লোড করুন
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# ডাউনলোড ফোল্ডার তৈরি করুন
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# টেরাবক্সের জন্য হেডার (ব্রাউজার সিমুলেশন)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://www.terabox.com/",
    "Accept-Language": "en-US,en;q=0.9",
}

def get_redirected_url(url: str) -> str:
    """রিডাইরেক্ট লিংক রিজল্ভ করে"""
    try:
        response = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=15)
        return response.url
    except Exception as e:
        print(f"Redirect Error: {e}")
        return None

async def download_video(url: str) -> str:
    """ভিডিও ডাউনলোড করে ফাইলপাথে রিটার্ন করে"""
    try:
        direct_url = get_redirected_url(url)
        if not direct_url:
            return None
        
        response = requests.get(direct_url, headers=HEADERS, stream=True, timeout=30)
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
    """ইউজারের মেসেজ হ্যান্ডল করে"""
    text = update.message.text
    print(f"User sent: {text}")
    
    # সমস্ত টেরাবক্স ডোমেইন সনাক্ত করুন (case-insensitive)
    video_urls = re.findall(
        r'https?://(www\.)?(terabox\.com|terafileshare\.com|terabox\.app)[^\s]+', 
        text, 
        re.IGNORECASE
    )
    print(f"Found URLs: {video_urls}")
    
    if not video_urls:
        await update.message.reply_text("❌ Invalid TeraBox Link!")
        return
    
    # ডাউনলোডিং স্ট্যাটাস মেসেজ
    status_msg = await update.message.reply_text("📥 Downloading... (10-30 seconds)")
    
    try:
        # প্রথম ম্যাচ করা লিংক নিন
        video_url = video_urls[0][1] if video_urls[0][0] else video_urls[0][1]
        video_file = await download_video(video_url)
        
        if not video_file:
            await status_msg.edit_text("😢 Failed to Download. Check Link or Try Later.")
            return
        
        # ভিডিও রিপ্লাই হিসেবে পাঠান + স্ট্যাটাস মেসেজ ডিলিট করুন
        with open(video_file, 'rb') as video:
            await update.message.reply_video(
                video,
                caption="⬇️ Downloaded by @YourBotName",
                reply_to_message_id=update.message.message_id,  # মূল মেসেজে রিপ্লাই
                read_timeout=200,
                write_timeout=200
            )
        await status_msg.delete()  # স্ট্যাটাস মেসেজ ডিলিট
        
        os.remove(video_file)
        
    except Exception as e:
        print(f"Error: {e}")
        await status_msg.edit_text("😢 Failed to Download. Check Link or Try Later.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start কমান্ড হ্যান্ডলার"""
    await update.message.reply_text(
        "🌟 Welcome to TeraBox Downloader Bot!\n"
        "Send any TeraBox/TeraFileshare link to download."
    )

def main():
    """বট চালু করুন"""
    application = Application.builder().token(TOKEN).build()
    
    # হ্যান্ডলার যোগ করুন
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # বট চালু করুন
    application.run_polling()

if __name__ == "__main__":
    main()
