import re
import os
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

# .env ফাইল থেকে টোকেন লোড করুন
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# টেরাবক্সের জন্য হেডার (ব্রাউজার সিমুলেশন)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://www.terabox.com/",
}

async def download_video(url: str) -> bytes:
    """ভিডিও ডাউনলোড করে মেমোরিতে রিটার্ন করে"""
    try:
        # রিডাইরেক্ট হ্যান্ডলিং
        response = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=15)
        final_url = response.url
        
        # ভিডিও কন্টেন্ট ডাউনলোড
        video_response = requests.get(final_url, headers=HEADERS, stream=True, timeout=30)
        video_response.raise_for_status()
        
        # মেমোরিতে ভিডিও কন্টেন্ট সংগ্রহ
        video_content = b""
        for chunk in video_response.iter_content(chunk_size=1024*1024):
            if chunk:
                video_content += chunk
        return video_content
    
    except Exception as e:
        print(f"Download Error: {e}")
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """মেসেজ হ্যান্ডলিং (কোন ফাইল সিস্টেম ব্যবহার ছাড়াই)"""
    text = update.message.text
    
    # টেরাবক্স লিংক ডিটেক্ট
    video_urls = re.findall(
        r'(https?://(?:www\.)?(?:terabox\.com|terafileshare\.com|terabox\.app)/\S+)', 
        text, 
        re.IGNORECASE
    )
    
    if not video_urls:
        await update.message.reply_text("❌ Invalid TeraBox Link!")
        return
    
    status_msg = await update.message.reply_text("📥 Downloading...")
    
    try:
        video_content = await download_video(video_urls[0])
        if not video_content:
            raise Exception("Download failed")
        
        # সরাসরি মেমোরি থেকে ভিডিও সেন্ড করুন
        await update.message.reply_video(
            video=video_content,
            caption="⬇️ Downloaded by @YourBotName",
            reply_to_message_id=update.message.message_id,
            read_timeout=200,
            write_timeout=200
        )
        await status_msg.delete()
        
    except Exception as e:
        print(f"Error: {e}")
        await status_msg.edit_text("😢 Failed to download. Check link or try later.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """স্টার্ট কমান্ড হ্যান্ডলার"""
    await update.message.reply_text(
        "🌟 Welcome to TeraBox Direct Download Bot!\n"
        "Send any TeraBox link to get instant video."
    )

def main():
    """বট চালু করুন"""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    main()
