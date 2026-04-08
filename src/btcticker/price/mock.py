import json
from pathlib import Path


class BitcoinPriceClientMock:
    def __init__(self, fixture_path: Path) -> None:
        self._fixture_path = fixture_path

    def retrieve_data(self) -> dict:
        return json.loads(self._fixture_path.read_text())
