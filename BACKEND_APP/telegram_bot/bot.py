from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from telegram_bot.config import BOT_TOKEN
from telegram_bot.handlers import auth, production, employees


async def main():
    print("БОТ ЗАПУЩЕН")
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(auth.router, production.router, employees.router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())