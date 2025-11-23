import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import asyncio

logging.basicConfig(level=logging.INFO)

# ====== Настройки ======
BOT_TOKEN = "8452605972:AAH32IFCrVYG-lvmNhm3zsjQ-I_Hxqzkwpg"
SOURCE_CHANNEL_ID = -1002913212827
TARGET_CHANNEL_ID = -1003248459795

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ====== Хранение медиа-групп ======
media_groups = {}

# ====== Обработчик медиа-групп ======
@dp.channel_post_handler(lambda msg: msg.chat.id == SOURCE_CHANNEL_ID and msg.media_group_id)
async def repost_media_group(message: types.Message):
    group_id = message.media_group_id
    if group_id not in media_groups:
        media_groups[group_id] = []
    media_groups[group_id].append(message)

    # Проверяем, все ли сообщения группы собраны (задержка 1 сек)
    await asyncio.sleep(1)

    if len(media_groups[group_id]) == len(set(m.message_id for m in media_groups[group_id])):
        media = []
        for msg in sorted(media_groups[group_id], key=lambda x: x.message_id):
            if msg.photo:
                media.append(types.InputMediaPhoto(msg.photo[-1].file_id, caption=msg.caption))
            elif msg.video:
                media.append(types.InputMediaVideo(msg.video.file_id, caption=msg.caption))
        if media:
            await bot.send_media_group(TARGET_CHANNEL_ID, media=media)
        media_groups.pop(group_id, None)

# ====== Обработчик одиночных сообщений ======
@dp.channel_post_handler(lambda msg: msg.chat.id == SOURCE_CHANNEL_ID and not msg.media_group_id)
async def repost_single_message(message: types.Message):
    try:
        if message.text:
            await bot.send_message(TARGET_CHANNEL_ID, message.text)
        elif message.photo:
            await bot.send_photo(TARGET_CHANNEL_ID, message.photo[-1].file_id, caption=message.caption)
        elif message.video:
            await bot.send_video(TARGET_CHANNEL_ID, message.video.file_id, caption=message.caption)
        elif message.document:
            await bot.send_document(TARGET_CHANNEL_ID, message.document.file_id, caption=message.caption)
        elif message.sticker:
            await bot.send_sticker(TARGET_CHANNEL_ID, message.sticker.file_id)
        elif message.audio:
            await bot.send_audio(TARGET_CHANNEL_ID, message.audio.file_id, caption=message.caption)
        elif message.voice:
            await bot.send_voice(TARGET_CHANNEL_ID, message.voice.file_id, caption=message.caption)
        logging.info(f"Reposted message {message.message_id}")
    except Exception as e:
        logging.error(f"Failed to repost message {message.message_id}: {e}")

# ====== Запуск ======
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
