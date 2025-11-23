from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import logging
import asyncio

API_TOKEN = '8452605972:AAH32IFCrVYG-lvmNhm3zsjQ-I_Hxqzkwpg'
SOURCE_CHANNEL_ID = '-1002913212827'  # канал, откуда берём посты
TARGET_CHANNEL_ID = '-1003248459795'  # канал, куда репостим

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.channel_post_handler()  # ловим новые сообщения в канале, где бот админ
async def repost_message(message: types.Message):
    try:
        await bot.forward_message(
            chat_id=TARGET_CHANNEL_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        logging.info(f"Репост успешен: {message.message_id}")
    except Exception as e:
        logging.error(f"Ошибка при репосте: {e}")

if __name__ == '__main__':
    # запуск бота
    executor.start_polling(dp, skip_updates=True)