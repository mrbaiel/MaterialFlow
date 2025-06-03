import logging

from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Awaitable, Dict, Any

from telegram_bot.utils import make_api_request

logger = logging.getLogger(__name__)

ALLOWED_ROLES = ["owner", "admin", "developer"]


class AccessMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        telegram_id = str(event.from_user.id)

        print("Мидлвар работает работу)")

        if data.get("state"):
            state_data = await data["state"].get_data()
            if state_data.get("access_granted"):
                return await handler(event, data)

        payload = {"telegram_id": telegram_id}
        result, error = await make_api_request("POST", "auth/verify-telegram/", payload)

        if error or result.get("role") not in ALLOWED_ROLES:
            await event.reply("Извините уважаемый,\n"
                              "у вас нет доступа :(")
            return

        logger.warning(f"Результат ответа: {result}")

        if data.get("state"):
            await data["state"].update_data(
                access_granted=True,
                user_id=result["user_id"],
                role=result["role"],
            )

        return await handler(event, data)