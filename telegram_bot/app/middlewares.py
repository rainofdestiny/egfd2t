from aiogram import BaseMiddleware
from aiogram.types import Update

from depends import get_redis


class RedisMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.redis = None

    async def __call__(self, handler, event: Update, data: dict):
        if self.redis is None:
            self.redis = await get_redis()
        data["r"] = self.redis
        return await handler(event, data)
