from typing import Protocol


class PriceSource(Protocol):
    def retrieve_data(self) -> dict | None: ...


class PriceFormatter(Protocol):
    def formatted_price_from_data(self, data: dict | None) -> str: ...
