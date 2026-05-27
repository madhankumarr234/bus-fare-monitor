"""
Web scraper module for bus fare data.
"""

from .redbus_scraper import RedbusScaper
from .abhibus_scraper import AbhibusScraper

__all__ = ["RedbusScaper", "AbhibusScraper"]
