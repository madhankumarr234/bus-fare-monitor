# Frequently Asked Questions

## 🚀 Getting Started

### Q: Do I need to install Playwright separately?
A: No, it's in requirements.txt. Just run:
```bash
pip install -r requirements.txt
playwright install chromium
```

### Q: Can I run this on Windows?
A: Yes! Just use `venv\Scripts\activate` instead of `source venv/bin/activate`

### Q: Do I need OpenAI API key?
A: No, it's optional. The app uses statistical analysis by default. OpenAI adds advanced reasoning.

---

## 💬 Telegram Configuration

### Q: How do I get a Telegram bot token?
1. Open Telegram
2. Search for @BotFather
3. Send `/newbot`
4. Follow the prompts
5. Copy the token (format: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### Q: How do I get my Telegram chat ID?
1. Search @userinfobot on Telegram
2. Send `/start`
3. Your chat ID will be displayed

Or:
1. Send a message to your bot
2. Visit: `https://api.telegram.org/bot{TOKEN}/getUpdates` (replace {TOKEN})
3. Look for `chat.id` in the response

### Q: Why am I not receiving alerts?
- Check bot token is correct
- Verify chat ID is correct
- Ensure Telegram app is active
- Check application logs: `tail -f logs/bus_monitor_*.log`
- Test manually: `curl -X POST https://api.telegram.org/bot{TOKEN}/sendMessage -d chat_id={CHAT_ID} -d text="Test"`

---

## 🔍 Scraping & Data

### Q: Why are no buses found?
- Check city names (case-sensitive in some cases)
- Verify travel date is in the future
- Ensure routes are enabled in config.json
- Check scraper logs for errors

### Q: Why is scraping slow?
- It's intentional! Random delays prevent bot detection
- Min/max delays in config.json control speed
- Reduce delays if you want faster scraping (risk: detection)

### Q: Can I scrape multiple dates for the same route?
A: Currently no, but you can add multiple route entries for different dates:
```json
{
  "id": "route_1_dec25",
  "source_city": "Bangalore",
  "destination_city": "Chennai",
  "travel_date": "2024-12-25",
  "enabled": true
},
{
  "id": "route_1_dec26",
  "source_city": "Bangalore",
  "destination_city": "Chennai",
  "travel_date": "2024-12-26",
  "enabled": true
}
```

### Q: Can I scrape other bus websites?
A: Currently supports RedBus and AbhiBus. Other platforms require custom scrapers (contribution welcome!)

---

## 📊 Database

### Q: Where is the database stored?
A: By default: `./data/fares.db` (SQLite)

Change in .env:
```
DATABASE_PATH=/custom/path/fares.db
```

### Q: How do I view the database?
A: Use the query tool:
```bash
python utils/query_fares.py
```

Or use SQLite browser:
```bash
sqlite3 data/fares.db
# Then: SELECT * FROM bus_fares LIMIT 10;
```

### Q: How much storage do I need?
A: ~10-50 MB per month (depending on routes monitored)
- Auto-cleanup: deletes data older than 7 days
- Configure in db_manager.py: `cleanup_old_data(days_to_keep=7)`

### Q: Can I reset the database?
```bash
rm data/fares.db
# App will recreate on next run
```

---

## 🚀 Deployment

### Q: Which platform should I use?

**For beginners**: Render.com (easiest, free)
**For reliability**: AWS/GCP (better uptime)
**For budget**: Railway.app (cheap, flexible)
**For control**: Docker on your own server

### Q: Can I run multiple instances?
A: Yes, but ensure different databases:
```bash
# Instance 1
DATABASE_PATH=/data/fares1.db

# Instance 2
DATABASE_PATH=/data/fares2.db
```

### Q: How do I keep it running 24/7?
- **Render/Railway**: Automatic
- **Docker**: Use `--restart unless-stopped`
- **AWS**: Use supervisor or systemd
- **Local**: Use screen/tmux or system scheduler

### Q: Can I deploy without GitHub?
A: For Docker:
```bash
git clone ...
docker build -t bus-monitor .
docker run -d bus-monitor
```

---

## 💰 Costs

### Q: Is this free?
A: It depends on deployment:
- **Local computer**: Free
- **Render**: Free tier available
- **Railway**: $5/month free credit
- **AWS**: Free for 12 months (EC2 t2.micro)
- **GCP**: Free tier available

### Q: Will API calls cost money?
- **OpenAI API**: ~$0.001 per request (if enabled)
- **Telegram**: Free
- **Web scraping**: Free

---

## ⚙️ Configuration

### Q: How do I change check interval?
In config.json:
```json
"scraper_settings": {
  "check_interval_minutes": 60  // Change to your preferred interval
}
```

### Q: How do I filter by bus type?
In config.json:
```json
"preferred_bus_types": ["AC", "Semi-Sleeper"]  // Only monitor these types
```

### Q: How do I set price alerts?
In config.json:
```json
"alert_on_price_drop_percentage": 10  // Alert when price drops 10%
```

### Q: How many routes can I monitor?
A: Technically unlimited, but:
- 1-5 routes: Recommended
- 5-10 routes: Works fine
- 10+ routes: May need more resources

---

## 🐛 Troubleshooting

### Q: Application crashes on startup

**Solution**:
1. Check environment variables: `env | grep TELEGRAM`
2. Verify config.json is valid JSON: `python -m json.tool config.json`
3. Check logs: `tail -f logs/bus_monitor_*.log`
4. Reinstall dependencies: `pip install -r requirements.txt`

### Q: "Module not found" error

**Solution**:
```bash
pip install -r requirements.txt
pip install --upgrade playwright
playwright install chromium
```

### Q: Database locked error

**Solution**:
```bash
# Stop the application
# Delete the database
rm data/fares.db
# Restart the application
```

### Q: High memory usage

**Solution**:
- Increase swap space
- Reduce number of concurrent browsers
- Increase check interval
- Disable headless mode visualization

### Q: Slow scraping

**Solution**:
- Reduce delays in config.json
- Disable unneeded platforms
- Increase browser timeout
- Run on faster hardware

---

## 🔒 Security

### Q: Is it safe to store API keys in .env?
A: Yes, if you:
1. Never commit .env to GitHub
2. Use `.gitignore` to exclude it
3. Restrict file permissions: `chmod 600 .env`

### Q: Can the app be hacked?
A: It's as secure as your API keys. Protect:
- Telegram bot token (don't share)
- OpenAI API key (has usage limits)
- Database file (SQLite is local)

### Q: Is web scraping legal?
A: Generally yes for personal use. Check:
- Website's robots.txt
- Terms of service
- Local laws

This tool uses reasonable delays and doesn't overload servers.

---

## 📱 Mobile & Notifications

### Q: Can I get SMS alerts?
A: Not yet, but you can integrate Twilio:
1. Sign up at twilio.com
2. Modify `notifier/telegram_notifier.py`
3. Add SMS sending logic

### Q: Can I get email alerts?
A: Yes, integrate SendGrid or SMTP:
1. Create `notifier/email_notifier.py`
2. Use Python's `smtplib` or SendGrid SDK

### Q: Can I integrate with other services?
A: The notification system is modular. Add custom notifier:
```python
# Create notifier/custom_notifier.py
class CustomNotifier:
    async def send_alert(self, message):
        # Your integration here
        pass
```

---

## 🚀 Performance

### Q: How much RAM do I need?
- **Minimum**: 512 MB
- **Recommended**: 1 GB
- **Optimal**: 2+ GB

### Q: How much CPU?
- **Minimum**: Single core
- **Recommended**: Dual core
- **Optimal**: Quad core+

### Q: Can I run on Raspberry Pi?
A: Yes! But:
1. Install Python 3.9+
2. May need to compile some dependencies
3. Expect slower scraping

---

## 🤝 Contributing

### Q: Can I contribute?
A: Absolutely! Areas for contribution:
- New bus platforms (MakemyTrip, Goibibo, etc.)
- Email/SMS notifications
- Web dashboard
- Mobile app
- Price prediction ML model
- Documentation improvements

### Q: How do I report bugs?
1. GitHub Issues
2. Include error log
3. Describe steps to reproduce
4. List your environment (OS, Python version, etc.)

---

## 📚 Learning Resources

### Q: How do I learn Playwright?
- Official docs: https://playwright.dev/python/
- Async/await: https://docs.python.org/3/library/asyncio.html
- APScheduler: https://apscheduler.readthedocs.io/

### Q: How do I extend this project?
1. Fork the repository
2. Create a feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

---

## 🎯 Tips & Tricks

### Tip 1: Monitor price trends
Query the database:
```bash
python utils/query_fares.py
# Then analyze the data
```

### Tip 2: Multiple instances
Run different routes in separate containers:
```bash
docker run ... -e ROUTES="route_1,route_2"
docker run ... -e ROUTES="route_3,route_4"
```

### Tip 3: Backup regularly
```bash
# Daily backup
cp data/fares.db backups/fares_$(date +%Y%m%d).db
```

### Tip 4: Monitor resource usage
```bash
# Docker
docker stats bus-monitor

# Local
top -p $(pgrep -f main.py)
```

---

## 📞 Still have questions?

1. Check README.md
2. Review QUICKSTART.md
3. Check DEPLOYMENT.md
4. Review logs: `tail -f logs/bus_monitor_*.log`
5. Create GitHub Issue
6. Start a Discussion

---

**Happy monitoring! 🚌💨**
