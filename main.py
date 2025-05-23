import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Replace with your bot token
TOKEN = "7639302300:AAEVm5QiwmV7gYy8HE6JkiQ1IJyiBcjHQxA"

# yt-dlp options for audio download
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': True,
    'no_warnings': True,
    'noplaylist': True
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! Send me a song name or YouTube link and I'll send you the audio!"
    )

async def download_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    chat_id = update.message.chat_id

    await update.message.reply_text(f"Searching YouTube for: *{query}*", parse_mode="Markdown")

    os.makedirs("downloads", exist_ok=True)

    try:
        # Search YouTube using ytsearch1:query (get first result only)
        search_url = f"ytsearch1:{query}"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_url, download=True)
            if 'entries' in info:
                info = info['entries'][0]  # Get first result

            filename = ydl.prepare_filename(info)
            audio_file = os.path.splitext(filename)[0] + ".mp3"

        with open(audio_file, "rb") as f:
            await context.bot.send_audio(chat_id=chat_id, audio=f, title=info.get('title', 'Audio'))

        os.remove(audio_file)

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_song))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
