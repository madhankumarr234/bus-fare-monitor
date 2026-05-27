"""
Notification module for sending alerts.
"""

from .telegram_notifier import TelegramNotifier

__all__ = ["TelegramNotifier"]
