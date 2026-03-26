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
        p = self.price_without_cents(price)
        match p:
            case p if p >= 100_000:
                value = p / 1_000_000
                truncated = int(value * 1000) / 1000  # truncate to 3 decimal places, no rounding
                formatted = f"{truncated:.3f}".rstrip("0").rstrip(".")
                return f'{self.symbol}{formatted.lstrip("0")}M'
            case p if p >= 1_000:
                value = p / 1_000
                truncated = int(value * 100) / 100  # truncate to 2 decimal places, no rounding
                formatted = f"{truncated:.2f}".rstrip("0").rstrip(".")
                return f"{self.symbol}{formatted}k"
            case p:
                return f"{self.symbol}{p}"

    def price_without_cents(self, price: float) -> int:
        return math.floor(price)
