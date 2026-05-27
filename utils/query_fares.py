#!/usr/bin/env python3
"""
Utility script to query and display fare data.

Usage:
    python utils/query_fares.py
"""

import asyncio
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import sys


class FareDataAnalyzer:
    """Analyze and display fare data from database."""

    def __init__(self, db_path: str = "data/fares.db"):
        """Initialize analyzer."""
        self.db_path = db_path

    def get_connection(self):
        """Get database connection."""
        if not Path(self.db_path).exists():
            print(f"❌ Database not found at {self.db_path}")
            print("Run main.py first to populate the database.")
            sys.exit(1)
        return sqlite3.connect(self.db_path)

    def display_latest_fares(self, route_id: str = None, hours: int = 24):
        """Display latest fares."""
        conn = self.get_connection()
        cursor = conn.cursor()

        if route_id:
            query = f"""
                SELECT operator_name, platform, fare, seats_left, bus_type, checked_at
                FROM bus_fares
                WHERE route_id = ? AND checked_at > datetime('now', '-{hours} hours')
                ORDER BY checked_at DESC
            """
            cursor.execute(query, (route_id,))
        else:
            query = f"""
                SELECT route_id, operator_name, platform, fare, seats_left, checked_at
                FROM bus_fares
                WHERE checked_at > datetime('now', '-{hours} hours')
                ORDER BY route_id, checked_at DESC
            """
            cursor.execute(query)

        results = cursor.fetchall()

        if not results:
            print(f"No data found in last {hours} hours")
            return

        print(f"\n📊 Latest Fares (Last {hours} hours)\n")
        print("-" * 80)
        if route_id:
            print(f"{'Operator':<20} {'Platform':<10} {'Fare':<8} {'Seats':<6} {'Type':<12}")
        else:
            print(f"{'Route':<15} {'Operator':<20} {'Platform':<10} {'Fare':<8} {'Seats':<6}")
        print("-" * 80)

        for row in results:
            if route_id:
                operator, platform, fare, seats, bus_type, checked_at = row
                print(f"{operator:<20} {platform:<10} ₹{fare:<7} {seats:<6} {bus_type:<12}")
            else:
                route, operator, platform, fare, seats, checked_at = row
                print(f"{route:<15} {operator:<20} {platform:<10} ₹{fare:<7} {seats:<6}")

        print("-" * 80)
        conn.close()

    def display_statistics(self, route_id: str):
        """Display fare statistics."""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT
                MIN(fare) as min_fare,
                MAX(fare) as max_fare,
                AVG(fare) as avg_fare,
                COUNT(*) as total_records,
                COUNT(DISTINCT operator_name) as unique_operators
            FROM bus_fares
            WHERE route_id = ?
        """
        cursor.execute(query, (route_id,))
        result = cursor.fetchone()

        if not result or result[0] is None:
            print(f"No data found for route: {route_id}")
            conn.close()
            return

        min_fare, max_fare, avg_fare, total, operators = result

        print(f"\n📈 Statistics for Route: {route_id}\n")
        print(f"  Minimum Fare:     ₹{min_fare}")
        print(f"  Maximum Fare:     ₹{max_fare}")
        print(f"  Average Fare:     ₹{avg_fare:.2f}")
        print(f"  Total Records:    {total}")
        print(f"  Unique Operators: {operators}")
        print()

        conn.close()

    def display_alerts(self, hours: int = 24):
        """Display recent alerts."""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = f"""
            SELECT route_id, operator_name, platform, alert_type, old_price, new_price, 
                   price_drop_percentage, alerted_at
            FROM price_alerts
            WHERE alerted_at > datetime('now', '-{hours} hours')
            ORDER BY alerted_at DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            print(f"\n No alerts in last {hours} hours\n")
            return

        print(f"\n⚠️  Alerts (Last {hours} hours)\n")
        print("-" * 100)
        print(f"{'Route':<15} {'Operator':<20} {'Type':<15} {'From':<8} {'To':<8} {'Drop %':<8}")
        print("-" * 100)

        for row in results:
            route, operator, platform, alert_type, old_price, new_price, drop_pct, alerted_at = row
            old_p = f"₹{old_price}" if old_price else "N/A"
            new_p = f"₹{new_price}" if new_price else "N/A"
            drop = f"{drop_pct:.1f}%" if drop_pct else "N/A"
            print(f"{route:<15} {operator:<20} {alert_type:<15} {old_p:<8} {new_p:<8} {drop:<8}")

        print("-" * 100)
        conn.close()

    def list_routes(self):
        """List all routes in database."""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT DISTINCT route_id, source_city, destination_city, travel_date, COUNT(*) as records
            FROM bus_fares
            GROUP BY route_id
            ORDER BY travel_date DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            print("\n No routes in database yet. Run main.py to start monitoring.\n")
            return

        print(f"\n🗺️  Available Routes\n")
        print("-" * 80)
        print(f"{'Route ID':<15} {'From':<20} {'To':<20} {'Date':<15} {'Records':<10}")
        print("-" * 80)

        for route_id, source, destination, travel_date, records in results:
            print(f"{route_id:<15} {source:<20} {destination:<20} {travel_date:<15} {records:<10}")

        print("-" * 80)
        conn.close()


if __name__ == "__main__":
    analyzer = FareDataAnalyzer()

    print("\n" + "="*80)
    print("🚌 Bus Fare Monitor - Data Query Tool")
    print("="*80)

    while True:
        print("\n📋 Options:")
        print("  1. List all routes")
        print("  2. View latest fares for a route")
        print("  3. View fare statistics")
        print("  4. View recent alerts")
        print("  5. Exit")

        choice = input("\nSelect option (1-5): ").strip()

        if choice == "1":
            analyzer.list_routes()
        elif choice == "2":
            analyzer.list_routes()
            route_id = input("Enter route ID: ").strip()
            if route_id:
                analyzer.display_latest_fares(route_id)
        elif choice == "3":
            analyzer.list_routes()
            route_id = input("Enter route ID: ").strip()
            if route_id:
                analyzer.display_statistics(route_id)
        elif choice == "4":
            analyzer.display_alerts()
        elif choice == "5":
            print("\n👋 Goodbye!\n")
            break
        else:
            print("❌ Invalid option. Please try again.")
