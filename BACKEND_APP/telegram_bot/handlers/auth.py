from aiogram import Router, types
from aiogram.filters import Command

from telegram_bot import config
from telegram_bot.utils import make_api_request, send_error_message

import logging

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command('start'))
async def start(message: types.Message):
    await message.reply(
        "Команды:\n"
        "/login - Авторизация\n"
        "/add_batch - Добавить партию\n"
        "/add_subbatch - Добавить подпартию\n"
        "/add_employee - Добавить сотрудника\n"
        "/add_client - Добавить клиента\n"
        "/add_order - Добавить заказ\n"
        "/add_order_item - Добавить позицию заказа\n"
        "/add_payment - Добавить платёж\n"
        "/report_production - Отчёт по производству\n"
        "/report_orders - Отчёт по заказам"
    )

@router.message(Command('login'))
async def login(message: types.Message):
    logger.info(f"{types.Message} - СМС от ЮЗЕРА")
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Введите /login <username>")
        return
    username = args[1]
    data = {'username': username, 'telegram_id': str(message.from_user.id)}
    print(f"Данные тг ЮЗЕРА - {data}")
    result, error = await make_api_request('POST', 'auth/verify-telegram/', data, config.API_TOKEN)
    print(config.API_TOKEN)
    if error:
        await send_error_message(message, error)
    else:
        await message.reply("Авторизация успешна!")