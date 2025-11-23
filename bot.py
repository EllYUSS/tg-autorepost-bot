import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = '8452605972:AAH32IFCrVYG-lvmNhm3zsjQ-I_Hxqzkwpg'
SOURCE_CHANNEL = -1001234567890  # канал-источник
TARGET_CHANNEL = -1009876543210  # канал-приёмник

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Репост одиночных сообщений
@dp.channel_post_handler()
async def repost_message(message: types.Message):
    try:
        if message.text:
            await bot.send_message(TARGET_CHANNEL, message.text)
        elif message.photo:
            await bot.send_photo(TARGET_CHANNEL, message.photo[-1].file_id, caption=message.caption)
        elif message.video:
            await bot.send_video(TARGET_CHANNEL, message.video.file_id, caption=message.caption)
        elif message.document:
            await bot.send_document(TARGET_CHANNEL, message.document.file_id, caption=message.caption)
    except Exception as e:
        logging.error(f"Ошибка при репосте: {e}")

# Репост альбомов (media_group)
media_groups = {}

@dp.channel_post_handler(content_types=types.ContentType.ANY)
async def repost_media_group(message: types.Message):
    if not message.media_group_id:
        return

    group_id = message.media_group_id
    if group_id not in media_groups:
        media_groups[group_id] = []

    if message.photo:
        media_groups[group_id].append(types.InputMediaPhoto(message.photo[-1].file_id, caption=message.caption))
    elif message.video:
        media_groups[group_id].append(types.InputMediaVideo(message.video.file_id, caption=message.caption))
    elif message.document:
        media_groups[group_id].append(types.InputMediaDocument(message.document.file_id, caption=message.caption))

    import asyncio
    await asyncio.sleep(1)

    if media_groups.get(group_id):
        try:
            await bot.send_media_group(TARGET_CHANNEL, media_groups[group_id])
        except Exception as e:
            logging.error(f"Ошибка при репосте альбома: {e}")
        finally:
            media_groups.pop(group_id, None)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
