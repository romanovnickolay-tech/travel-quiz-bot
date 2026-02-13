import json
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = "8594199632:AAHEABnUdvfDj3zd6-Xpzh2cutUQ-GV7gGA"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Загружаем статистику или создаём новую
try:
    with open("stats.json", "r") as f:
        stats = json.load(f)
except:
    stats = {"total": 0, "countries": {}}


def save_stats():
    with open("stats.json", "w") as f:
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

    # увеличиваем общий счётчик
    stats["total"] += 1

    # считаем популярность стран
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


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
