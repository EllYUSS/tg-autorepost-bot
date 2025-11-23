from aiogram import Bot, Dispatcher
from aiogram.utils.executor import start_webhook
import os

TOKEN = "8452605972:AAH32IFCrVYG-lvmNhm3zsjQ-I_Hxqzkwpg"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://worker-production-abb5.up.railway.app{WEBHOOK_PATH}"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.environ.get("PORT", 8000))  # Railway автоматически даёт порт

async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook установлен: {WEBHOOK_URL}")

start_webhook(
    dispatcher=dp,
    webhook_path=WEBHOOK_PATH,
    on_startup=on_startup,
    host=WEBAPP_HOST,
    port=WEBAPP_PORT,
)
