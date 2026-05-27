"""
AI fare analysis engine.

This module handles:
- Fare classification (cheap/normal/expensive)
- Price trend analysis
- Deal detection
- OpenAI integration for reasoning
"""

from typing import Dict, Optional, Tuple
from loguru import logger

try:
    import openai
except ImportError:
    openai = None


class FareAnalyzer:
    """Analyze bus fares using AI and statistical methods."""

    # Fare classification thresholds (percentile-based)
    CHEAP_THRESHOLD = 0.35  # Bottom 35% are cheap
    EXPENSIVE_THRESHOLD = 0.70  # Top 30% are expensive

    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize fare analyzer.

        Args:
            openai_api_key: OpenAI API key for advanced analysis
        """
        self.openai_api_key = openai_api_key
        if openai_api_key and openai:
            openai.api_key = openai_api_key

    def classify_fare(
        self,
        current_fare: int,
        fare_stats: Dict,
        bus_type: Optional[str] = None,
    ) -> Tuple[str, str, float]:
        """
        Classify a fare as cheap, normal, or expensive.

        Args:
            current_fare: Current ticket fare
            fare_stats: Dictionary with min, max, avg, p25, p50, p75
            bus_type: Type of bus (for context)

        Returns:
            Tuple of (classification, reasoning, confidence_score)
        """
        try:
            # Use statistical percentile analysis
            min_fare = fare_stats.get("min_fare", 0)
            max_fare = fare_stats.get("max_fare", current_fare)
            p25 = fare_stats.get("p25", current_fare)
            p50 = fare_stats.get("p50", current_fare)
            p75 = fare_stats.get("p75", current_fare)

            # Normalize fare to 0-1 range
            if max_fare == min_fare:
                normalized = 0.5
            else:
                normalized = (current_fare - min_fare) / (max_fare - min_fare)

            # Classify based on percentile
            if normalized <= self.CHEAP_THRESHOLD:
                classification = "cheap"
                reasoning = f"Fare (₹{current_fare}) is in the bottom 35% of prices. Expected range: ₹{min_fare}-₹{p25}"
                confidence = min(1.0, 0.9 - (normalized * 0.2))
            elif normalized >= self.EXPENSIVE_THRESHOLD:
                classification = "expensive"
                reasoning = f"Fare (₹{current_fare}) is in the top 30% of prices. Expected range: ₹{p75}-₹{max_fare}"
                confidence = min(1.0, 0.85 + ((1 - normalized) * 0.1))
            else:
                classification = "normal"
                reasoning = f"Fare (₹{current_fare}) is within normal range. Median: ₹{p50}"
                confidence = 0.85

            logger.info(
                f"Fare classified as {classification}: {current_fare} "
                f"(confidence: {confidence:.2f})"
            )

            return classification, reasoning, confidence

        except Exception as e:
            logger.error(f"Error classifying fare: {e}")
            return "normal", "Unable to classify due to error", 0.5

    def detect_price_drop(
        self,
        current_fare: int,
        previous_fare: int,
        threshold_percentage: float = 10.0,
    ) -> Optional[Dict]:
        """
        Detect if there's a significant price drop.

        Args:
            current_fare: Current fare
            previous_fare: Previous fare
            threshold_percentage: Threshold for alert (default 10%)

        Returns:
            Dictionary with drop info if threshold exceeded, None otherwise
        """
        if previous_fare == 0:
            return None

        percentage_drop = ((previous_fare - current_fare) / previous_fare) * 100

        if percentage_drop >= threshold_percentage:
            return {
                "detected": True,
                "previous_fare": previous_fare,
                "current_fare": current_fare,
                "percentage_drop": percentage_drop,
                "savings": previous_fare - current_fare,
            }

        return {"detected": False, "percentage_drop": percentage_drop}

    def detect_seat_availability_change(
        self,
        current_seats: int,
        previous_seats: int,
        minimum_seats_threshold: int = 5,
    ) -> Optional[Dict]:
        """
        Detect significant seat availability changes.

        Args:
            current_seats: Current seat count
            previous_seats: Previous seat count
            minimum_seats_threshold: Alert if seats below this

        Returns:
            Dictionary with availability info if significant change
        """
        seats_difference = previous_seats - current_seats

        alert = False
        reason = None

        if seats_difference > 0 and current_seats <= minimum_seats_threshold:
            alert = True
            reason = "limited_seats"
        elif seats_difference > 5:  # More than 5 seats sold
            alert = True
            reason = "high_booking_rate"

        return {
            "alert": alert,
            "reason": reason,
            "previous_seats": previous_seats,
            "current_seats": current_seats,
            "seats_booked": seats_difference,
        }
