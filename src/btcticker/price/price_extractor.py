import math

_MILLION = 1_000_000
_THOUSAND = 1_000


def _is_valid_price(value: object) -> bool:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return False
    try:
        return math.isfinite(value) and value >= 0
    except OverflowError:  # JSON integer too large to represent as a float
        return False


class PriceExtractor:
    def __init__(self, currency: str, symbol: str) -> None:
        self.currency = currency
        self.symbol = symbol

    def formatted_price_from_data(self, data: dict | None) -> str:
        if not data:
            return "N/A"
        currency_data = data.get(self.currency)
        if not currency_data:
            return "N/A"
        price = currency_data.get("last")
        if not _is_valid_price(price):
            # The payload comes from the network: a string, bool, NaN, inf or
            # negative value would otherwise crash math.floor() and put the
            # service into a restart loop.
            return "N/A"
        return self.format_price(price)

    def format_price(self, price: float) -> str:
        """Format a price for display on the e-paper screen.

        Thresholds (applied to the whole-dollar value, cents stripped):
          >= 100,000 → millions, e.g. "$1.234M" or "$0.1M"
          >=   1,000 → thousands, e.g. "$84.99k" or "$50k"
          <    1,000 → raw integer, e.g. "$999"

        Trailing zeros are stripped. Values are truncated, never rounded,
        so the display never shows a price higher than the actual value.
        """
        whole = math.floor(price)
        if whole >= 100_000:
            return f"{self.symbol}{self._compact(whole, _MILLION, decimals=3)}M"
        if whole >= 1_000:
            return f"{self.symbol}{self._compact(whole, _THOUSAND, decimals=2)}k"
        return f"{self.symbol}{whole}"

    @staticmethod
    def _compact(whole: int, unit: int, decimals: int) -> str:
        """Truncate whole/unit to `decimals` places (never round) and strip
        trailing zeros.

        Truncates with integer floor division before any float math: dividing
        first and truncating the float would drop a digit for values whose
        binary representation falls just below the decimal one (e.g. 1130/1000
        -> 1.13 -> *100 -> 112.999... -> "1.12" instead of "1.13").
        """
        scale = 10**decimals
        truncated = whole * scale // unit / scale
        return f"{truncated:.{decimals}f}".rstrip("0").rstrip(".")
