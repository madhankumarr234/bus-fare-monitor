# Deployment Guide

## 🚀 Quick Deployment Options

Choose your preferred deployment platform:

### Option 1: Docker (Local/Self-Hosted)
### Option 2: Render.com (Recommended - Free)
### Option 3: Railway.app
### Option 4: AWS/GCP/Azure

---

## 1️⃣ Docker Deployment (Local Server)

### Prerequisites
- Docker installed
- Docker Compose (optional)

### Deploy with Docker Compose (Easiest)

```bash
# 1. Clone repository
git clone https://github.com/madhankumarr234/bus-fare-monitor.git
cd bus-fare-monitor

# 2. Create .env file
cp .env.example .env

# 3. Edit .env with your credentials
nano .env  # or use your preferred editor

# 4. Start services
docker-compose up -d

# 5. View logs
docker-compose logs -f

# 6. Stop services
docker-compose down
```

### Deploy with Docker (Manual)

```bash
# Build image
docker build -t bus-fare-monitor:latest .

# Run container
docker run -d \
  --name bus-monitor \
  --restart unless-stopped \
  -e TELEGRAM_BOT_TOKEN="your_token_here" \
  -e TELEGRAM_CHAT_ID="your_chat_id_here" \
  -e OPENAI_API_KEY="your_key_here" \
  -v bus-data:/app/data \
  -v bus-logs:/app/logs \
  bus-fare-monitor:latest

# View logs
docker logs -f bus-monitor

# Stop container
docker stop bus-monitor
```

### Verify Deployment

```bash
# Check container status
docker ps | grep bus-monitor

# View real-time logs
docker logs -f bus-monitor

# Access database (from container)
docker exec bus-monitor ls -lah data/
```

---

## 2️⃣ Render.com Deployment (Recommended) ⭐

### Step 1: Prepare GitHub Repository

```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### Step 2: Create Render Account

1. Go to https://render.com
2. Sign up (free account)
3. Verify email

### Step 3: Create Web Service

1. Click **Dashboard** → **New Web Service**
2. Select **Public Repository** → Connect your GitHub repo
3. Configure:
   - **Name**: `bus-fare-monitor`
   - **Environment**: `Python`
   - **Build Command**: 
     ```
     pip install -r requirements.txt && playwright install chromium
     ```
   - **Start Command**: 
     ```
     python main.py
     ```

### Step 4: Add Environment Variables

1. Go to **Environment** tab
2. Add these variables:
   ```
   TELEGRAM_BOT_TOKEN = your_bot_token
   TELEGRAM_CHAT_ID = your_chat_id
   OPENAI_API_KEY = your_openai_key (optional)
   DATABASE_PATH = ./data/fares.db
   BROWSER_HEADLESS = true
   ```

### Step 5: Deploy

1. Click **Create Web Service**
2. Wait for build to complete (3-5 minutes)
3. Check logs: **Logs** tab
4. Done! ✅

### Render Cost
- **Free Tier**: $0/month
  - Limits: 750 free tier hours/month
  - Suitable for 1 instance
- **Paid**: $7+/month for guaranteed uptime

### Render Logs

```
Render Dashboard → Your Service → Logs
```

---

## 3️⃣ Railway.app Deployment

### Step 1: Install Railway CLI

```bash
curl -fsSL https://railway.app/install.sh | sh
# or
npm install -g @railway/cli
```

### Step 2: Login to Railway

```bash
railway login
```

### Step 3: Initialize Project

```bash
cd bus-fare-monitor
railway init
```

### Step 4: Add Environment Variables

```bash
railway variables set TELEGRAM_BOT_TOKEN "your_token"
railway variables set TELEGRAM_CHAT_ID "your_chat_id"
railway variables set OPENAI_API_KEY "your_key"
railway variables set DATABASE_PATH "./data/fares.db"
```

### Step 5: Deploy

```bash
railway up
```

### Step 6: Monitor

```bash
# View logs
railway logs

# View status
railway status

# Redeploy
railway redeploy
```

### Railway Cost
- **Pricing**: Pay-as-you-go
- **Free Credits**: $5/month free
- **Typical Cost**: $5-15/month for continuous monitoring

---

## 4️⃣ AWS Deployment (EC2)

### Step 1: Launch EC2 Instance

```bash
# AWS Console → Launch Instance
# Select: Ubuntu 22.04 LTS (Free tier eligible)
# Instance type: t2.micro (1GB RAM)
# Storage: 20GB (Free tier)
# Security: Allow inbound on port 22 (SSH)
```

### Step 2: Connect & Setup

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3-pip git

# Clone repository
git clone https://github.com/madhankumarr234/bus-fare-monitor.git
cd bus-fare-monitor
```

### Step 3: Install Requirements

```bash
pip install -r requirements.txt
playwright install chromium
```

### Step 4: Setup Environment

```bash
cp .env.example .env
sudo nano .env  # Add your credentials
```

### Step 5: Run with Supervisor (Keep Running)

```bash
# Install supervisor
sudo apt install supervisor -y

# Create config
sudo nano /etc/supervisor/conf.d/bus-monitor.conf
```

Add:
```ini
[program:bus-monitor]
directory=/home/ubuntu/bus-fare-monitor
command=/usr/bin/python3 /home/ubuntu/bus-fare-monitor/main.py
autostart=true
autorestart=true
user=ubuntu
stdout_logfile=/var/log/bus-monitor.log
stderr_logfile=/var/log/bus-monitor-error.log
```

Then:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start bus-monitor
```

### Step 6: Monitor

```bash
# View logs
tail -f /var/log/bus-monitor.log

# Check status
sudo supervisorctl status bus-monitor
```

### AWS Cost
- **Free Tier**: $0/month (12 months)
- **After**: ~$5-10/month (t2.micro)

---

## 5️⃣ Google Cloud Platform (GCP)

### Step 1: Create Cloud Run Service

```bash
# Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

### Step 2: Deploy via Cloud Run

```bash
# From repository directory
gcloud run deploy bus-fare-monitor \
  --source . \
  --platform managed \
  --region us-central1 \
  --memory 512Mi \
  --timeout 3600 \
  --set-env-vars=TELEGRAM_BOT_TOKEN="your_token",TELEGRAM_CHAT_ID="your_chat_id" \
  --allow-unauthenticated
```

### GCP Cost
- **Free Tier**: 2M requests/month
- **Typical**: $5-20/month

---

## 6️⃣ Heroku Deployment (Legacy)

⚠️ **Note**: Heroku discontinued free tier. Use Render or Railway instead.

---

## 📊 Deployment Comparison

| Platform | Cost | Uptime | Setup | Support |
|----------|------|--------|-------|----------|
| Docker (Self) | Infrastructure only | 99%+ | Medium | Community |
| **Render** ⭐ | Free/7+/mo | 99.99% | Easy | Good |
| Railway | 5/mo free credit | 99.9% | Easy | Good |
| AWS | Free/5-10/mo | 99.99% | Hard | Excellent |
| GCP | Free/5-20/mo | 99.99% | Medium | Excellent |
| Azure | Free/5-20/mo | 99.99% | Medium | Excellent |

---

## ✅ Verification Checklist

After deployment:

- [ ] Application started without errors
- [ ] Logs show "Monitoring scheduler started"
- [ ] Database file created in data/
- [ ] Telegram bot token is valid
- [ ] Chat ID is correct
- [ ] First monitoring job triggered
- [ ] Received test alert on Telegram
- [ ] Database contains fare records

---

## 🆘 Common Issues

### Issue: "Playwright chromium not found"

**Solution**:
```bash
playwright install chromium
```

For Docker:
```dockerfile
RUN playwright install chromium
```

### Issue: "Telegram token invalid"

**Solution**:
- Verify token from @BotFather
- Ensure no extra spaces in .env
- Restart application

### Issue: "Database locked"

**Solution**:
```bash
rm data/fares.db
# Application will recreate on next run
```

### Issue: "Memory limit exceeded"

**Solution**:
- Increase instance size
- Disable browser if not needed
- Reduce check frequency

---

## 📈 Monitoring After Deployment

### View Logs

**Render**:
```
Dashboard → Logs tab
```

**Railway**:
```bash
railway logs
```

**Docker**:
```bash
docker logs -f bus-monitor
```

**AWS EC2**:
```bash
tail -f /var/log/bus-monitor.log
```

### Check Database

```bash
# Query latest fares
python utils/query_fares.py
```

### Verify Alerts

- Check Telegram for notifications
- Query `price_alerts` table
- Review logs for errors

---

## 🔄 Update Deployment

### Docker

```bash
# Pull latest code
git pull origin main

# Rebuild image
docker build -t bus-fare-monitor:latest .

# Stop old container
docker stop bus-monitor

# Remove old container
docker rm bus-monitor

# Start new container
docker run -d --name bus-monitor ...
```

### Render

```bash
# Push to GitHub
git push origin main

# Render auto-deploys on push
# Watch deployment in Render dashboard
```

### Railway

```bash
# Push to GitHub
git push origin main

# Railway auto-deploys
# Or manually:
railway redeploy
```

---

## 💾 Backup & Recovery

### Backup Database

```bash
# Docker
docker cp bus-monitor:/app/data/fares.db ./backup/

# Local
cp data/fares.db backup/fares.db.$(date +%Y%m%d)
```

### Restore Database

```bash
# Replace corrupted database
cp backup/fares.db data/fares.db

# Restart application
docker restart bus-monitor
```

---

## 🔒 Security Best Practices

1. **Never commit secrets**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use environment variables**
   - Store API keys in platform's secret manager
   - Never hardcode credentials

3. **Enable HTTPS** (Render/Railway/GCP do this automatically)

4. **Restrict database access**
   ```bash
   chmod 600 data/fares.db
   ```

5. **Regular backups**
   - Automate weekly backups
   - Store in secure location

---

## 📞 Support & Help

- **Documentation**: See README.md
- **Issues**: GitHub Issues
- **Logs**: Check application logs
- **Community**: Start a discussion

---

**Recommended**: Start with **Render.com** (free tier, easiest setup) 🚀
