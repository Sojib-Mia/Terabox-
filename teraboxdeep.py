import os
import requests
from telegram import Bot, Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv
import re

# .env ফাইল থেকে টোকেন লোড করুন
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# টেরাবক্সের জন্য প্রয়োজনীয় হেডার
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://www.terabox.com/"
}

def download_video(url):
    try:
        response = requests.get(url, headers=HEADERS, stream=True, timeout=10)
        response.raise_for_status()
        
        filename = f"video_{len(os.listdir('downloads')) + 1}.mp4"
        with open(f"downloads/{filename}", 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024*1024):
                if chunk:
                    file.write(chunk)
        return filename
    except Exception as e:
        print(f"Download Error: {e}")
        return None

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    video_urls = re.findall(r'https?://terabox[^\s]+', text)
    
    if not video_urls:
        update.message.reply_text("❌ Invalid TeraBox Link!")
        return
    
    update.message.reply_text("📥 Downloading... (10-30 seconds)")
    
    try:
        video_file = download_video(video_urls[0])
        if not video_file:
            raise Exception("Download Failed")
        
        with open(f"downloads/{video_file}", 'rb') as video:
            update.message.reply_video(video, timeout=100)
        
        # ফাইল ডিলিট করুন (ঐচ্ছিক)
        os.remove(f"downloads/{video_file}")
        update.message.reply_text("✅ Video Sent Successfully!")
    except Exception as e:
        update.message.reply_text("😢 Failed to Download. Check Link or Try Later.")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    main()