from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import logging

API_TOKEN = '8452605972:AAH32IFCrVYG-lvmNhm3zsjQ-I_Hxqzkwpg'
SOURCE_CHANNEL = -1002913212827
TARGET_CHANNEL = -1003248459795

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.channel_post_handler()
async def repost_message(message: types.Message):
    try:
        if message.text:
            await bot.send_message(TARGET_CHANNEL, message.text)
        elif message.photo:
            photo = message.photo[-1]
            caption = message.caption or ""
            await bot.send_photo(TARGET_CHANNEL, photo.file_id, caption=caption)
        elif message.video:
            caption = message.caption or ""
            await bot.send_video(TARGET_CHANNEL, message.video.file_id, caption=caption)
        elif message.document:
            caption = message.caption or ""
            await bot.send_document(TARGET_CHANNEL, message.document.file_id, caption=caption)
        else:
            logging.info("Неизвестный тип сообщения, пропускаем")
    except Exception as e:
        logging.error(f"Ошибка при репосте: {e}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
