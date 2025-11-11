import redis.asyncio as redis
from app.core.config import settings
from typing import Dict


class StatsService:
    client = None

    async def connect(self):
        self.client = redis.from_url(settings.redis_url, decode_responses=True)

    async def disconnect(self):
        if self.client:
            await self.client.close()

    async def increment_requests(self, supply_id: str, country: str):
        await self.client.hincrby(f"stats:{supply_id}", "total", 1)
        await self.client.hincrby(f"stats:{supply_id}:country", country, 1)

    @staticmethod
    def _build_bid_key(supply_id: str, bidder_id: str):
        return f"stats:{supply_id}:bidder:{bidder_id}"

    async def record_bid(
            self,
            supply_id: str,
            bidder_id: str,
            won: bool = False,
            price: float = None,
            no_bid: bool = False,
            timeout: bool = False,
    ):
        key = self._build_bid_key(supply_id, bidder_id)

        if won and price:
            await self.client.hincrbyfloat(key, "revenue", price)
            await self.client.hincrby(key, "wins", 1)

        if no_bid:
            await self.client.hincrby(key, "no_bids", 1)

        if timeout:
            await self.client.hincrby(key, "timeouts", 1)

    async def get_stats(self) -> Dict:
        result = {}
        keys = await self.client.keys("stats:*")

        supply_ids = set()

        for key in keys:
            parts = key.split(":")
            if len(parts) >= 2:
                supply_ids.add(parts[1])

        for sid in supply_ids:
            stats_data = {
                "total_reqs": 0,
                "reqs_per_country": {},
                "bidders": {}
            }

            total = await self.client.hget(f"stats:{sid}", "total")
            if total:
                stats_data["total_reqs"] = int(total)

            countries = await self.client.hgetall(f"stats:{sid}:country")
            stats_data["reqs_per_country"] = {k: int(v) for k, v in countries.items()}

            bidder_keys = await self.client.keys(f"stats:{sid}:bidder:*")
            for bkey in bidder_keys:
                bid_id = bkey.split(":")[-1]
                data = await self.client.hgetall(bkey)

                stats_data["bidders"][bid_id] = {
                    "wins": int(data.get("wins", 0)),
                    "total_revenue": float(data.get("revenue", 0.0)),
                    "no_bids": int(data.get("no_bids", 0)),
                    "timeouts": int(data.get("timeouts", 0))
                }

            result[sid] = stats_data

        return result
