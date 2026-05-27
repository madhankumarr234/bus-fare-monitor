#!/usr/bin/env python3
"""
Setup wizard for initial configuration.

This script helps you:
1. Create config.json
2. Set up .env file
3. Initialize database
"""

import json
import os
from pathlib import Path


def get_user_input(prompt: str, default: str = None) -> str:
    """Get user input with optional default."""
    if default:
        prompt += f" [{default}]"
    prompt += ": "
    response = input(prompt).strip()
    return response or default


def setup_telegram():
    """Setup Telegram credentials."""
    print("\n🤖 Telegram Configuration")
    print("-" * 40)
    print("Get credentials at: https://t.me/BotFather")

    token = get_user_input("Telegram Bot Token")
    chat_id = get_user_input("Telegram Chat ID")

    return token, chat_id


def setup_openai():
    """Setup OpenAI API key."""
    print("\n🤖 OpenAI Configuration (Optional)")
    print("-" * 40)
    print("Get API key at: https://platform.openai.com/api-keys")
    print("Leave blank to skip (AI analysis will use basic classification)")

    api_key = get_user_input("OpenAI API Key", "")
    return api_key


def setup_routes():
    """Setup monitoring routes."""
    print("\n🗺️  Route Configuration")
    print("-" * 40)

    routes = []
    route_count = int(get_user_input("Number of routes to monitor", "1"))

    for i in range(route_count):
        print(f"\n📍 Route {i+1}:")
        route = {
            "id": f"route_{i+1}",
            "source_city": get_user_input("Source city"),
            "destination_city": get_user_input("Destination city"),
            "travel_date": get_user_input("Travel date (YYYY-MM-DD)"),
            "max_budget": int(get_user_input("Max budget (₹)", "2000")),
            "preferred_bus_types": [
                t.strip() for t in get_user_input(
                    "Preferred bus types (comma-separated: AC,Sleeper,etc)", "AC"
                ).split(",")
            ],
            "alert_on_price_drop_percentage": int(
                get_user_input("Alert on price drop % ", "10")
            ),
            "minimum_seats_to_alert": int(get_user_input("Min seats to alert", "5")),
            "enabled": True,
        }
        routes.append(route)

    return routes


def create_env_file(telegram_token: str, chat_id: str, openai_key: str):
    """Create .env file."""
    env_content = f"""# Telegram Configuration
TELEGRAM_BOT_TOKEN={telegram_token}
TELEGRAM_CHAT_ID={chat_id}

# OpenAI Configuration
OPENAI_API_KEY={openai_key}

# Database Configuration
DATABASE_PATH=./data/fares.db

# Scraper Configuration
CHECK_INTERVAL_MINUTES=60
BROWSER_HEADLESS=true
REQUEST_TIMEOUT_SECONDS=30

# Retry Configuration
MAX_RETRIES=3
RETRY_DELAY_SECONDS=5

# Anti-bot Configuration
MIN_DELAY_SECONDS=2
MAX_DELAY_SECONDS=5
"""

    with open(".env", "w") as f:
        f.write(env_content)
    print("\n✅ .env file created")


def create_config_file(routes: list):
    """Create config.json file."""
    config = {
        "routes": routes,
        "scraper_settings": {
            "enable_redbus": True,
            "enable_abhibus": True,
            "browser_headless": True,
            "request_timeout": 30,
            "check_interval_minutes": 60,
            "min_delay_seconds": 2,
            "max_delay_seconds": 5,
        },
        "ai_analysis": {"enabled": True, "price_percentiles": {"cheap": 30, "normal": 70}},
        "notifications": {"enabled": True, "telegram": True, "console": True},
    }

    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
    print("✅ config.json file created")


def main():
    """Main setup wizard."""
    print("\n" + "="*50)
    print("🚌 Bus Fare Monitor - Setup Wizard")
    print("="*50)

    # Check if files already exist
    if Path(".env").exists() and Path("config.json").exists():
        overwrite = (
            input(
                "\n⚠️  Configuration files already exist. Overwrite? (y/n): "
            )
            .strip()
            .lower()
        )
        if overwrite != "y":
            print("Setup cancelled.")
            return

    # Get Telegram credentials
    token, chat_id = setup_telegram()

    # Get OpenAI key
    openai_key = setup_openai()

    # Get routes
    routes = setup_routes()

    # Create files
    print("\n💾 Creating configuration files...")
    create_env_file(token, chat_id, openai_key)
    create_config_file(routes)

    print("\n" + "="*50)
    print("✅ Setup Complete!")
    print("="*50)
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Install Playwright: playwright install chromium")
    print("3. Run the application: python main.py")
    print("\n")


if __name__ == "__main__":
    main()
