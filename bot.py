import yt_dlp
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
import re

# 🔐 Replace with your NEW bot token (regenerate from BotFather)
BOT_TOKEN = "Your Bot Token"


# 🎯 Extract playlist videos
def get_playlist_videos(playlist_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)

        if 'entries' not in info:
            raise Exception("Invalid playlist or no videos found")

        videos = []
        for entry in info['entries']:
            if entry:
                title = entry.get('title', 'No Title')
                video_id = entry.get('id')
                url = f"https://www.youtube.com/watch?v={video_id}"
                videos.append((title, url))

        playlist_title = info.get('title', 'playlist')
        return videos, playlist_title


# 🧹 Clean filename
def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)


# 🚀 /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Send a YouTube playlist link")


# 📩 Handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "list=" not in url:
        await update.message.reply_text("❌ Please send a valid YouTube playlist link")
        return

    await update.message.reply_text("⏳ Fetching playlist...")

    try:
        videos, playlist_title = get_playlist_videos(url)

        if not videos:
            await update.message.reply_text("❌ Playlist is empty")
            return

        safe_name = sanitize_filename(playlist_title)
        file_name = f"{safe_name}.txt"

        # ✨ FINAL FORMAT (Title : Link in same line)
        with open(file_name, "w", encoding="utf-8") as f:
            for i, (title, link) in enumerate(videos, 1):
                f.write(f"{i}. {title} : {link}\n")

        # 📤 Send file
        with open(file_name, "rb") as f:
            await update.message.reply_document(
                document=InputFile(f),
                filename=file_name
            )

        os.remove(file_name)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


# ▶️ Run bot
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("✅ Bot is running...")
app.run_polling()
