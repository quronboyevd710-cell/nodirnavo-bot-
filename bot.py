import asyncio
import logging
import os
import re
import shutil
import tempfile

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, Message
from yt_dlp import YoutubeDL

TOKEN = os.getenv("BOT_TOKEN")  # @BotFather bergan token
MAX_SIZE = 50 * 1024 * 1024  # Telegram bot limiti: 50 MB

URL_RE = re.compile(
    r"https?://(?:www\.|m\.)?(?:youtube\.com|youtu\.be|instagram\.com)/\S+"
)

bot = Bot(TOKEN)
dp = Dispatcher()


def download(url: str, folder: str) -> str:
    opts = {
        "outtmpl": f"{folder}/%(id)s.%(ext)s",
        "format": "bv*[height<=720]+ba/b[height<=720]/b",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "max_filesize": MAX_SIZE,
    }
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return info["requested_downloads"][0]["filepath"]


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Salom! YouTube yoki Instagram havolasini yuboring, "
        "men videoni yuklab beraman."
    )


@dp.message()
async def handle_link(message: Message):
    match = URL_RE.search(message.text or "")
    if not match:
        await message.answer("Iltimos, YouTube yoki Instagram havolasini yuboring.")
        return

    status = await message.answer("⏳ Yuklanmoqda...")
    folder = tempfile.mkdtemp()
    try:
        path = await asyncio.to_thread(download, match.group(0), folder)
        if os.path.getsize(path) > MAX_SIZE:
            await status.edit_text("❌ Video 50 MB dan katta, yuborib bo'lmaydi.")
            return
        await message.answer_video(FSInputFile(path))
        await status.delete()
    except Exception as e:
        logging.exception("Yuklashda xato")
        await status.edit_text(f"❌ Yuklab bo'lmadi.\n\nSabab: {str(e)[:300]}")
    finally:
        shutil.rmtree(folder, ignore_errors=True)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
