import json
import unittest
from pathlib import Path
from unittest.mock import patch

import requests

from epaper.price.client import BitcoinPriceClient
from epaper.price.extractor import PriceExtractor
from epaper.price.mock import BitcoinPriceClientMock

FIXTURE = Path(__file__).parents[1] / "mock_data.json"


class TestPriceExtractorIntegration(unittest.TestCase):
    def setUp(self):
        self.data = BitcoinPriceClientMock(FIXTURE).retrieve_data()

    def test_format_usd_price(self):
        extractor = PriceExtractor("USD", "$")
        result = extractor.formatted_price_from_data(self.data)
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("$"))

    def test_format_chf_price(self):
        extractor = PriceExtractor("CHF", "CHF")
        result = extractor.formatted_price_from_data(self.data)
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("CHF"))

    def test_missing_data_returns_na(self):
        extractor = PriceExtractor("USD", "$")
        self.assertEqual(extractor.formatted_price_from_data(None), "N/A")
        self.assertEqual(extractor.formatted_price_from_data({}), "N/A")


class TestBitcoinPriceClientErrorHandling(unittest.TestCase):
    def _client_with_mock_http(self, side_effect):
        with patch("epaper.price.client.HttpClient") as MockHttp:
            MockHttp.return_value.get.side_effect = side_effect
            client = BitcoinPriceClient()
            return client.retrieve_data()

    def test_connection_error_returns_none(self):
        result = self._client_with_mock_http(ConnectionError("connection refused"))
        self.assertIsNone(result)

    def test_requests_timeout_returns_none(self):
        result = self._client_with_mock_http(requests.Timeout("timed out"))
        self.assertIsNone(result)

    def test_requests_exception_returns_none(self):
        result = self._client_with_mock_http(requests.RequestException("network error"))
        self.assertIsNone(result)

    def test_malformed_json_returns_none(self):
        with patch("epaper.price.client.HttpClient") as MockHttp:
            MockHttp.return_value.get.return_value = "not valid json {"
            client = BitcoinPriceClient()
            result = client.retrieve_data()
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
