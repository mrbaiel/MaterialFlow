from aiogram import Router, types
from .. import config

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from telegram_bot.utils import make_api_request, send_error_message
from telegram_bot.states import AddEmployeeState

router = Router()

@router.message(Command('add_employee'))
async def add_employee_start(message: types.Message, state: FSMContext):
    await message.reply("Введите имя сотрудника: ")
    await state.set_state(AddEmployeeState.first_name)

@router.message(AddEmployeeState.first_name)
async def add_employee_first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text.strip())
    await message.reply("Введите фамилию сотрудника: ")
    await state.set_state(AddEmployeeState.last_name)

@router.message(AddEmployeeState.last_name)
async def add_employee_last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text.strip()) or ""
    await message.reply("Введите номер телефона через +996 (или оставьте пустым)")
    await state.set_state(AddEmployeeState.phone)

@router.message(AddEmployeeState.phone)
async def add_employee_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip() or ""
    await state.update_data(phone=phone)
    await message.reply("Введите адрес сотрудника: (или оставьте пустым)")
    await state.set_state(AddEmployeeState.address)

@router.message(AddEmployeeState.address)
async def add_employee_address(message: types.Message, state: FSMContext):
    data = await state.get_data()
    payload = {
        'first_name': data['first_name'],
        'last_name': data['last_name'],
        'phone': data['phone'],
        'address': message.text.strip() or "",
    }
    result, error = await make_api_request('POST', 'employees/', payload, config.API_TOKEN)
    if error:
        await send_error_message(message, error)
    else:
        await message.reply(f"Сотрудник {result['first_name']} добавлен!")
    await state.clear()
