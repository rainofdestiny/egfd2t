import logging

import uvicorn

import redis.asyncio as redis

from fastapi import FastAPI, Depends, Request, HTTPException, status, Body, Query
from aiogram import Bot, Dispatcher, types, filters, exceptions
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.deep_linking import decode_payload, encode_payload

from config import settings
from depends import get_redis
from middlewares import RedisMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.telegram_bot_token)
dp = Dispatcher(storage=MemoryStorage(), r=get_redis)
dp.message.middleware(RedisMiddleware())

app = FastAPI()


@dp.message(filters.CommandStart())
async def cmd_start(
    message: types.Message, command: filters.CommandObject, r: redis.Redis
):
    logger.info("IM HERE HELP ME PLEASE")
    if command and command.args:
        try:
            user_id = decode_payload(command.args)
            logger.info(f"{user_id=}")
            await r.set(user_id, message.from_user.id)
            logger.info(f"Linked UID {user_id} to Telegram user {message.from_user.id}")
        except UnicodeDecodeError as e:
            logger.error(f"Payload decoding error: {e}")
    else:
        logger.warning("Command /start invoked without arguments.")

    await message.answer("Вы успешно привязали Discord аккаунт!")


@app.post("/webhook")
async def telegram_webhook(request: Request) -> dict:
    try:
        update_data = await request.json()
    except Exception as e:
        logger.exception("Error reading JSON from request")
        raise HTTPException(400) from e

    try:
        update = types.Update(**update_data)
    except Exception as e:
        logger.exception("Failed to parse Update object")
        raise HTTPException(400) from e

    await dp.feed_update(bot, update)
    return {"ok": True}


@app.post("/send-gif", status_code=status.HTTP_200_OK)
async def send_gif(
    user_id: int = Body(...),
    url: str = Body(...),
    r: redis.Redis = Depends(get_redis),
):
    tuid = await r.get(user_id)
    if tuid:
        try:
            await bot.send_animation(tuid, url)
            return
        except exceptions.TelegramBadRequest as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@app.get("/link", status_code=status.HTTP_200_OK)
async def link(user_id: int = Query(...)) -> dict:
    username = (await bot.me()).username
    payload = encode_payload(str(user_id))
    sync_link = f"https://t.me/{username}?start={payload}"
    return {"link": sync_link}


@app.get("/reset", status_code=status.HTTP_200_OK)
async def reset(user_id: int = Query(...), r: redis.Redis = Depends(get_redis)) -> dict:
    await r.delete(user_id)
    return {"ok": True}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
