"""
Telegram notification handler.

This module handles:
- Sending alerts via Telegram
- Formatting messages
- Error handling for notification delivery
- Async notification sending
"""

from typing import Optional
from loguru import logger
from telegram import Bot
from telegram.error import TelegramError


class TelegramNotifier:
    """Handle Telegram notifications."""

    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize Telegram notifier.

        Args:
            bot_token: Telegram bot token
            chat_id: Telegram chat ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = Bot(token=bot_token)

    async def send_price_drop_alert(
        self,
        operator: str,
        platform: str,
        source: str,
        destination: str,
        old_fare: int,
        new_fare: int,
        percentage_drop: float,
    ) -> bool:
        """
        Send price drop alert.

        Args:
            operator: Bus operator name
            platform: Platform name (RedBus/AbhiBus)
            source: Source city
            destination: Destination city
            old_fare: Previous fare
            new_fare: Current fare
            percentage_drop: Percentage drop

        Returns:
            True if sent successfully
        """
        try:
            message = (
                f"🎉 *Price Drop Alert!*\n\n"
                f"*{operator}* on *{platform}*\n"
                f"📍 {source} → {destination}\n\n"
                f"💰 *Previous:* ₹{old_fare}\n"
                f"💰 *Current:* ₹{new_fare}\n"
                f"📉 *Drop:* {percentage_drop:.1f}%\n\n"
                f"_Hurry! This deal might expire soon._"
            )

            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode="Markdown",
            )

            logger.info(f"Price drop alert sent for {operator}")
            return True

        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending alert: {e}")
            return False

    async def send_low_seats_alert(
        self,
        operator: str,
        platform: str,
        source: str,
        destination: str,
        seats_left: int,
        fare: int,
    ) -> bool:
        """
        Send low seats availability alert.

        Args:
            operator: Bus operator name
            platform: Platform name
            source: Source city
            destination: Destination city
            seats_left: Number of seats remaining
            fare: Ticket fare

        Returns:
            True if sent successfully
        """
        try:
            message = (
                f"⚠️ *Limited Seats Available!*\n\n"
                f"*{operator}* on *{platform}*\n"
                f"📍 {source} → {destination}\n\n"
                f"💺 *Seats Left:* {seats_left}\n"
                f"💰 *Fare:* ₹{fare}\n\n"
                f"_Book soon before seats run out!_"
            )

            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode="Markdown",
            )

            logger.info(f"Low seats alert sent for {operator}")
            return True

        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending alert: {e}")
            return False

    async def send_good_deal_alert(
        self,
        operator: str,
        platform: str,
        source: str,
        destination: str,
        fare: int,
        classification: str,
        reasoning: str,
    ) -> bool:
        """
        Send good deal detected alert.

        Args:
            operator: Bus operator name
            platform: Platform name
            source: Source city
            destination: Destination city
            fare: Ticket fare
            classification: Fare classification (cheap/normal/expensive)
            reasoning: AI reasoning for classification

        Returns:
            True if sent successfully
        """
        try:
            emoji = "💎" if classification == "cheap" else "✅"

            message = (
                f"{emoji} *Great Deal Found!*\n\n"
                f"*{operator}* on *{platform}*\n"
                f"📍 {source} → {destination}\n\n"
                f"💰 *Fare:* ₹{fare}\n"
                f"⭐ *Rating:* {classification.upper()}\n\n"
                f"📊 *Analysis:* {reasoning}\n\n"
                f"_This looks like a good opportunity!_"
            )

            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode="Markdown",
            )

            logger.info(f"Good deal alert sent for {operator}")
            return True

        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending alert: {e}")
            return False

    async def send_summary_report(
        self,
        source: str,
        destination: str,
        travel_date: str,
        cheapest_fare: int,
        average_fare: int,
        total_buses: int,
        best_operator: Optional[str] = None,
    ) -> bool:
        """
        Send daily summary report.

        Args:
            source: Source city
            destination: Destination city
            travel_date: Travel date
            cheapest_fare: Cheapest fare found
            average_fare: Average fare
            total_buses: Total buses found
            best_operator: Best operator by fare

        Returns:
            True if sent successfully
        """
        try:
            message = (
                f"📊 *Daily Fare Report*\n\n"
                f"📍 {source} → {destination}\n"
                f"📅 {travel_date}\n\n"
                f"🚌 *Total Buses:* {total_buses}\n"
                f"💰 *Cheapest:* ₹{cheapest_fare}\n"
                f"📈 *Average:* ₹{average_fare}\n"
            )

            if best_operator:
                message += f"⭐ *Best Operator:* {best_operator}\n"

            message += f"\n_Monitor your fares continuously._"

            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode="Markdown",
            )

            logger.info("Summary report sent")
            return True

        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending alert: {e}")
            return False

    async def send_error_notification(self, error_message: str) -> bool:
        """
        Send error notification.

        Args:
            error_message: Error message to send

        Returns:
            True if sent successfully
        """
        try:
            message = (
                f"❌ *Error in Bus Fare Monitor*\n\n"
                f"{error_message}\n\n"
                f"_Please check the logs for more details._"
            )

            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode="Markdown",
            )

            logger.info("Error notification sent")
            return True

        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending alert: {e}")
            return False
