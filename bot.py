import os
import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.utils.exceptions import RetryAfter, TelegramAPIError

# ===== ENV VARIABLES =====
BOT_TOKEN = os.getenv("BOT_TOKEN")            # токен бота
SOURCE_CHANNEL_ID = int(os.getenv("SOURCE_ID"))  # -100...
TARGET_CHANNEL_ID = int(os.getenv("TARGET_ID"))  # -100...

# ===== LOGGING =====
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Временное хранение сообщений альбомов: {media_group_id: [Message, ...]}
_media_groups = {}

# Время ожидания, чтобы собрать все части альбома (в секундах)
ALBUM_WAIT_SEC = 0.7


@dp.channel_post_handler(content_types=types.ContentTypes.ANY)
async def handle_channel_post(message: types.Message):
    try:
        # Принимаем сообщения только из нужного источника (доп. защита)
        if message.chat.id != SOURCE_CHANNEL_ID:
            return

        # Если сообщение принадлежит media_group (альбом)
        if message.media_group_id:
            mg_id = message.media_group_id

            # добавляем в буфер
            buf = _media_groups.setdefault(mg_id, [])
            buf.append(message)

            # маленькая задержка чтобы собрать элементы альбома (один раз после первого элемента)
            # если несколько сообщений приходят почти одновременно — они попадут в один буфер
            await asyncio.sleep(ALBUM_WAIT_SEC)

            # после ожидания — если буфер есть, пересылаем все части по порядку message_id
            if mg_id in _media_groups:
                parts = _media_groups.pop(mg_id)
                parts.sort(key=lambda m: m.message_id)  # сохраняем порядок

                for part in parts:
                    await _forward_with_retry(part)

                logging.info(f"Forwarded media group {mg_id} with {len(parts)} items")

        else:
            # одиночное сообщение — просто форвардим
            await _forward_with_retry(message)
            logging.info(f"Forwarded single message {message.message_id}")

    except Exception as e:
        logging.exception(f"Unhandled error in channel_post handler: {e}")


async def _forward_with_retry(message: types.Message, max_retries: int = 3):
    """
    Форвард с обработкой RetryAfter (flood) и других ошибок.
    """
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
            # неполадка API — логируем и пробуем ещё пару раз
            logging.error(f"TelegramAPIError on forward (attempt {attempt+1}): {e}")
            await asyncio.sleep(1 + attempt)
            attempt += 1
        except Exception as e:
            logging.exception(f"Unexpected error while forwarding message {message.message_id}: {e}")
            # не повторяем бесконечно — выходим
            break

    logging.error(f"Failed to forward message {message.message_id} after {max_retries} attempts")


if __name__ == "__main__":
    # Запускаем polling; skip_updates=True чтобы не обрабатывать старые апдейты после рестартов
    executor.start_polling(dp, skip_updates=True)