import aiohttp
import logging
from aiogram import types

from telegram_bot import config

logger = logging.getLogger(__name__)

async def make_api_request(method, endpoint, data=None, token=None):
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.request(method, f"{config.API_URL}{endpoint}", json=data, headers=headers) as response:
                if response.status >= 400:
                    text = await response.text()
                    logger.error(f"API error: {response.status} {await response.text()}")
                    return None, f"Error {response.status}"
                try:
                    result = await response.json()
                except Exception:
                    text = await response.text()
                    logger.error(f"Ошибка разбора JSON: {text}")
                    return None, "Ошибка: не удалось прочитать JSON-ответ"

                logger.info(f"API {method} {endpoint} success: {result}")
                return result, None
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            return None, str(e)

async def send_error_message(message: types.Message, error: str):
    await message.reply(f"Ошибка: {error}")