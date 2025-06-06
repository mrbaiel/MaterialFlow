from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить партию"), KeyboardButton(text="Добавить подпартию")],
        [KeyboardButton(text="Добавить сотрудника"), KeyboardButton(text="Добавить клиента")],
        [KeyboardButton(text="Добавить заказ"), KeyboardButton(text="Добавить позиции заказа")],
        [KeyboardButton(text="Отчет по производству"), KeyboardButton(text="Отчет по заказам")],
    ],
    resize_keyboard=True,  # чтобы кнопки были удобными
    input_field_placeholder="Что хотите сделать?"
)
