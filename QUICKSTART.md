# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Clone and Setup

```bash
git clone https://github.com/madhankumarr234/bus-fare-monitor.git
cd bus-fare-monitor
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### Step 3: Run Setup Wizard

```bash
python utils/setup_wizard.py
```

This will guide you through:
- Adding Telegram bot credentials
- OpenAI API key (optional)
- Configuring routes to monitor

### Step 4: Start Monitoring

```bash
python main.py
```

## 📱 Get Telegram Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/start`
3. Send `/newbot`
4. Follow the prompts
5. Copy the bot token provided

## 👤 Get Telegram Chat ID

### Method 1: Using @userinfobot
1. Search for **@userinfobot** on Telegram
2. Send `/start`
3. Your chat ID will be displayed

### Method 2: Manual
1. Send a message to your bot
2. Visit: `https://api.telegram.org/bot{TOKEN}/getUpdates`
3. Replace `{TOKEN}` with your bot token
4. Find your chat ID in the JSON response

## 🐳 Docker Quick Start

```bash
# Build image
docker build -t bus-fare-monitor .

# Run container
docker run -d \
  --name bus-monitor \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e TELEGRAM_CHAT_ID=your_chat_id \
  -v bus-data:/app/data \
  bus-fare-monitor

# View logs
docker logs -f bus-monitor
```

## 🌐 Deploy on Render

1. Push repository to GitHub
2. Go to [render.com](https://render.com)
3. Create new Web Service
4. Connect GitHub repository
5. Add environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `OPENAI_API_KEY` (optional)
6. Deploy!

## 🚀 Deploy on Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize
railway init

# Add environment variables
railway variables set TELEGRAM_BOT_TOKEN="your_token"
railway variables set TELEGRAM_CHAT_ID="your_chat_id"

# Deploy
railway up
```

## 📊 Query Fare Data

After running for some time, query the database:

```bash
python utils/query_fares.py
```

This provides an interactive menu to:
- List all monitored routes
- View latest fares
- See statistics
- Check alerts

## 🔧 Configuration Examples

### Monitor Bangalore to Chennai

```json
{
  "id": "bangalore_chennai",
  "source_city": "Bangalore",
  "destination_city": "Chennai",
  "travel_date": "2024-12-25",
  "max_budget": 1000,
  "preferred_bus_types": ["AC"],
  "alert_on_price_drop_percentage": 10,
  "minimum_seats_to_alert": 5,
  "enabled": true
}
```

### Monitor Multiple Routes

Add multiple route objects in the `routes` array in `config.json`

## 📈 Understanding Alerts

### Price Drop Alert 🎉
Sent when fare drops by configured percentage

### Low Seats Alert ⚠️
Sent when available seats drop below threshold

### Good Deal Alert 💎
Sent when AI classifies fare as "cheap"

## 🐛 Troubleshooting

### No buses found?
- Check source/destination spelling
- Ensure travel date is in future
- Check if routes are enabled

### Telegram not working?
- Verify bot token
- Verify chat ID
- Check internet connection
- Review logs in `logs/` directory

### Database issues?
- Delete `data/fares.db` to reset
- Check disk space
- Verify write permissions

## 📚 Learn More

See README.md for:
- Complete feature list
- Detailed configuration
- Database schema
- Performance optimization
- Contributing guidelines

---

**Need help?** Check the logs:
```bash
tail -f logs/bus_monitor_*.log
```
