import httpx

from config import settings


class Telegram:
    def __init__(self):
        self.service = settings.telegram_bot_service_url

    async def link(self, user_id: int) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=f"{self.service}/link",
                params={"user_id": user_id},
            )
            return response

    async def reset(self, user_id: int) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=f"{self.service}/reset",
                params={"user_id": user_id},
            )
            return response

    async def send_gif(self, user_id: int, url: str) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=f"{self.service}/send-gif",
                json={
                    "user_id": user_id,
                    "url": url,
                },
            )
            return response


telegram = Telegram()
