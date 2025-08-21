from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable

class ErrorsLoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]], event: Any, data: Dict[str, Any]) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            try:
                await event.answer("Что-то пошло не так. Попробуйте ещё раз.")
            except Exception:
                pass
            print("[ERROR]", type(e).__name__, e)
            return None
