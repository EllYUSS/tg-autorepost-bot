import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook

TOKEN = "8452605972:AAH32IFCrVYG-lvmNhm3zsjQ-I_Hxqzkwpg"

# --- Настройки вебхука ---
WEBHOOK_PATH = "/webhook"
RAILWAY_URL = "https://worker-production-abb5.up.railway.app"
WEBHOOK_URL = f"{RAILWAY_URL}{WEBHOOK_PATH}"

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.environ.get("PORT", 8000))  # Railway сам назначает порт

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# --- Хендлер, который отвечает на любое сообщение ---
@dp.message_handler()
async def echo(message: types.Message):
    await message.reply(f"Привет! Ты написал: {message.text}")

# --- Функция старта вебхука ---
async def on_startup(dispatcher):
    # Устанавливаем webhook
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook установлен: {WEBHOOK_URL}")

async def on_shutdown(dispatcher):
    # Убираем webhook при остановке
    await bot.delete_webhook()
    print("Webhook удалён")

# --- Запуск вебхука ---
if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
