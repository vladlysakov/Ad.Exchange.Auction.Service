from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    
    rate_limit_requests: int = 3
    rate_limit_window: int = 60
    
    min_bid_price: float = 0.01
    max_bid_price: float = 1.00
    no_bid_probability: float = 0.30
    
    class Config:
        env_file = ".env"


settings = Settings()
