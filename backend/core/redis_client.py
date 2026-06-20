import redis.asyncio as aioredis
from core.config import settings
from loguru import logger


class RedisClient:
    def __init__(self):
        self.client: aioredis.Redis | None = None

    async def connect(self):
        self.client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
        await self.client.ping()
        logger.info("Redis connection established.")

    async def disconnect(self):
        if self.client:
            await self.client.aclose()

    async def set(self, key: str, value: str, ex: int | None = None):
        await self.client.set(key, value, ex=ex)

    async def get(self, key: str) -> str | None:
        return await self.client.get(key)

    async def delete(self, key: str):
        await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        return bool(await self.client.exists(key))

    async def setex(self, key: str, seconds: int, value: str):
        await self.client.setex(key, seconds, value)

    async def publish(self, channel: str, message: str):
        await self.client.publish(channel, message)

    async def lpush(self, key: str, *values):
        await self.client.lpush(key, *values)

    async def lrange(self, key: str, start: int, end: int):
        return await self.client.lrange(key, start, end)

    async def expire(self, key: str, seconds: int):
        await self.client.expire(key, seconds)

    async def incr(self, key: str) -> int:
        return await self.client.incr(key)

    async def hset(self, name: str, mapping: dict):
        await self.client.hset(name, mapping=mapping)

    async def hget(self, name: str, key: str):
        return await self.client.hget(name, key)

    async def hgetall(self, name: str):
        return await self.client.hgetall(name)


redis_client = RedisClient()
