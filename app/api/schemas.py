from pydantic import BaseModel, Field, field_validator
from typing import Dict


class BidRequest(BaseModel):
    supply_id: str
    ip: str
    country: str = Field(min_length=2, max_length=2)
    tmax: int | None = None
    
    @field_validator('country')
    @classmethod
    def uppercase_country(cls, v: str) -> str:
        return v.upper()


class BidResponse(BaseModel):
    winner: str
    price: float


class BidderStats(BaseModel):
    wins: int = 0
    total_revenue: float = 0.0
    no_bids: int = 0
    timeouts: int = 0


class SupplyStats(BaseModel):
    total_reqs: int = 0
    reqs_per_country: Dict[str, int] = Field(default_factory=dict)
    bidders: Dict[str, BidderStats] = Field(default_factory=dict)
