import random
import asyncio
import logging
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Supply, Bidder
from app.services.stats import StatsService
from app.core.config import settings
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)


class AuctionService:
    def __init__(self, stats_service: StatsService):
        self.stats = stats_service
        self.min_price = settings.min_bid_price
        self.max_price = settings.max_bid_price
        self.no_bid_prob = settings.no_bid_probability

    @staticmethod
    async def get_eligible_bidders(
            db: AsyncSession,
            supply_id: str,
            country: str
    ) -> List[Bidder]:
        result = await db.execute(
            select(Supply)
            .filter(Supply.id == supply_id)
            .options(selectinload(Supply.bidders))
        )
        supply = result.scalar_one_or_none()

        if not supply:
            return []

        return [b for b in supply.bidders if b.country == country]

    async def _simulate_bid(self, bidder: Bidder, tmax: int = None):
        if tmax:
            latency = random.uniform(0, tmax + 50)
            await asyncio.sleep(latency / 1000)

            if latency > tmax:
                logger.warning(f"Timeout: {bidder.id} took {latency:.1f}ms")
                return None, False, True

        if random.random() < self.no_bid_prob:
            return None, True, False

        price = round(random.uniform(self.min_price, self.max_price), 2)
        return price, False, False

    async def run_auction(
            self,
            db: AsyncSession,
            supply_id: str,
            ip: str,
            country: str,
            tmax: int = None
    ) -> Tuple[str, float]:
        await self.stats.increment_requests(supply_id, country)

        bidders = await self.get_eligible_bidders(db, supply_id, country)

        if not bidders:
            logger.info(f"No eligible bidders for {supply_id} ({country})")
            return None, None

        logger.info(f"Auction: {supply_id} (country={country})")

        tasks = [self._simulate_bid(b, tmax) for b in bidders]
        results = await asyncio.gather(*tasks)

        bids = []
        for bidder, (price, no_bid, timeout) in zip(bidders, results):
            if timeout:
                logger.info(f"  {bidder.id} - timeout")
                await self.stats.record_bid(supply_id, bidder.id, timeout=True)
            elif no_bid:
                logger.info(f"  {bidder.id} - no bid")
                await self.stats.record_bid(supply_id, bidder.id, no_bid=True)
            else:
                logger.info(f"  {bidder.id} - {price}")
                bids.append((bidder.id, price))

        if not bids:
            logger.info("No winner")
            return None, None

        winner_id, price = max(bids, key=lambda x: x[1])
        logger.info(f"Winner: {winner_id} ({price})")

        await self.stats.record_bid(supply_id, winner_id, won=True, price=price)

        for bid_id, _ in bids:
            if bid_id != winner_id:
                await self.stats.record_bid(supply_id, bid_id, won=False)

        return winner_id, price
