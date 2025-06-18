import os
import sys
import django
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from decouple import config
from asgiref.sync import sync_to_async
import yt_dlp
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from core.models import TelegramUser
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "downloaded_audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

FFMPEG_DIR = os.path.join(os.path.dirname(__file__), "ffmpeg") 
FFMPEG_EXE = os.path.join(FFMPEG_DIR, "ffmpeg.exe")  

@sync_to_async
def register_user(username):
    TelegramUser.objects.get_or_create(username=username)

@sync_to_async
def get_user_by_username(username):
    try:
        return TelegramUser.objects.get(username=username)
    except TelegramUser.DoesNotExist:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username or f"tg_user_{user.id}"
    await register_user(username)
    await update.message.reply_text(f'👋 Hello {username}, you are registered!')

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username or f"tg_user_{user.id}"
    db_user = await get_user_by_username(username)

    if db_user:
        message = (
            f"*Profile Information:*\n"
            f"Username: `{db_user.username}`\n"
            f"Email: `{db_user.email or 'Not set'}`\n"
            f"Joined: `{db_user.created_at.strftime('%Y-%m-%d %H:%M:%S')}`"
        )
    else:
        message = "You are not registered yet. Use /start to register."

    await update.message.reply_text(message, parse_mode="Markdown")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Please provide a YouTube URL or search query.")
        return

    query = " ".join(context.args)
    file_path = await download_audio(query)

    if file_path and os.path.exists(file_path):
        await update.message.reply_audio(audio=open(file_path, 'rb'))
        os.remove(file_path)  # cleanup
    else:
        await update.message.reply_text("Sorry,Failed to download audio.") 
async def download_audio(query):
    filename_template = os.path.join(AUDIO_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': filename_template,
        'noplaylist': True,
        'quiet': True,
        'ffmpeg_location': FFMPEG_DIR,
        'default_search': 'ytsearch',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    loop = asyncio.get_event_loop()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(query, download=True))
            if 'entries' in info:
                info = info['entries'][0]

            # Now find the mp3 path safely
            mp3_path = None
            if 'requested_downloads' in info:
                for file_info in info['requested_downloads']:
                    if file_info.get('ext') == 'mp3':
                        mp3_path = file_info.get('filepath')
                        break

            if not mp3_path:
                mp3_path = ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"

            print(f"[DEBUG] Downloaded file path: {mp3_path}")
            return mp3_path

    except Exception as e:
        import traceback
        print("Download failed:", e)
        traceback.print_exc()
        return None

def run():
    bot_token = config('TELEGRAM_BOT_TOKEN')
    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("play", play))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    run()
