from aiogram import Bot, Dispatcher
from aiogram.types import Message
import asyncio
import requests
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message()
async def search(message: Message):

    text = message.text

    params = {}

    if "bmw" in text.lower():
        params["brand"] = "BMW"

    cars = requests.get("http://backend:8000/api/cars").json()

    result = "\n".join(
        f"{c['brand']} {c['model']} {c['price']}"
        for c in cars
    )

    await message.answer(result or "Ничего не найдено")


async def main():
    await dp.start_polling(bot)


asyncio.run(main())