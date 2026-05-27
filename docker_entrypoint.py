#!/usr/bin/env python3
"""
Docker entry point script.

Handles initialization and starts the application.
"""

import os
import sys
from pathlib import Path
import asyncio
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def setup_config():
    """Setup configuration if needed."""
    config_path = Path("config.json")
    if not config_path.exists():
        print("Creating default configuration...")
        default_config = {
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
                    "enabled": True,
                }
            ],
            "scraper_settings": {
                "enable_redbus": True,
                "enable_abhibus": True,
                "browser_headless": True,
                "request_timeout": 30,
                "check_interval_minutes": 60,
                "min_delay_seconds": 2,
                "max_delay_seconds": 5,
            },
            "ai_analysis": {"enabled": True},
            "notifications": {"enabled": True, "telegram": True},
        }
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=2)


def verify_env():
    """Verify environment variables are set."""
    required_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    missing = []

    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        print(f"⚠️  Warning: Missing environment variables: {', '.join(missing)}")
        print("Notifications will be disabled.")
        return False
    return True


async def main():
    """Main entry point."""
    setup_config()
    verify_env()

    # Import after environment is set
    from main import BusFareMonitor

    monitor = BusFareMonitor("config.json")
    await monitor.run()


if __name__ == "__main__":
    asyncio.run(main())
