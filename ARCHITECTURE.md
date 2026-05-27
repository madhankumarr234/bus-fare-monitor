# Architecture Overview

## System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    BusFareMonitor                            │
│                   (main.py)                                  │
└─────────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼─────┐    ┌─────▼──────┐   ┌─────▼──────┐
    │ Scheduler │    │ Scrapers   │   │ Database   │
    │ (APSched) │    │ (Playwright)   │ (SQLite)   │
    └────┬─────┘    └─────┬──────┘   └─────┬──────┘
         │                │                │
         └────────────────┼────────────────┘
                          │
                 ┌────────▼────────┐
                 │  AI Engine      │
                 │  (Analyzer)     │
                 └────────┬────────┘
                          │
                 ┌────────▼────────┐
                 │  Notifier       │
                 │  (Telegram)     │
                 └─────────────────┘
```

## Data Flow

```
1. Scheduler triggers monitoring job
   ↓
2. Scraper fetches bus data from platforms
   ├─ RedBus scraper
   └─ AbhiBus scraper
   ↓
3. Data stored in database (bus_fares table)
   ↓
4. AI Analyzer classifies fares
   ├─ Statistical percentile analysis
   └─ OpenAI integration (optional)
   ↓
5. Comparison engine checks for changes
   ├─ Price drops
   ├─ Seat availability
   └─ Good deals
   ↓
6. Alerts recorded in database
   ↓
7. Telegram notifier sends alerts
```

## Module Architecture

### Database Module (`database/`)
- **db_manager.py**: SQLite operations
  - Table creation and indexing
  - Insert/update fare data
  - Historical data retrieval
  - Statistics calculation
  - Alert recording

### Scraper Module (`scraper/`)
- **base_scraper.py**: Abstract base class
  - Browser initialization
  - Retry with exponential backoff
  - Random delay injection
  - Anti-bot headers

- **redbus_scraper.py**: RedBus implementation
  - URL building
  - DOM parsing
  - Data extraction

- **abhibus_scraper.py**: AbhiBus implementation
  - URL building
  - DOM parsing
  - Data extraction

### AI Engine Module (`ai_engine/`)
- **fare_analyzer.py**: Analysis engine
  - Percentile-based classification
  - Price drop detection
  - Seat availability analysis
  - OpenAI integration

### Notifier Module (`notifier/`)
- **telegram_notifier.py**: Telegram bot
  - Price drop alerts
  - Low seats alerts
  - Good deal alerts
  - Summary reports
  - Error notifications

### Scheduler Module (`scheduler/`)
- **task_scheduler.py**: Job management
  - APScheduler wrapper
  - Hourly job creation
  - Custom intervals
  - Job lifecycle management

## Database Schema

### bus_fares Table
```sql
CREATE TABLE bus_fares (
    id INTEGER PRIMARY KEY,
    route_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    operator_name TEXT NOT NULL,
    departure_time TEXT,
    arrival_time TEXT,
    fare INTEGER NOT NULL,
    seats_left INTEGER,
    bus_type TEXT,
    source_city TEXT,
    destination_city TEXT,
    travel_date TEXT,
    checked_at TIMESTAMP
)
```

### Indexes
- `idx_route_date`: (route_id, travel_date, checked_at)
- `idx_platform`: (platform, operator_name)

### price_alerts Table
```sql
CREATE TABLE price_alerts (
    id INTEGER PRIMARY KEY,
    route_id TEXT,
    operator_name TEXT,
    platform TEXT,
    alert_type TEXT,
    old_price INTEGER,
    new_price INTEGER,
    price_drop_percentage REAL,
    old_seats INTEGER,
    new_seats INTEGER,
    alerted_at TIMESTAMP
)
```

### ai_analysis Table
```sql
CREATE TABLE ai_analysis (
    id INTEGER PRIMARY KEY,
    route_id TEXT,
    operator_name TEXT,
    platform TEXT,
    fare_classification TEXT,
    reasoning TEXT,
    confidence_score REAL,
    analyzed_at TIMESTAMP
)
```

## Configuration Structure

```json
{
  "routes": [
    {
      "id": "route_1",
      "source_city": "Bangalore",
      "destination_city": "Chennai",
      "travel_date": "2024-12-25",
      "max_budget": 1000,
      "preferred_bus_types": ["AC"],
      "alert_on_price_drop_percentage": 10,
      "minimum_seats_to_alert": 5,
      "enabled": true
    }
  ],
  "scraper_settings": {
    "enable_redbus": true,
    "enable_abhibus": true,
    "browser_headless": true,
    "check_interval_minutes": 60,
    "min_delay_seconds": 2,
    "max_delay_seconds": 5
  },
  "ai_analysis": {
    "enabled": true
  },
  "notifications": {
    "enabled": true,
    "telegram": true
  }
}
```

## Error Handling Strategy

### Scraper Errors
- Automatic retry with exponential backoff (3 attempts)
- Graceful fallback if all retries fail
- Detailed logging of failures
- Optional error notifications

### Database Errors
- Duplicate entry handling (skip silently)
- Connection pooling for concurrent access
- Automatic cleanup of old data
- Transaction support for data consistency

### Notification Errors
- Non-blocking error handling
- Logging of failed notifications
- Retry mechanism (future enhancement)

## Performance Characteristics

### Memory Usage
- Browser: ~150-200 MB
- Database connection: ~5-10 MB
- Cache: ~20-50 MB
- Total: ~200-300 MB

### Processing Time
- Per route scrape: 5-15 seconds
- AI analysis: 100-500 ms per bus
- Database operations: 10-50 ms
- Notification sending: 100-300 ms

### Scalability
- Max concurrent scrapes: 2-3 (configurable)
- Max routes: 10+ (tested)
- Database: 1M+ records (SQLite limit: 2TB)

## Security Considerations

### API Keys
- Stored in environment variables
- Never logged or exposed
- Loaded via python-dotenv

### Browser Automation
- Anti-automation detection headers
- Random delays between requests
- User-Agent rotation (future)
- Headless mode for production

### Database
- SQLite (local file-based)
- No network exposure
- File permissions: 0600

### Logging
- Sensitive data redacted
- Structured logging format
- Configurable log levels
- Automatic rotation (500 MB)

## Deployment Architecture

### Local Development
```
Your Machine
├─ Python 3.9+
├─ SQLite database
└─ Browser (Chromium)
```

### Docker
```
Docker Container
├─ Python 3.11 slim image
├─ Playwright (preinstalled)
├─ SQLite (mounted volume)
└─ Logs (mounted volume)
```

### Cloud (Render/Railway)
```
Cloud Instance
├─ Python runtime
├─ Ephemeral storage (logs)
├─ Persistent storage (database)
└─ Environment variables
```

## Future Enhancements

- [ ] Distributed scraping (multiple instances)
- [ ] PostgreSQL support
- [ ] REST API for external integration
- [ ] Web dashboard (FastAPI)
- [ ] Machine learning for price prediction
- [ ] Mobile app (Flutter/React Native)
- [ ] SMS notifications (Twilio)
- [ ] Email notifications (SendGrid)
- [ ] More platforms (MakemyTrip, Goibibo, etc.)
- [ ] Multi-language support
