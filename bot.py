import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import os

logging.basicConfig(level=logging.INFO)

TOKEN = "8452605972:AAH32IFCrVYG-lvmNhm3zsjQ-I_Hxqzkwpg"
SOURCE_CHAT = -1002913212827
TARGET_CHAT = -1003248459795

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.channel_post_handler(lambda message: message.chat.id == SOURCE_CHAT)
async def autorepost(message: types.Message):
    try:
        await bot.copy_message(
            chat_id=TARGET_CHAT,
            from_chat_id=SOURCE_CHAT,
            message_id=message.message_id
        )
        logging.info(f"Copied message {message.message_id}")
    except Exception as e:
        logging.exception("Failed to copy message: %s", e)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
