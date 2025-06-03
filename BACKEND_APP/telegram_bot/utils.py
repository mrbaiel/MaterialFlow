import aiohttp
import logging
from aiogram import types
from aiogram.fsm.context import FSMContext

from telegram_bot import config

logger = logging.getLogger(__name__)

async def make_api_request(method, endpoint, data=None):
    url = f"{config.API_URL}{endpoint}"

    logger.info(f"Запрос на {url}")
    logger.info(f"Данные {data}")


    async with aiohttp.ClientSession() as session:
        try:
            async with session.request(method, url, json=data) as response:
                text = await response.text()

                if response.status >= 400:
                    logger.error(f"[{response.status}] {method} {url} — {text}")
                    return None, f"Ошибка API: {response.status}"

                try:
                    result = await response.json()
                    logger.info(f"{method} {url} — успешно: {result}")
                    return result, None
                except Exception:
                    logger.error(f"{method} {url} — не JSON: {text}")
                    return None, "Ошибка: ответ не является JSON"
        except Exception as e:
            logger.error(f"Сбой запроса к API: {str(e)}")
            return None, f"Сбой соединения: {str(e)}"


async def send_error_message(message: types.Message, error: str):
    await message.reply(f"Ошибка: {error}")