
import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram import executor
from aiohttp import web

# Получаем токен
API_TOKEN = os.getenv("BOT_TOKEN")

print("TOKEN:", API_TOKEN)
print("Working directory:", os.getcwd())
print("Files:", os.listdir())

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Railway выдаёт домен в переменной окружения
WEBHOOK_HOST = os.getenv("RAILWAY_PUBLIC_DOMAIN")  # например https://mybot.up.railway.app
WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 8080))

# Статистика — только в /tmp
STATS_PATH = "/tmp/stats.json"

try:
    with open(STATS_PATH, "r") as f:
        stats = json.load(f)
except:
    stats = {"total": 0, "countries": {}}


def save_stats():
    with open(STATS_PATH, "w") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(
            text="Открыть квиз 💙",
            web_app=types.WebAppInfo(url="https://frontside-seven.vercel.app/")
        )
    )

    await message.answer(
        "Привет! Готов пройти романтичный travel‑квиз? Нажми кнопку ниже 👇",
        reply_markup=kb
    )


@dp.message_handler(content_types=['web_app_data'])
async def web_app_data_handler(message: types.Message):
    data = json.loads(message.web_app_data.data)
    result = data.get("result")

    stats["total"] += 1
    stats["countries"][result] = stats["countries"].get(result, 0) + 1

    save_stats()

    await message.answer(f"Спасибо! Я получил твой результат: {result}")


@dp.message_handler(commands=['stats'])
async def stats_cmd(message: types.Message):
    text = f"📊 Статистика квиза:\n\n"
    text += f"Всего прохождений: {stats['total']}\n\n"
    text += "Популярность стран:\n"

    for country, count in stats["countries"].items():
        text += f"— {country}: {count}\n"

    await message.answer(text)


# -----------------------------
#       WEBHOOK MODE
# -----------------------------

async def on_startup(dp):
    print("Setting webhook:", WEBHOOK_URL)
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(dp):
    print("Deleting webhook")
    await bot.delete_webhook()


if __name__ == '__main__':
    executor.start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
