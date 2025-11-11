from app.services.auction import AuctionService
from app.services.rate_limiter import RateLimiter
from app.services.stats import StatsService

rate_limiter = RateLimiter()
stats_service = StatsService()
auction_service = AuctionService(stats_service)
