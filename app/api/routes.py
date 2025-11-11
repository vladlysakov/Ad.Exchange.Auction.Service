from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import BidRequest, BidResponse
from app.db.session import get_db
from . import rate_limiter, auction_service, stats_service
router = APIRouter()


@router.post("/bid", response_model=BidResponse)
async def create_bid(request: BidRequest, db: AsyncSession = Depends(get_db)):
    allowed = await rate_limiter.is_allowed(request.ip)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )

    winner, price = await auction_service.run_auction(
        db, request.supply_id, request.ip, request.country, request.tmax
    )

    if not winner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No winner found"
        )

    return BidResponse(winner=winner, price=price)


@router.get("/stat")
async def get_stats():
    stats = await stats_service.get_stats()
    return {"supplies": stats}


@router.get("/health")
async def health():
    return {"status": "ok"}
