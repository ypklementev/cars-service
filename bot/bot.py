from aiogram import Bot, Dispatcher
from aiogram.types import Message
import asyncio
import requests
from dotenv import load_dotenv
import os

from llm import extract_filters

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

BACKEND_URL = os.getenv("API_URL_BOT")


@dp.message()
async def search(message: Message):

    text = message.text

    # сообщение-заглушка
    waiting = await message.answer("🔍 Ищу автомобили...")

    try:
        filters = extract_filters(text)

        print("LLM filters:", filters)

        cars = requests.get(
            BACKEND_URL,
            params=filters
        ).json()

        if not isinstance(cars, list):
            await waiting.edit_text("⚠️ Ошибка backend")
            print(cars)
            return

        if not cars:
            await waiting.edit_text("Ничего не найдено")
            return

        result = "\n\n".join(
            f"{c['brand']} {c['model']}\n"
            f"Year: {c['year']}\n"
            f"Price: ¥{c['price']}\n"
            f"{c['url']}"
            for c in cars[:10]
        )

        await waiting.edit_text(result)

    except Exception as e:
        print(e)
        await waiting.edit_text("⚠️ Ошибка поиска")


async def main():
    await dp.start_polling(bot)


asyncio.run(main())