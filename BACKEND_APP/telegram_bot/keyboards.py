from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/add_batch"), KeyboardButton(text="/add_subbatch")],
        [KeyboardButton(text="/add_employee"), KeyboardButton(text="/add_client")],
        [KeyboardButton(text="/add_order"), KeyboardButton(text="/add_order_item")],
        [KeyboardButton(text="/add_payment")],
        [KeyboardButton(text="/report_production"), KeyboardButton(text="/report_orders")],
    ],
    resize_keyboard=True,  # чтобы кнопки были удобными
    input_field_placeholder="Выберите команду из меню 👇"
)