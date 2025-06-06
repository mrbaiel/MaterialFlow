from aiogram.fsm.context import FSMContext
from aiogram import Router, F, types

from datetime import date

from telegram_bot.states import AddOrderState
from telegram_bot.utils import make_api_request, send_error_message

router = Router()

@router.message(F.text.in_({"/add_order", "Добавить заказ"}))
async def add_order_start(message: types.Message, state: FSMContext):

    user_id = message.from_user.id
    headers = {"X-User-ID": user_id}
    result, error = await make_api_request("GET", "clients/", headers)

    if error:
        await send_error_message(message, error)
        return

    clients = result['results']
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=f"{client['first_name']} {client['last_name']}", callback_data=f"client_{client['id']}")]
        for client in clients[:6]
    ])

    await message.reply("Выберите клиента:", reply_markup=keyboard)
    await state.set_state(AddOrderState.client)

@router.callback_query(AddOrderState.client)
async def add_order_client(callback: types.CallbackQuery, state: FSMContext):
    print(callback.data)
    client_id = int(callback.data.split('_')[1])
    await state.update_data(client_id=client_id)
    await callback.message.reply("Введите дату (ГГГГ-ММ-ДД) или 'сегодня'")
    await state.set_state(AddOrderState.date)

@router.message(AddOrderState.date)
async def add_order_date(message: types.Message, state: FSMContext):
    date_str = message.text.strip()
    try:
        if date_str.lower() == 'сегодня':
            order_date = date.today().isoformat()
        else:
            order_date = date.fromisoformat(date_str).isoformat()
    except ValueError:
        await send_error_message(message, "Неверный формат даты! \n пример: (ГГГГ-ММ-ДД)")
        return

    await state.update_data(order_date=order_date)
    await message.reply("Введите сумму аванса или '0'")
    await state.set_state(AddOrderState.initial_payment)

@router.message(AddOrderState.initial_payment)
async def add_order_initial_payment(message: types.Message, state: FSMContext):
    try:
        initial_payment = float(message.text)
        if initial_payment < 0:
            raise ValueError("Сумма не может быть отрицательным")
    except ValueError:
        await send_error_message(message, "Неверные данные")
        return

    data = await state.get_data()
    payload = {
        "client_id": data['client_id'],
        "order_date": data['order_date'],
        "initial_payment": initial_payment,
        "status": "pending",
    }

    user_id = message.from_user.id
    headers = {"X-User-ID": str(user_id)}
    result, error = await make_api_request("POST", "orders/", data=payload, headers=headers)

    if error:
        await send_error_message(message, error)
    else:
        await message.reply(f"Заказ №{result['id']} создан!")
    await state.clear()