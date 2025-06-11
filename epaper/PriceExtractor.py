class PriceExtractor(object):
    def __init__(self, currency: str, symbol: str):
        self.currency = currency
        self.symbol = symbol

    def formatted_price_from_data(self, data: dict) -> str:
        if not data:
            return 'N/A'

        price = data[self.currency]['last']
        return self.format_price(price)

    def format_price(self, price: float) -> str:
        price_without_cents = self.price_without_cents(price)
        if price_without_cents >= 100_000:
            value = price_without_cents / 1_000_000
            return f'{self.symbol}{value:.3f}M'
        elif price_without_cents >= 1_000:
            value = price_without_cents / 1_000
            return f'{self.symbol}{value:.2f}k'
        else:
            return f'{self.symbol}{price_without_cents:.3f}'
    
    def price_without_cents(self, price: float) -> float:
        separator = '.'
        price_without_cents = str(price).split(separator, 1)[0]
        return float(price_without_cents)