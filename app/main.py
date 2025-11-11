import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.routes import router, rate_limiter, stats_service
from app.db.session import init_db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    await rate_limiter.connect()
    await stats_service.connect()
    
    yield
    
    await rate_limiter.disconnect()
    await stats_service.disconnect()


app = FastAPI(title="Ad Exchange Auction", lifespan=lifespan)
app.include_router(router)
