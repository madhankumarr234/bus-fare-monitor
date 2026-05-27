"""
AbhiBus scraper implementation.

This module handles:
- Navigating AbhiBus website
- Extracting bus information
- Handling dynamic content loading
- Parsing bus details
"""

import re
from typing import List, Dict, Optional
from loguru import logger
from playwright.async_api import Page
from .base_scraper import BaseScraper


class AbhibusScraper(BaseScraper):
    """Scraper for AbhiBus platform."""

    PLATFORM_NAME = "AbhiBus"
    BASE_URL = "https://www.abhibus.com"

    async def scrape(
        self,
        source: str,
        destination: str,
        travel_date: str,
        route_id: str,
    ) -> List[Dict]:
        """
        Scrape bus fares from AbhiBus.

        Args:
            source: Source city
            destination: Destination city
            travel_date: Travel date (YYYY-MM-DD)
            route_id: Unique route identifier

        Returns:
            List of bus fare data dictionaries
        """
        logger.info(f"Scraping AbhiBus for {source} -> {destination} on {travel_date}")

        async def _scrape_internal():
            page = await self._create_page()
            try:
                # Build AbhiBus search URL
                url = self._build_search_url(source, destination, travel_date)
                logger.debug(f"Navigating to: {url}")

                # Navigate to the page
                await page.goto(url, wait_until="networkidle", timeout=30000)

                # Wait for bus results to load
                await page.wait_for_selector(
                    '[class*="bus-item"], [data-testid*="bus"]',
                    timeout=15000,
                )

                # Extract bus data
                buses = await self.extract_bus_data(page)

                return buses

            except Exception as e:
                logger.error(f"Error scraping AbhiBus: {e}")
                return []
            finally:
                await page.close()

        return await self.retry_with_backoff(_scrape_internal)

    def _build_search_url(self, source: str, destination: str, travel_date: str) -> str:
        """
        Build AbhiBus search URL.

        Args:
            source: Source city
            destination: Destination city
            travel_date: Travel date (YYYY-MM-DD)

        Returns:
            AbhiBus search URL
        """
        # Convert spaces to lowercase for URL
        source_slug = source.lower().replace(" ", "-")
        dest_slug = destination.lower().replace(" ", "-")

        url = (
            f"{self.BASE_URL}/buses/"
            f"{source_slug}-to-{dest_slug}/"
            f"{travel_date}"
        )

        return url

    async def extract_bus_data(self, page: Page) -> List[Dict]:
        """
        Extract bus data from AbhiBus page.

        Args:
            page: Playwright page object

        Returns:
            List of bus data dictionaries
        """
        buses = []

        try:
            # Wait for bus items to be present
            await page.wait_for_selector(
                '[class*="bus-item"], [data-testid*="bus"]',
                timeout=10000,
            )

            # Get all bus items
            bus_elements = await page.query_selector_all(
                '[class*="bus-item"], [data-testid*="bus"]'
            )

            logger.info(f"Found {len(bus_elements)} bus(es) on AbhiBus")

            for bus_element in bus_elements:
                try:
                    bus_data = await self._extract_single_bus(bus_element, page)
                    if bus_data:
                        buses.append(bus_data)
                except Exception as e:
                    logger.warning(f"Error extracting individual bus data: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error extracting bus data from page: {e}")

        return buses

    async def _extract_single_bus(self, bus_element, page: Page) -> Optional[Dict]:
        """
        Extract data for a single bus.

        Args:
            bus_element: Playwright element handle
            page: Playwright page object

        Returns:
            Dictionary with bus data or None
        """
        try:
            # Extract operator name
            operator_elem = await bus_element.query_selector(
                '[class*="operator"], [data-testid*="operator"]'
            )
            operator = (
                await operator_elem.text_content()
                if operator_elem
                else "Unknown"
            )

            # Extract departure time
            departure_elem = await bus_element.query_selector(
                '[class*="departure"], [data-testid*="departure"]'
            )
            departure = (
                await departure_elem.text_content()
                if departure_elem
                else "N/A"
            )

            # Extract arrival time
            arrival_elem = await bus_element.query_selector(
                '[class*="arrival"], [data-testid*="arrival"]'
            )
            arrival = (
                await arrival_elem.text_content() if arrival_elem else "N/A"
            )

            # Extract fare
            fare_elem = await bus_element.query_selector(
                '[class*="price"], [class*="fare"], [data-testid*="price"]'
            )
            fare_text = (
                await fare_elem.text_content() if fare_elem else "0"
            )
            fare = self._extract_price(fare_text)

            # Extract seats left
            seats_elem = await bus_element.query_selector(
                '[class*="seats"], [data-testid*="seats"]'
            )
            seats_text = (
                await seats_elem.text_content() if seats_elem else "0"
            )
            seats = self._extract_seats(seats_text)

            # Extract bus type
            bus_type_elem = await bus_element.query_selector(
                '[class*="type"], [data-testid*="type"]'
            )
            bus_type = (
                await bus_type_elem.text_content() if bus_type_elem else "AC"
            )

            bus_data = {
                "platform": self.PLATFORM_NAME,
                "operator_name": operator.strip(),
                "departure_time": departure.strip(),
                "arrival_time": arrival.strip(),
                "fare": fare,
                "seats_left": seats,
                "bus_type": bus_type.strip(),
            }

            return bus_data

        except Exception as e:
            logger.warning(f"Error extracting single bus data: {e}")
            return None

    @staticmethod
    def _extract_price(text: str) -> int:
        """
        Extract price from text.

        Args:
            text: Text containing price

        Returns:
            Price as integer
        """
        # Remove currency symbols and extract numbers
        numbers = re.findall(r"\d+", text.replace(",", ""))
        if numbers:
            return int(numbers[0])
        return 0

    @staticmethod
    def _extract_seats(text: str) -> int:
        """
        Extract seat count from text.

        Args:
            text: Text containing seat information

        Returns:
            Seat count as integer
        """
        numbers = re.findall(r"\d+", text)
        if numbers:
            return int(numbers[0])
        return 0
