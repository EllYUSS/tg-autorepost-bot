import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = "8335085716:AAEdtHlmC09U9xcWZMziFNQnzp-EUn67d5A"
SOURCE_CHANNEL_ID = -1002913212827
TARGET_CHANNEL_ID = -1003248459795

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.channel_post_handler()
async def repost_message(message: types.Message):
    try:
        # copy_message копирует ВСЕ типы постов, включая фото, видео, альбом, файлы, гифки
        await bot.copy_message(
            chat_id=TARGET_CHANNEL_ID,
            from_chat_id=SOURCE_CHANNEL_ID,
            message_id=message.message_id
        )
        logging.info(f"Скопировано: {message.message_id}")

    except Exception as e:
        logging.error(f"Ошибка при копировании: {e}")