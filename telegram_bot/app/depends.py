import redis.asyncio as redis
from redis.asyncio import ConnectionPool


async def get_redis_pool() -> ConnectionPool:
    pool: ConnectionPool = redis.ConnectionPool(
        host="redis", port=6379, db=0, decode_responses=True, max_connections=10
    )
    return pool


async def get_redis() -> redis.Redis:
    pool: ConnectionPool = await get_redis_pool()
    return redis.Redis(connection_pool=pool)
