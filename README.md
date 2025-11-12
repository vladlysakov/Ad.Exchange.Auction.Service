# Ad Exchange Auction Service

A real-time bidding (RTB) auction service for ad exchanges built with FastAPI, PostgreSQL, and Redis.

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Task (optional, but recommended) - [installation guide](https://taskfile.dev/installation/)

### Running the Application

The easiest way to run the application is using Docker Compose:

```bash
# Using task (recommended)
task docker-up

# Or using docker-compose directly
docker-compose up -d
```

This will:
- Start PostgreSQL database
- Start Redis cache
- Build and run the API service
- Automatically run database migrations
- Seed initial test data

The API will be available at: **http://localhost:8000**

### Viewing Logs

```bash
# Using task
task docker-logs

# Or directly
docker-compose logs -f api
```

### Stopping the Application

```bash
# Using task
task docker-down

# Or directly
docker-compose down
```

## API Documentation

Once the application is running, open the interactive API documentation in your browser:

**Swagger UI**: http://localhost:8000/docs

**ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. POST /bid - Create Auction Bid

Starts a new auction for a given supply and returns the winning bidder.

**Request Example:**

```json
{
  "supply_id": "supply1",
  "ip": "192.168.1.1",
  "country": "US"
}
```

**Request with timeout (optional tmax parameter):**

```json
{
  "supply_id": "supply1",
  "ip": "192.168.1.1",
  "country": "US",
  "tmax": 100
}
```

**Response (200 OK):**

```json
{
  "winner": "bidder1",
  "price": 0.73
}
```

**Response (404 Not Found):**

```json
{
  "detail": "No winner found"
}
```

**Response (429 Too Many Requests):**

```json
{
  "detail": "Rate limit exceeded"
}
```

**cURL Example:**

```bash
curl -X POST "http://localhost:8000/bid" \
  -H "Content-Type: application/json" \
  -d '{
    "supply_id": "supply1",
    "ip": "192.168.1.1",
    "country": "US"
  }'
```

**Field Descriptions:**

- `supply_id` (string, required) - Supply identifier (e.g., "supply1", "supply2", "supply3")
- `ip` (string, required) - Client IP address for rate limiting
- `country` (string, required) - Two-letter ISO country code (e.g., "US", "GB", "CA")
- `tmax` (integer, optional) - Maximum time in milliseconds for bidder response

### 2. GET /stat - Get Statistics

Returns overall auction statistics grouped by supply.

**Response Example:**

```json
{
  "supplies": {
    "supply1": {
      "total_reqs": 10,
      "reqs_per_country": {
        "US": 6,
        "GB": 4
      },
      "bidders": {
        "bidder1": {
          "wins": 3,
          "total_revenue": 1.45,
          "no_bids": 2,
          "timeouts": 0
        },
        "bidder2": {
          "wins": 2,
          "total_revenue": 0.89,
          "no_bids": 1,
          "timeouts": 1
        }
      }
    }
  }
}
```

**cURL Example:**

```bash
curl http://localhost:8000/stat
```

### 3. GET /health - Health Check

Simple health check endpoint.

**Response:**

```json
{
  "status": "ok"
}
```

**cURL Example:**

```bash
curl http://localhost:8000/health
```

## Testing Different Scenarios

### Scenario 1: Basic Auction

```bash
curl -X POST "http://localhost:8000/bid" \
  -H "Content-Type: application/json" \
  -d '{
    "supply_id": "supply1",
    "ip": "10.0.0.1",
    "country": "US"
  }'
```

Expected: Winner will be either `bidder1` or `bidder3` (both from US)

### Scenario 2: Country Filtering

```bash
curl -X POST "http://localhost:8000/bid" \
  -H "Content-Type: application/json" \
  -d '{
    "supply_id": "supply1",
    "ip": "10.0.0.2",
    "country": "GB"
  }'
```

Expected: Winner will be `bidder2` (only GB bidder for supply1)

### Scenario 3: Timeout Simulation

```bash
curl -X POST "http://localhost:8000/bid" \
  -H "Content-Type: application/json" \
  -d '{
    "supply_id": "supply1",
    "ip": "10.0.0.3",
    "country": "US",
    "tmax": 30
  }'
```

Expected: Some bidders may timeout with low tmax value

### Scenario 4: Rate Limiting

Run the same request 4 times quickly:

```bash
for i in {1..4}; do
  curl -X POST "http://localhost:8000/bid" \
    -H "Content-Type: application/json" \
    -d '{
      "supply_id": "supply1",
      "ip": "192.168.1.100",
      "country": "US"
    }'
  echo ""
done
```

Expected: First 3 requests succeed, 4th returns 429 (rate limit exceeded)

## Test Data

The application is seeded with the following test data:

**Supplies:**
- `supply1` - has bidders: bidder1 (US), bidder2 (GB), bidder3 (US)
- `supply2` - has bidders: bidder2 (GB), bidder3 (US)
- `supply3` - has bidders: bidder1 (US), bidder4 (CA), bidder5 (GB)

**Bidders:**
- `bidder1` - Country: US
- `bidder2` - Country: GB
- `bidder3` - Country: US
- `bidder4` - Country: CA
- `bidder5` - Country: GB

## Configuration

Application settings can be configured via environment variables in `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ad_exchange
REDIS_URL=redis://localhost:6379/0

# Rate limiting
RATE_LIMIT_REQUESTS=3
RATE_LIMIT_WINDOW=60

# Auction settings
MIN_BID_PRICE=0.01
MAX_BID_PRICE=1.00
NO_BID_PROBABILITY=0.30
```

## Development

### Manual Setup (without Docker)

If you prefer to run services manually:

```bash
# Install dependencies
pip install -e ".[dev]"

# Start PostgreSQL and Redis
docker run -d --name postgres -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=ad_exchange postgres:16-alpine

docker run -d --name redis -p 6379:6379 redis:7-alpine

# Copy environment file
cp .env.example .env

# Run migrations
alembic upgrade head

# Seed data
python seed.py

# Run application
uvicorn app.main:app --reload
```

### Running Tests

```bash
# Using task
task test

# Or directly
pytest -v
```

### Available Task Commands

```bash
task install       # Install dependencies
task run           # Run application locally
task migrate       # Run database migrations
task seed          # Seed test data
task test          # Run tests
task docker-up     # Start all services with Docker
task docker-down   # Stop Docker services
task docker-logs   # View API logs
task docker-build  # Rebuild Docker image
task docker-restart # Restart API service
task clean         # Clean cache files
```

## How It Works

### Auction Flow

1. **Request Validation** - Validates supply_id, IP, and country code
2. **Rate Limiting** - Checks if IP has exceeded rate limit (3 requests per minute)
3. **Bidder Selection** - Filters bidders by matching country
4. **Bid Simulation** - Each bidder:
   - Generates random bid between 0.01 and 1.00
   - Has 30% chance of not bidding
   - May timeout if tmax parameter is set
5. **Winner Selection** - Highest bid wins
6. **Statistics Update** - Records results in Redis

### Rate Limiting

- Default: 3 requests per minute per IP address
- Uses Redis for distributed rate limiting
- Returns HTTP 429 when limit exceeded

### Statistics Tracking

All statistics are stored in Redis for fast access:
- Total requests per supply
- Requests per country
- Bidder wins and revenue
- No-bid counts
- Timeout counts

## Troubleshooting

### API not responding

Check if services are running:
```bash
docker compose ps
```

View logs:
```bash
docker compose logs api
```

### Database connection error

Ensure PostgreSQL is healthy:
```bash
docker compose logs postgres
```

Restart services:
```bash
docker compose restart
```

### Reset all data

```bash
# Stop and remove volumes
docker compose down -v

# Start fresh
docker compose up -d
```