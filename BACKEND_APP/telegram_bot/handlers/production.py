from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import date
from telegram_bot import config
from telegram_bot.states import AddBatchState, AddSubBatchState
from telegram_bot.utils import make_api_request, send_error_message

router = Router()


@router.message(Command('add_batch'))
async def add_batch_start(message: types.Message, state: FSMContext):
    result, error = await make_api_request('GET', 'products/', token=config.API_TOKEN)
    if error:
        await send_error_message(message, error)
        return
    products = result.get('results', result)

    if not isinstance(products, list):
        await message.reply("Ошибка: неверный формат данных от сервера")
        return

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=f"{p['name']}", callback_data=f"product_{p['id']}")]
        for p in products[:10]
    ])
    await message.reply("Выберите продукт:", reply_markup=keyboard)
    await state.set_state(AddBatchState.product)


@router.callback_query(AddBatchState.product)
async def add_batch_product(callback: types.CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split('_')[1])
    await state.update_data(product_id=product_id)
    await callback.message.reply("Введите количество (шт):")
    await state.set_state(AddBatchState.quantity)


@router.message(AddBatchState.quantity)
async def add_batch_quantity(message: types.Message, state: FSMContext):
    try:
        quantity = int(message.text)
        if quantity <= 0:
            raise ValueError("Количество должно быть больше 0")
    except ValueError:
        await send_error_message(message, "Неверное количество")
        return
    await state.update_data(quantity=quantity)
    await message.reply("Введите дату (YYYY-MM-DD) или 'сегодня':")
    await state.set_state(AddBatchState.date)


@router.message(AddBatchState.date)
async def add_batch_date(message: types.Message, state: FSMContext):
    data = await state.get_data()
    date_str = message.text.strip()
    try:
        if date_str.lower() == 'сегодня':
            production_date = date.today().isoformat()
            print(f"ДАТА: {production_date}")
        else:
            production_date = date.fromisoformat(date_str).isoformat()
    except ValueError:
        await send_error_message(message, "Неверный формат даты (YYYY-MM-DD)")
        return

    payload = {
        'product_id': data['product_id'],
        'quantity': data['quantity'],
        'production_date': production_date,
    }
    result, error = await make_api_request('POST', 'batches/', payload, config.API_TOKEN)
    if error:
        await send_error_message(message, error)
    else:
        await message.reply(f"Партия создана!({result['quantity']}шт)")
    await state.clear()


@router.message(Command('add_subbatch'))
async def add_subbatch_start(message: types.Message, state: FSMContext):
    result, error = await make_api_request('GET', 'batches/?limit=10', token=config.API_TOKEN)
    print(f"{result} РЕЗУЛЬТАТ")

    if error:
        await send_error_message(message, error)
        return
    if not isinstance(result, dict):
        await send_error_message((message, error))
        return

    batches = result.get('results', [])

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(
            text=f"#{b['id']} {b['product']['name']}",
            callback_data=f"batch_{b['id']}"
        )] for b in batches if isinstance(b, dict) and isinstance(b.get("product"), dict)
    ])
    await message.reply("Выберите партию:", reply_markup=keyboard)
    await state.set_state(AddSubBatchState.batch)


@router.callback_query(AddSubBatchState.batch)
async def add_subbatch_batch(callback: types.CallbackQuery, state: FSMContext):
    batch_id = int(callback.data.split('_')[1])
    await state.update_data(batch_id=batch_id)
    await callback.message.reply("Введите количество (шт):")
    await state.set_state(AddSubBatchState.quantity)


@router.message(AddSubBatchState.quantity)
async def add_subbatch_quantity(message: types.Message, state: FSMContext):
    try:
        quantity = int(message.text)
        if quantity <= 0:
            raise ValueError("Количество должно быть больше 0")
    except ValueError:
        await send_error_message(message, "Неверное количество")
        return

    result, error = await make_api_request('GET', 'employees/', token=config.API_TOKEN)

    if error:
        await send_error_message(message, error)
        return

    employees = result.get('results', []) if isinstance(result, dict) else []

    await state.update_data(quantity=quantity, employees=employees)

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=f"{e['first_name']}", callback_data=f"emp_{e['id']}")]
        for e in employees[:10]
    ])

    await message.reply("Выберите сотрудников (можно несколько):", reply_markup=keyboard)
    await state.set_state(AddSubBatchState.employees)


@router.callback_query(AddSubBatchState.employees)
async def add_subbatch_employees(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if callback.data == "done":
        employee_ids = data.get("employee_ids", [])
        employee_names = data.get("employee_names", [])
        if not employee_ids:
            await callback.message.reply("Вы не выбрали ни одного сотрудника.")
            return

        payload = {
            'production_batch': data.get('batch_id'),
            'quantity': data.get('quantity'),
            'employee_ids': employee_ids,
        }

        result, error = await make_api_request('POST', 'subbatch/', payload, config.API_TOKEN)
        if error:
            await send_error_message(callback.message, error)
        else:
            await callback.message.reply(f"Подпартия создана для: {', '.join(employee_names)} ✅")

        await state.clear()
        return

    if callback.data.startswith("emp_"):
        try:
            employee_id = int(callback.data.split('_')[1])
        except (IndexError, ValueError):
            await send_error_message(callback.message, "Некорректный формат данных.")
            return

        employees = data.get("employees", [])
        selected_employee = next((e for e in employees if e["id"] == employee_id), None)
        if not selected_employee:
            await send_error_message(callback.message, "Сотрудник не найден.")
            return

        employee_ids = data.get("employee_ids", [])
        employee_names = data.get("employee_names", [])

        if employee_id not in employee_ids:
            employee_ids.append(employee_id)
            employee_names.append(selected_employee["first_name"])
            await state.update_data(employee_ids=employee_ids, employee_names=employee_names)

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Готово", callback_data="done")]
        ])
        await callback.message.reply(
            f"Добавить ещё сотрудника или нажмите 'Готово'. Уже выбрано: {', '.join(employee_names)}",
            reply_markup=keyboard
        )

@router.callback_query(AddSubBatchState.employees, lambda c: c.data == 'done')
async def add_subbatch_done(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    payload = {
        'production_batch': data['batch_id'],  # ❗ Используем правильное имя
        'quantity': data['quantity'],
        'employee_ids': data.get('employee_ids', []),
    }

    result, error = await make_api_request('POST', 'subbatch/', payload, config.API_TOKEN)

    if error:
        # Проверяем конкретную ошибку от API
        if isinstance(error, dict):
            non_field_errors = error.get("non_field_errors")
            if non_field_errors and "Общее количество подпартий превышает количество партии" in non_field_errors:
                await callback.message.reply(
                    "❌ Общее количество подпартий превышает количество партии.\n"
                    "Введите другое количество (меньше):"
                )
                await state.set_state(AddSubBatchState.quantity)
                return

        # Если другая ошибка — показать обычное сообщение
        await send_error_message(callback.message, error)
        return

    # Успешно
    await callback.message.reply(f"Подпартия создана! ✅")
    await state.clear()
