import redis.asyncio as redis
from app.core.config import settings


class RateLimiter:
    client = None

    def __init__(self, max_requests=settings.rate_limit_requests, window=settings.rate_limit_window):
        self.window = window
        self.max_requests = max_requests

    async def connect(self):
        self.client = redis.from_url(settings.redis_url, decode_responses=True)

    async def disconnect(self):
        if self.client:
            await self.client.close()

    async def is_allowed(self, ip: str) -> bool:
        key = f"rl:{ip}"
        current = await self.client.get(key)

        if current is None:
            await self.client.setex(key, self.window, 1)
            return True

        count = int(current)
        if count >= self.max_requests:
            return False

        await self.client.incr(key)
        return True
