"""
Base scraper class with common functionality.

This module provides:
- Base class for all scrapers
- Common retry logic
- Delay handling to avoid detection
- Error handling
"""

import asyncio
import random
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from loguru import logger
from playwright.async_api import async_playwright, Browser, Page


class BaseScraper(ABC):
    """Base class for all bus fare scrapers."""

    def __init__(
        self,
        min_delay: float = 2.0,
        max_delay: float = 5.0,
        max_retries: int = 3,
        retry_delay: float = 5.0,
        headless: bool = True,
    ):
        """
        Initialize base scraper.

        Args:
            min_delay: Minimum delay between requests (seconds)
            max_delay: Maximum delay between requests (seconds)
            max_retries: Maximum number of retries for failed requests
            retry_delay: Delay between retries (seconds)
            headless: Run browser in headless mode
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.playwright = None

    async def init_browser(self) -> None:
        """Initialize Playwright browser."""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=["--disable-blink-features=AutomationControlled"],
            )
            logger.info("Browser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise

    async def close_browser(self) -> None:
        """Close Playwright browser."""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")

    async def _random_delay(self) -> None:
        """Apply random delay to avoid detection."""
        delay = random.uniform(self.min_delay, self.max_delay)
        await asyncio.sleep(delay)

    async def _create_page(self) -> Page:
        """Create a new browser page with anti-bot headers."""
        if not self.browser:
            await self.init_browser()

        page = await self.browser.new_page()

        # Set user agent and headers to mimic real browser
        await page.set_extra_http_headers(
            {
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
            }
        )

        return page

    async def retry_with_backoff(self, func, *args, **kwargs):
        """
        Retry a function with exponential backoff.

        Args:
            func: Async function to retry
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result or None if all retries fail
        """
        for attempt in range(self.max_retries):
            try:
                await self._random_delay()
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed after {self.max_retries} retries: {e}")
                    return None
                else:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)

    @abstractmethod
    async def scrape(
        self,
        source: str,
        destination: str,
        travel_date: str,
        route_id: str,
    ) -> List[Dict]:
        """
        Scrape bus fares from the platform.

        Args:
            source: Source city
            destination: Destination city
            travel_date: Travel date (YYYY-MM-DD)
            route_id: Unique route identifier

        Returns:
            List of bus fare data dictionaries
        """
        pass

    @abstractmethod
    async def extract_bus_data(self, page: Page) -> List[Dict]:
        """
        Extract bus data from page.

        Args:
            page: Playwright page object

        Returns:
            List of bus data dictionaries
        """
        pass
