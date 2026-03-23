class PriceExtractor:
    def __init__(self, currency: str, symbol: str) -> None:
        self.currency = currency
        self.symbol = symbol

    def formatted_price_from_data(self, data: dict) -> str:
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
        price_without_cents = self.price_without_cents(price)
        if price_without_cents >= 100_000:
            value = price_without_cents / 1_000_000
            truncated = int(value * 1000) / 1000  # 3 decimal places, no rounding
            return f'{self.symbol}{str(truncated).lstrip("0")}M'
        elif price_without_cents >= 1_000:
            value = price_without_cents / 1_000
            truncated = int(value * 100) / 100  # 2 decimal places, no rounding
            return f"{self.symbol}{truncated:.2f}k"
        else:
            truncated = int(price_without_cents * 1000) / 1000  # 3 decimal places
            return f"{self.symbol}{truncated:.3f}"

    def price_without_cents(self, price: float) -> float:
        return float(str(price).split(".", 1)[0])
