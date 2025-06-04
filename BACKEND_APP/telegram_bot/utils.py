import aiohttp
import logging
from aiogram import types
from aiogram.fsm.context import FSMContext

from telegram_bot import config

logger = logging.getLogger(__name__)

async def make_api_request(method, endpoint, data=None, headers=None, payload=None):
    url = f"{config.API_URL}{endpoint}"

    logger.info(f"Запрос на {url}")
    logger.info(f"Данные {data}")

    headers = headers.copy() if headers else {}

    try:
        async with aiohttp.ClientSession() as session:
            if method == "GET":
                async with session.get(url, headers=headers)as resp:
                    data = await resp.json()
                    return data, None if resp.status < 400 else data
            elif method == "POST":
                async with session.post(url, headers=headers, json=data) as resp:
                    data = await resp.json()
                    return data, None if resp.status < 400 else data

    except Exception as e:
        return None, str(e)



async def send_error_message(message: types.Message, error: str):
    await message.reply(f"Ошибка: {error}")