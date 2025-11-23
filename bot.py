import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook
import os

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8452605972:AAH32IFCrVYG-lvmNhm3zsjQ-I_Hxqzkwpg"
SOURCE_CHANNEL = -1002913212827
TARGET_CHANNEL = -1003248459795

WEBHOOK_HOST = "https://worker-production-abb5.up.railway.app"
WEBHOOK_PATH = "/"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = "0.0.0.0"  # Railway использует этот хост
WEBAPP_PORT = int(os.environ.get("PORT", 8000))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Обработчик новых постов в канале
@dp.channel_post_handler(lambda message: message.chat.id == SOURCE_CHANNEL)
async def repost_channel_post(message: types.Message):
    # Репостим пост в целевой канал
    await bot.copy_message(
        chat_id=TARGET_CHANNEL,
        from_chat_id=SOURCE_CHANNEL,
        message_id=message.message_id
    )

async def on_startup(dispatcher):
    # Устанавливаем webhook
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook установлен: {WEBHOOK_URL}")

async def on_shutdown(dispatcher):
    # Убираем webhook при остановке
    logging.info("Удаляем webhook...")
    await bot.delete_webhook()

if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
