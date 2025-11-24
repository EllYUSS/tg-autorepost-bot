import os
import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.utils.exceptions import RetryAfter, TelegramAPIError

# ===== ENV VARIABLES =====
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Теперь тут можно указать несколько SOURCE_ID через запятую
# Например: SOURCE_IDS="-100111,-100222,-100333"
_raw_source_ids = os.getenv("SOURCE_IDS", "")
SOURCE_CHANNEL_IDS = {int(x.strip()) for x in _raw_source_ids.split(",") if x.strip()}  # set()

TARGET_CHANNEL_ID = int(os.getenv("TARGET_ID"))

# ===== LOGGING =====
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Временное хранение сообщений альбомов: {media_group_id: [Message, ...]}
_media_groups = {}

ALBUM_WAIT_SEC = 0.7


@dp.channel_post_handler(content_types=types.ContentTypes.ANY)
async def handle_channel_post(message: types.Message):
    try:
        # Принимаем сообщения только из списка источников
        if message.chat.id not in SOURCE_CHANNEL_IDS:
            return

        # Если сообщение принадлежит альбому
        if message.media_group_id:
            mg_id = message.media_group_id

            buf = _media_groups.setdefault(mg_id, [])
            buf.append(message)

            await asyncio.sleep(ALBUM_WAIT_SEC)

            if mg_id in _media_groups:
                parts = _media_groups.pop(mg_id)
                parts.sort(key=lambda m: m.message_id)

                for part in parts:
                    await _forward_with_retry(part)

                logging.info(f"Forwarded media group {mg_id} with {len(parts)} items")

        else:
            # обычное сообщение
            await _forward_with_retry(message)
            logging.info(f"Forwarded single message {message.message_id}")

    except Exception as e:
        logging.exception(f"Unhandled error in channel_post handler: {e}")


async def _forward_with_retry(message: types.Message, max_retries: int = 3):
    attempt = 0
    while attempt < max_retries:
        try:
            await bot.forward_message(
                chat_id=TARGET_CHANNEL_ID,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
            return
        except RetryAfter as e:
            wait = e.timeout if hasattr(e, "timeout") else 1
            logging.warning(f"RetryAfter: sleeping {wait} seconds (attempt {attempt+1})")
            await asyncio.sleep(wait + 0.5)
            attempt += 1
        except TelegramAPIError as e:
            logging.error(f"TelegramAPIError on forward (attempt {attempt+1}): {e}")
            await asyncio.sleep(1 + attempt)
            attempt += 1
        except Exception as e:
            logging.exception(f"Unexpected error while forwarding message {message.message_id}: {e}")
            break

    logging.error(f"Failed to forward message {message.message_id} after {max_retries} attempts")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
