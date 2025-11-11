import asyncio
from app.db.session import AsyncSessionLocal
from app.db.models import Supply, Bidder


async def seed():
    async with AsyncSessionLocal() as session:
        bidder1 = Bidder(id="bidder1", country="US")
        bidder2 = Bidder(id="bidder2", country="GB")
        bidder3 = Bidder(id="bidder3", country="US")
        bidder4 = Bidder(id="bidder4", country="CA")
        bidder5 = Bidder(id="bidder5", country="GB")
        
        session.add_all([bidder1, bidder2, bidder3, bidder4, bidder5])
        
        supply1 = Supply(id="supply1")
        supply1.bidders = [bidder1, bidder2, bidder3]
        
        supply2 = Supply(id="supply2")
        supply2.bidders = [bidder2, bidder3]
        
        supply3 = Supply(id="supply3")
        supply3.bidders = [bidder1, bidder4, bidder5]
        
        session.add_all([supply1, supply2, supply3])
        
        await session.commit()
        print("Data seeded successfully")


if __name__ == "__main__":
    asyncio.run(seed())
