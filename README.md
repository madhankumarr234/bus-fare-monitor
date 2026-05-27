# Bus Fare Monitor 🚌💰

A production-ready Python AI-powered agent for monitoring and analyzing bus ticket fares across multiple platforms. It uses Playwright for browser automation, checks prices every hour, stores data in SQLite, and sends Telegram alerts when deals are detected.

## ✨ Features

✅ **Multi-Platform Scraping**
- RedBus and AbhiBus support
- Extracts: operator name, departure/arrival time, fare, seats available, bus type
- Anti-bot friendly with random delays and retry logic

✅ **AI-Powered Fare Analysis**
- Classifies fares as: cheap, normal, or expensive
- Uses statistical percentile analysis
- OpenAI integration for advanced reasoning

✅ **Smart Alerts via Telegram**
- 🎉 Price drop notifications
- ⚠️ Low seats availability warnings
- 💎 Good deal detected alerts
- 📊 Daily summary reports

✅ **Historical Data Tracking**
- SQLite database with indexed queries
- Price history and trend analysis
- Automatic data cleanup after 7 days

✅ **Configurable Monitoring**
- Per-route configuration
- Custom price drop thresholds
- Preferred bus type filtering
- Budget limits

✅ **Modern Architecture**
- Fully async/await Python
- APScheduler for job management
- Modular design with clear separation of concerns
- Comprehensive logging

## 📋 Requirements

- Python 3.9+
- Telegram Bot Token
- OpenAI API Key (optional, for advanced analysis)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/madhankumarr234/bus-fare-monitor.git
cd bus-fare-monitor
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
OPENAI_API_KEY=your_openai_key_here (optional)
DATABASE_PATH=./data/fares.db
```

### 5. Configure Routes

Edit `config.json` with your preferred routes:

```json
{
  "routes": [
    {
      "id": "route_1",
      "source_city": "Bangalore",
      "destination_city": "Chennai",
      "travel_date": "2024-06-15",
      "max_budget": 800,
      "preferred_bus_types": ["AC", "Semi-Sleeper"],
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

### 6. Run Locally

```bash
python main.py
```

## 🐳 Deploy with Docker

### Build Image

```bash
docker build -t bus-fare-monitor .
```

### Run Container

```bash
docker run -d \
  --name bus-monitor \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e TELEGRAM_CHAT_ID=your_chat_id \
  -e OPENAI_API_KEY=your_key \
  -v bus-data:/app/data \
  -v bus-logs:/app/logs \
  bus-fare-monitor
```

### With Docker Compose

```bash
# Copy environment from template
cp .env.example .env
# Edit .env with your credentials

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

## ☁️ Deploy on Render

### 1. Push to GitHub

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Create New Web Service on Render

1. Go to [render.com](https://render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Choose Python environment
5. Build command: `pip install -r requirements.txt && playwright install chromium`
6. Start command: `python main.py`

### 3. Add Environment Variables

In Render dashboard, add:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `OPENAI_API_KEY` (optional)
- `DATABASE_PATH=./data/fares.db`

### 4. Deploy

Click "Create Web Service" and wait for deployment.

## 🚂 Deploy on Railway

### 1. Install Railway CLI

```bash
npm install -g @railway/cli
```

### 2. Login and Initialize

```bash
railway login
railway init
```

### 3. Add Environment Variables

```bash
railway variables set TELEGRAM_BOT_TOKEN="your_token"
railway variables set TELEGRAM_CHAT_ID="your_chat_id"
railway variables set OPENAI_API_KEY="your_key"
```

### 4. Deploy

```bash
railway up
```

### 5. View Logs

```bash
railway logs
```

## 📊 Project Structure

```
bus-fare-monitor/
├── database/              # Database management
│   ├── __init__.py
│   └── db_manager.py      # SQLite operations
├── scraper/               # Web scraping
│   ├── __init__.py
│   ├── base_scraper.py    # Base class with retry logic
│   ├── redbus_scraper.py  # RedBus implementation
│   └── abhibus_scraper.py # AbhiBus implementation
├── notifier/              # Notifications
│   ├── __init__.py
│   └── telegram_notifier.py
├── ai_engine/             # AI analysis
│   ├── __init__.py
│   └── fare_analyzer.py   # Fare classification
├── scheduler/             # Job scheduling
│   ├── __init__.py
│   └── task_scheduler.py
├── main.py                # Application entry point
├── config.json.sample     # Configuration template
├── .env.example           # Environment template
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
└── README.md              # This file
```

## 🔧 Configuration Details

### Routes Configuration

Each route object requires:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique route identifier |
| `source_city` | string | Starting city |
| `destination_city` | string | Destination city |
| `travel_date` | string | Travel date (YYYY-MM-DD) |
| `max_budget` | number | Maximum acceptable price |
| `preferred_bus_types` | array | Preferred bus types (AC, Sleeper, etc.) |
| `alert_on_price_drop_percentage` | number | Price drop threshold for alerts |
| `minimum_seats_to_alert` | number | Alert when seats drop below this |
| `enabled` | boolean | Enable/disable this route |

### Scraper Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `enable_redbus` | true | Enable RedBus scraping |
| `enable_abhibus` | true | Enable AbhiBus scraping |
| `browser_headless` | true | Run browser in headless mode |
| `check_interval_minutes` | 60 | Check interval in minutes |
| `min_delay_seconds` | 2 | Minimum delay between requests |
| `max_delay_seconds` | 5 | Maximum delay between requests |

## 📱 Telegram Setup

### Get Bot Token

1. Open Telegram and search for "BotFather"
2. Send `/start` and then `/newbot`
3. Follow the prompts to create a new bot
4. Copy the bot token

### Get Chat ID

1. Search for "@userinfobot" on Telegram
2. Send `/start`
3. Your chat ID will be displayed

Alternatively:
1. Send a message to your bot
2. Visit: `https://api.telegram.org/bot{TOKEN}/getUpdates`
3. Find your chat ID in the response

## 🔍 Monitoring and Logs

### View Live Logs

```bash
tail -f logs/bus_monitor_*.log
```

### Log Locations

- Local: `./logs/bus_monitor_*.log`
- Docker: `docker logs bus-monitor`
- Render: Dashboard → Logs
- Railway: `railway logs`

## 📊 Database Schema

### bus_fares Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| route_id | TEXT | Route identifier |
| platform | TEXT | Bus platform (RedBus/AbhiBus) |
| operator_name | TEXT | Bus operator name |
| departure_time | TEXT | Departure time |
| arrival_time | TEXT | Arrival time |
| fare | INTEGER | Ticket price |
| seats_left | INTEGER | Available seats |
| bus_type | TEXT | Bus type (AC/Sleeper/etc) |
| source_city | TEXT | Source city |
| destination_city | TEXT | Destination city |
| travel_date | TEXT | Travel date |
| checked_at | TIMESTAMP | Check timestamp |

### price_alerts Table

Records all alerts (price drops, low seats, good deals)

### ai_analysis Table

Stores AI classification results with confidence scores

## 🔐 Security Best Practices

1. **Never commit `.env` file**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use environment variables for secrets**
   - Telegram bot token
   - OpenAI API key
   - Database paths

3. **Enable browser security features**
   - Anti-automation headers
   - Random delays between requests
   - Rotating user agents

4. **Database security**
   - SQLite file with restricted permissions
   - Automatic data cleanup after 7 days

## 🆘 Troubleshooting

### Playwright Installation Issues

```bash
# On Ubuntu/Debian:
sudo apt-get install -y libgconf-2-4 libxss1 libappindicator1 libindicator7 libgbm1 libxss1

# Then reinstall:
pip install --upgrade playwright
playwright install chromium
```

### Database Locked Error

The application handles concurrent access. If you see database locked errors:

```bash
rm data/fares.db
# Application will recreate it on next run
```

### Telegram Messages Not Sending

1. Verify bot token and chat ID
2. Check internet connectivity
3. Ensure bot has message permissions
4. Check logs for specific error messages

### No Buses Found

1. Verify source/destination cities are correct
2. Check if travel date is in the future
3. Ensure routes are enabled in config
4. Check scraper logs for errors

## 📈 Performance Optimization

### For Large Scale Deployment

1. **Increase browser pool** (modify `BaseScraper`)
2. **Use connection pooling** for database
3. **Implement caching** for repeated searches
4. **Use async context managers** properly

### Memory Usage

- Typical: ~200-300 MB with browser
- Database: ~10-50 MB per month (auto-cleanup)
- Logs: ~100 MB per month

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 💡 Future Enhancements

- [ ] Web dashboard for monitoring
- [ ] SMS notifications
- [ ] Multiple language support
- [ ] Email notifications
- [ ] Price prediction using ML
- [ ] More bus platforms (MakemyTrip, etc.)
- [ ] REST API for integration
- [ ] Mobile app

## 🆘 Support

For issues and questions:

1. Check existing GitHub issues
2. Review logs in `logs/` directory
3. Create a new issue with detailed error messages
4. Include your configuration (without secrets)

## 🎯 Pro Tips

1. **Monitor multiple routes**
   - Add multiple entries in `config.json`
   - System manages all concurrently

2. **Use price history**
   - Access `price_alerts` table
   - Analyze trends over time

3. **Optimize scraping**
   - Increase `min/max_delay_seconds` to be less detected
   - Decrease to scan faster

4. **Save bandwidth**
   - Disable unneeded platforms in `scraper_settings`
   - Increase check interval

## 📞 Contact

Created by [@madhankumarr234](https://github.com/madhankumarr234)

---

**Happy fare hunting! 🎉🚌**
