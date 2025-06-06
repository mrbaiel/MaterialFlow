import re

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from telegram_bot.states import AddClientState
from telegram_bot.utils import make_api_request, send_error_message

router = Router()

@router.message(F.text.in_({"/add_client", "Добавить клиента"}))
async def add_client_start(message: types.Message, state: FSMContext):
    await message.reply("Введите имя клиента:")
    await state.set_state(AddClientState.first_name)

@router.message(AddClientState.first_name)
async def add_client_first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text.strip())
    await message.reply("Введите фамилию клиента:")
    await state.set_state(AddClientState.last_name)

@router.message(AddClientState.last_name)
async def add_client_last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text.strip())
    await message.reply("Введите номер телефона:")
    await state.set_state(AddClientState.phone)

@router.message(AddClientState.phone)
async def add_client_phone(message: types.Message, state:FSMContext):
    phone = message.text.strip()

    pattern = r"^(\+996\s?\d{3}\s?\d{3}\s?\d{3}|\d{3}\s?\d{3}\s?\d{3})$"
    if not re.fullmatch(pattern, phone):
        await message.reply("Неверный формат номера. Введите номер в формате:\n+996 999111222 или 700 800900")
        return

    await state.update_data(phone=message.text.strip())
    await message.reply("Введите адрес клиента:")
    await state.set_state(AddClientState.address)

@router.message(AddClientState.address)
async def add_client_address(message: types.Message, state:FSMContext):
    data = await state.get_data()
    payload = {
        'first_name': data['first_name'],
        'last_name': data['last_name'],
        'phone': data['phone'],
        'address': message.text.strip(),
    }

    user_id = message.from_user.id
    headers = {"X-User-ID": str(user_id)}
    result, error = await make_api_request("POST", 'clients/', headers=headers, data=payload)

    if error:
        await send_error_message(message, error)
    else:
        await message.reply(f"Клиент {result['first_name']} добавлен!")
    await state.clear()