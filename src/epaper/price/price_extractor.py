import math

type PriceData = dict | None


class PriceExtractor:
    def __init__(self, currency: str, symbol: str) -> None:
        self.currency = currency
        self.symbol = symbol

    def formatted_price_from_data(self, data: PriceData) -> str:
        if not data:
            return "N/A"
        currency_data = data.get(self.currency)
        if not currency_data:
            return "N/A"
        price = currency_data.get("last")
        if price is None:
            return "N/A"
        return self.format_price(price)

    def format_price(self, price: float) -> str:
        """Format a price for display on the e-paper screen.

        Thresholds (applied to the whole-dollar value, cents stripped):
          >= 100,000 → millions, e.g. "$1.234M" or "$.1M"
          >=   1,000 → thousands, e.g. "$84.99k" or "$50k"
          <    1,000 → raw integer, e.g. "$999"

        Trailing zeros are stripped. Values are truncated, never rounded,
        so the display never shows a price higher than the actual value.
        """
        p = self.price_without_cents(price)
        match p:
            case p if p >= 100_000:
                value = p / 1_000_000
                truncated = (
                    int(value * 1000) / 1000
                )  # truncate to 3 decimal places, no rounding
                formatted = f"{truncated:.3f}".rstrip("0").rstrip(".")
                return f"{self.symbol}{formatted.lstrip('0')}M"
            case p if p >= 1_000:
                value = p / 1_000
                truncated = (
                    int(value * 100) / 100
                )  # truncate to 2 decimal places, no rounding
                formatted = f"{truncated:.2f}".rstrip("0").rstrip(".")
                return f"{self.symbol}{formatted}k"
            case p:
                return f"{self.symbol}{p}"

    def price_without_cents(self, price: float) -> int:
        return math.floor(price)
