"""
Main application entry point for Bus Fare Monitor.

This module orchestrates:
- Configuration loading
- Database initialization
- Scraper setup
- Scheduler setup
- Monitoring loop
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

from database import DatabaseManager
from scraper import RedbusScaper, AbhibusScraper
from notifier import TelegramNotifier
from ai_engine import FareAnalyzer
from scheduler import TaskScheduler

# Load environment variables
load_dotenv()

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logger.add(
    "logs/bus_monitor_{time}.log",
    rotation="500 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
)

logger.info("\n" + "="*60)
logger.info("Bus Fare Monitor Started")
logger.info("="*60)


class BusFareMonitor:
    """Main application class for monitoring bus fares."""

    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the Bus Fare Monitor.

        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.db = DatabaseManager(os.getenv("DATABASE_PATH", "data/fares.db"))
        self.redbus_scraper = None
        self.abhibus_scraper = None
        self.notifier = None
        self.analyzer = FareAnalyzer(os.getenv("OPENAI_API_KEY"))
        self.scheduler = TaskScheduler()
        self.active_routes = {}

    def _load_config(self, config_path: str) -> dict:
        """
        Load configuration from JSON file.

        Args:
            config_path: Path to config file

        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in config file: {config_path}")
            raise

    async def initialize(self) -> None:
        """
        Initialize all components.
        """
        try:
            logger.info("Initializing components...")

            # Initialize database
            await self.db.init_db()
            logger.info("✓ Database initialized")

            # Initialize scrapers
            scraper_settings = self.config.get("scraper_settings", {})
            min_delay = scraper_settings.get("min_delay_seconds", 2)
            max_delay = scraper_settings.get("max_delay_seconds", 5)
            headless = scraper_settings.get("browser_headless", True)

            if scraper_settings.get("enable_redbus", True):
                self.redbus_scraper = RedbusScaper(
                    min_delay=min_delay, max_delay=max_delay, headless=headless
                )
                await self.redbus_scraper.init_browser()
                logger.info("✓ RedBus scraper initialized")

            if scraper_settings.get("enable_abhibus", True):
                self.abhibus_scraper = AbhibusScraper(
                    min_delay=min_delay, max_delay=max_delay, headless=headless
                )
                await self.abhibus_scraper.init_browser()
                logger.info("✓ AbhiBus scraper initialized")

            # Initialize notifier
            telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
            telegram_chat = os.getenv("TELEGRAM_CHAT_ID")

            if telegram_token and telegram_chat:
                self.notifier = TelegramNotifier(telegram_token, telegram_chat)
                logger.info("✓ Telegram notifier initialized")
            else:
                logger.warning(
                    "⚠ Telegram credentials not found. Notifications disabled."
                )

            logger.info("✓ All components initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise

    async def monitor_route(
        self, route: dict
    ) -> None:
        """
        Monitor a single route for fare changes.

        Args:
            route: Route configuration dictionary
        """
        if not route.get("enabled", True):
            logger.debug(f"Route {route['id']} is disabled, skipping")
            return

        route_id = route["id"]
        source = route["source_city"]
        destination = route["destination_city"]
        travel_date = route["travel_date"]
        max_budget = route.get("max_budget", float("inf"))
        preferred_types = route.get("preferred_bus_types", [])
        alert_threshold = route.get("alert_on_price_drop_percentage", 10)
        min_seats_alert = route.get("minimum_seats_to_alert", 5)

        logger.info(
            f"Monitoring route: {source} → {destination} on {travel_date}"
        )

        try:
            # Scrape from RedBus
            redbus_buses = []
            if self.redbus_scraper:
                redbus_buses = await self.redbus_scraper.scrape(
                    source, destination, travel_date, route_id
                )
                logger.info(f"RedBus: Found {len(redbus_buses)} buses")

            # Scrape from AbhiBus
            abhibus_buses = []
            if self.abhibus_scraper:
                abhibus_buses = await self.abhibus_scraper.scrape(
                    source, destination, travel_date, route_id
                )
                logger.info(f"AbhiBus: Found {len(abhibus_buses)} buses")

            all_buses = redbus_buses + abhibus_buses

            if not all_buses:
                logger.warning(f"No buses found for route {route_id}")
                return

            # Process and analyze each bus
            await self._process_buses(
                route_id,
                all_buses,
                source,
                destination,
                travel_date,
                max_budget,
                preferred_types,
                alert_threshold,
                min_seats_alert,
            )

        except Exception as e:
            logger.error(f"Error monitoring route {route_id}: {e}")
            if self.notifier:
                await self.notifier.send_error_notification(
                    f"Error monitoring {source} → {destination}: {str(e)}"
                )

    async def _process_buses(
        self,
        route_id: str,
        buses: list,
        source: str,
        destination: str,
        travel_date: str,
        max_budget: float,
        preferred_types: list,
        alert_threshold: float,
        min_seats_alert: int,
    ) -> None:
        """
        Process and analyze bus data.

        Args:
            route_id: Route identifier
            buses: List of bus dictionaries
            source: Source city
            destination: Destination city
            travel_date: Travel date
            max_budget: Maximum budget
            preferred_types: Preferred bus types
            alert_threshold: Price drop threshold
            min_seats_alert: Minimum seats to alert
        """
        for bus in buses:
            try:
                # Filter by budget
                if bus["fare"] > max_budget:
                    continue

                # Filter by bus type if specified
                if preferred_types and bus["bus_type"] not in preferred_types:
                    continue

                operator = bus["operator_name"]
                platform = bus["platform"]
                fare = bus["fare"]
                seats = bus["seats_left"]

                # Store in database
                await self.db.insert_fare_data(
                    route_id=route_id,
                    platform=platform,
                    operator_name=operator,
                    departure_time=bus["departure_time"],
                    arrival_time=bus["arrival_time"],
                    fare=fare,
                    seats_left=seats,
                    bus_type=bus["bus_type"],
                    source_city=source,
                    destination_city=destination,
                    travel_date=travel_date,
                )

                # Get fare statistics for analysis
                stats = await self.db.get_statistics(route_id, travel_date)

                if stats and "error" not in stats:
                    # Classify fare using AI
                    classification, reasoning, confidence = self.analyzer.classify_fare(
                        fare, stats, bus["bus_type"]
                    )

                    # Record AI analysis
                    await self.db.record_ai_analysis(
                        route_id, operator, platform, classification, reasoning, confidence
                    )

                    # Check for price drops
                    history = await self.db.get_price_history(
                        route_id, operator, travel_date, platform
                    )

                    if len(history) > 1:
                        previous_fare = history[-2]["fare"]
                        drop_info = self.analyzer.detect_price_drop(
                            fare, previous_fare, alert_threshold
                        )

                        if drop_info["detected"]:
                            logger.info(
                                f"Price drop detected for {operator}: "
                                f"₹{previous_fare} → ₹{fare} "
                                f"({drop_info['percentage_drop']:.1f}%)"
                            )

                            await self.db.record_alert(
                                route_id,
                                operator,
                                platform,
                                "PRICE_DROP",
                                previous_fare,
                                fare,
                                drop_info["percentage_drop"],
                            )

                            if self.notifier:
                                await self.notifier.send_price_drop_alert(
                                    operator,
                                    platform,
                                    source,
                                    destination,
                                    previous_fare,
                                    fare,
                                    drop_info["percentage_drop"],
                                )

                    # Check for low seats
                    if seats <= min_seats_alert:
                        logger.warning(
                            f"Low seats alert: {operator} has only {seats} seats left"
                        )

                        await self.db.record_alert(
                            route_id,
                            operator,
                            platform,
                            "LOW_SEATS",
                            new_seats=seats,
                        )

                        if self.notifier:
                            await self.notifier.send_low_seats_alert(
                                operator, platform, source, destination, seats, fare
                            )

                    # Send deal alerts for cheap fares
                    if classification == "cheap" and confidence > 0.8:
                        logger.info(f"Good deal detected: {operator} @ ₹{fare}")

                        await self.db.record_alert(
                            route_id,
                            operator,
                            platform,
                            "GOOD_DEAL",
                            new_price=fare,
                        )

                        if self.notifier:
                            await self.notifier.send_good_deal_alert(
                                operator,
                                platform,
                                source,
                                destination,
                                fare,
                                classification,
                                reasoning,
                            )

            except Exception as e:
                logger.warning(f"Error processing bus {bus.get('operator_name')}: {e}")

    async def start_monitoring(self) -> None:
        """
        Start the monitoring scheduler.
        """
        try:
            logger.info("Starting monitoring scheduler...")

            # Add monitoring jobs for each enabled route
            for route in self.config.get("routes", []):
                if not route.get("enabled", True):
                    continue

                route_id = route["id"]
                check_interval = self.config.get("scraper_settings", {}).get(
                    "check_interval_minutes", 60
                )

                # Add job with custom interval
                job_id = f"monitor_{route_id}"
                self.scheduler.add_custom_interval_job(
                    job_id=job_id,
                    func=self.monitor_route,
                    interval_minutes=check_interval,
                    args=(route,),
                )

                logger.info(
                    f"Scheduled monitoring for route {route_id} "
                    f"every {check_interval} minutes"
                )

            # Add database cleanup job
            self.scheduler.add_custom_interval_job(
                job_id="cleanup_database",
                func=self.db.cleanup_old_data,
                interval_minutes=1440,  # Daily
                kwargs={"days_to_keep": 7},
            )

            logger.info("Scheduled database cleanup job")

            # Start scheduler
            self.scheduler.start()
            logger.info("✓ Monitoring scheduler started")

        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            raise

    async def run(self) -> None:
        """
        Main run loop.
        """
        try:
            await self.initialize()
            await self.start_monitoring()

            logger.info("\n" + "="*60)
            logger.info("Bus Fare Monitor is running...")
            logger.info("Press Ctrl+C to stop")
            logger.info("="*60 + "\n")

            # Keep the application running
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("\nShutdown signal received...")

        except Exception as e:
            logger.error(f"Fatal error: {e}")
            raise
        finally:
            await self.cleanup()

    async def cleanup(self) -> None:
        """
        Clean up resources.
        """
        logger.info("Cleaning up resources...")

        try:
            self.scheduler.stop()
            logger.info("✓ Scheduler stopped")
        except Exception as e:
            logger.warning(f"Error stopping scheduler: {e}")

        try:
            if self.redbus_scraper:
                await self.redbus_scraper.close_browser()
            logger.info("✓ RedBus scraper closed")
        except Exception as e:
            logger.warning(f"Error closing RedBus scraper: {e}")

        try:
            if self.abhibus_scraper:
                await self.abhibus_scraper.close_browser()
            logger.info("✓ AbhiBus scraper closed")
        except Exception as e:
            logger.warning(f"Error closing AbhiBus scraper: {e}")

        logger.info("\n" + "="*60)
        logger.info("Bus Fare Monitor Stopped")
        logger.info("="*60)


async def main():
    """
    Main entry point.
    """
    monitor = BusFareMonitor("config.json")
    await monitor.run()


if __name__ == "__main__":
    asyncio.run(main())
