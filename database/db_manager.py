"""
SQLite Database Manager for storing and retrieving bus fare data.

This module handles:
- Creating and initializing database tables
- Storing bus fare information
- Retrieving historical data for comparison
- Efficient querying with indexes
"""

import aiosqlite
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from loguru import logger


class DatabaseManager:
    """Manages SQLite database for bus fare monitoring."""

    def __init__(self, db_path: str = "data/fares.db"):
        """
        Initialize the database manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_directory()

    def _ensure_db_directory(self) -> None:
        """Ensure the database directory exists."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    async def init_db(self) -> None:
        """Initialize database tables if they don't exist."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS bus_fares (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    route_id TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    operator_name TEXT NOT NULL,
                    departure_time TEXT NOT NULL,
                    arrival_time TEXT NOT NULL,
                    fare INTEGER NOT NULL,
                    seats_left INTEGER NOT NULL,
                    bus_type TEXT NOT NULL,
                    source_city TEXT NOT NULL,
                    destination_city TEXT NOT NULL,
                    travel_date TEXT NOT NULL,
                    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(route_id, platform, operator_name, departure_time, travel_date, checked_at)
                )
                """
            )

            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS price_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    route_id TEXT NOT NULL,
                    operator_name TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    old_price INTEGER,
                    new_price INTEGER,
                    price_drop_percentage REAL,
                    old_seats INTEGER,
                    new_seats INTEGER,
                    alerted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    route_id TEXT NOT NULL,
                    operator_name TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    fare_classification TEXT NOT NULL,
                    reasoning TEXT,
                    confidence_score REAL,
                    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Create indexes for faster queries
            await db.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_route_date 
                ON bus_fares(route_id, travel_date, checked_at)
                """
            )

            await db.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_platform 
                ON bus_fares(platform, operator_name)
                """
            )

            await db.commit()
            logger.info("Database initialized successfully")

    async def insert_fare_data(
        self,
        route_id: str,
        platform: str,
        operator_name: str,
        departure_time: str,
        arrival_time: str,
        fare: int,
        seats_left: int,
        bus_type: str,
        source_city: str,
        destination_city: str,
        travel_date: str,
    ) -> bool:
        """
        Insert or update bus fare data.

        Args:
            route_id: Unique route identifier
            platform: Bus platform (RedBus/AbhiBus)
            operator_name: Bus operator name
            departure_time: Departure time
            arrival_time: Arrival time
            fare: Ticket fare
            seats_left: Number of seats available
            bus_type: Type of bus (AC, Sleeper, etc.)
            source_city: Source city
            destination_city: Destination city
            travel_date: Travel date

        Returns:
            True if inserted, False otherwise
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO bus_fares 
                    (route_id, platform, operator_name, departure_time, arrival_time,
                     fare, seats_left, bus_type, source_city, destination_city, travel_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        route_id,
                        platform,
                        operator_name,
                        departure_time,
                        arrival_time,
                        fare,
                        seats_left,
                        bus_type,
                        source_city,
                        destination_city,
                        travel_date,
                    ),
                )
                await db.commit()
                return True
        except sqlite3.IntegrityError:
            # Duplicate entry, skip
            return True
        except Exception as e:
            logger.error(f"Error inserting fare data: {e}")
            return False

    async def get_latest_fares(
        self, route_id: str, travel_date: str, hours_back: int = 1
    ) -> List[Dict]:
        """
        Get the latest fare data for comparison.

        Args:
            route_id: Route identifier
            travel_date: Travel date
            hours_back: Look back this many hours

        Returns:
            List of fare records
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                query = """
                    SELECT * FROM bus_fares 
                    WHERE route_id = ? AND travel_date = ? 
                    AND checked_at >= datetime('now', '-' || ? || ' hours')
                    ORDER BY checked_at DESC
                """
                async with db.execute(query, (route_id, travel_date, hours_back)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching latest fares: {e}")
            return []

    async def get_price_history(
        self, route_id: str, operator_name: str, travel_date: str, platform: str
    ) -> List[Dict]:
        """
        Get complete price history for a specific bus.

        Args:
            route_id: Route identifier
            operator_name: Operator name
            travel_date: Travel date
            platform: Bus platform

        Returns:
            List of historical records
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                query = """
                    SELECT * FROM bus_fares 
                    WHERE route_id = ? AND operator_name = ? 
                    AND travel_date = ? AND platform = ?
                    ORDER BY checked_at ASC
                """
                async with db.execute(query, (route_id, operator_name, travel_date, platform)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching price history: {e}")
            return []

    async def record_alert(
        self,
        route_id: str,
        operator_name: str,
        platform: str,
        alert_type: str,
        old_price: Optional[int] = None,
        new_price: Optional[int] = None,
        price_drop_percentage: Optional[float] = None,
        old_seats: Optional[int] = None,
        new_seats: Optional[int] = None,
    ) -> bool:
        """
        Record a price or availability alert.

        Args:
            route_id: Route identifier
            operator_name: Operator name
            platform: Bus platform
            alert_type: Type of alert (PRICE_DROP, LOW_SEATS, GOOD_DEAL)
            old_price: Previous price
            new_price: Current price
            price_drop_percentage: Percentage drop
            old_seats: Previous seat count
            new_seats: Current seat count

        Returns:
            True if recorded successfully
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO price_alerts 
                    (route_id, operator_name, platform, alert_type, old_price, new_price, 
                     price_drop_percentage, old_seats, new_seats)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        route_id,
                        operator_name,
                        platform,
                        alert_type,
                        old_price,
                        new_price,
                        price_drop_percentage,
                        old_seats,
                        new_seats,
                    ),
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error recording alert: {e}")
            return False

    async def get_statistics(self, route_id: str, travel_date: str) -> Dict:
        """
        Get statistical information about fares for a route.

        Args:
            route_id: Route identifier
            travel_date: Travel date

        Returns:
            Dictionary with statistics
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row

                # Get all fares
                async with db.execute(
                    """
                    SELECT fare FROM bus_fares 
                    WHERE route_id = ? AND travel_date = ?
                    ORDER BY fare
                    """,
                    (route_id, travel_date),
                ) as cursor:
                    rows = await cursor.fetchall()
                    fares = [row["fare"] for row in rows]

                if not fares:
                    return {"error": "No data available"}

                min_fare = min(fares)
                max_fare = max(fares)
                avg_fare = sum(fares) / len(fares)

                # Calculate percentiles
                sorted_fares = sorted(fares)
                n = len(sorted_fares)
                p25 = sorted_fares[int(n * 0.25)] if n > 0 else 0
                p50 = sorted_fares[int(n * 0.50)] if n > 0 else 0
                p75 = sorted_fares[int(n * 0.75)] if n > 0 else 0

                return {
                    "min_fare": min_fare,
                    "max_fare": max_fare,
                    "avg_fare": round(avg_fare, 2),
                    "p25": p25,
                    "p50": p50,
                    "p75": p75,
                    "total_records": len(fares),
                }
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {}

    async def cleanup_old_data(self, days_to_keep: int = 7) -> int:
        """
        Delete old data to keep database size manageable.

        Args:
            days_to_keep: Keep data from last N days

        Returns:
            Number of records deleted
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Delete old bus fare data
                cursor = await db.execute(
                    """
                    DELETE FROM bus_fares 
                    WHERE checked_at < datetime('now', '-' || ? || ' days')
                    """,
                    (days_to_keep,),
                )
                deleted_fares = cursor.rowcount

                # Delete old alert records
                cursor = await db.execute(
                    """
                    DELETE FROM price_alerts 
                    WHERE alerted_at < datetime('now', '-' || ? || ' days')
                    """,
                    (days_to_keep,),
                )
                deleted_alerts = cursor.rowcount

                await db.commit()
                total_deleted = deleted_fares + deleted_alerts

                logger.info(f"Cleaned up {total_deleted} old records from database")
                return total_deleted
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return 0
