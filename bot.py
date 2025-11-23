# bot.py
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook

API_TOKEN = "8452605972:AAH32IFCrVYG-lvmNhm3zsjQ-I_Hxqzkwpg"

SOURCE_CHANNEL = -1002913212827
TARGET_CHANNEL = -1003248459795

WEBHOOK_URL = "https://worker-production-abb5.up.railway.app/"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = 8080

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.channel_post_handler()
async def repost_channel_post(message: types.Message):
    if message.chat.id != SOURCE_CHANNEL:
        return

    # --- Репост текста ---
    if message.text:
        await bot.send_message(TARGET_CHANNEL, message.text)

    # --- Репост фото ---
    if message.photo:
        photo = message.photo[-1]
        await bot.send_photo(TARGET_CHANNEL, photo.file_id, caption=message.caption or "")

    # --- Репост видео ---
    if message.video:
        await bot.send_video(TARGET_CHANNEL, message.video.file_id, caption=message.caption or "")

    # --- Репост документов ---
    if message.document:
        await bot.send_document(TARGET_CHANNEL, message.document.file_id, caption=message.caption or "")

    # --- Репост анимаций (GIF) ---
    if message.animation:
        await bot.send_animation(TARGET_CHANNEL, message.animation.file_id, caption=message.caption or "")

    # --- Репост аудио ---
    if message.audio:
        await bot.send_audio(TARGET_CHANNEL, message.audio.file_id, caption=message.caption or "")

    # --- Репост голосовых сообщений ---
    if message.voice:
        await bot.send_voice(TARGET_CHANNEL, message.voice.file_id, caption=message.caption or "")


async def on_startup(dispatcher):
    logging.info("Удаляем старый webhook...")
    await bot.delete_webhook()
    logging.info("Устанавливаем webhook...")
    await bot.set_webhook(WEBHOOK_URL)


if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path="/",
        skip_updates=True,
        on_startup=on_startup,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
