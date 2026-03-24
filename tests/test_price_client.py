import json
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, call

import requests

from epaper.price.client import BitcoinPriceClient, MAX_RETRIES, RETRY_DELAY
from epaper.price.extractor import PriceExtractor
from epaper.price.mock import BitcoinPriceClientMock

FIXTURE = Path(__file__).parent / "mock_data.json"


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
    def _run_with_error(self, side_effect):
        with patch("epaper.price.client.HttpClient") as MockHttp, \
             patch("epaper.price.client.time.sleep"):
            MockHttp.return_value.get.side_effect = side_effect
            return BitcoinPriceClient().retrieve_data()

    def test_connection_error_returns_none(self):
        self.assertIsNone(self._run_with_error(ConnectionError("connection refused")))

    def test_requests_timeout_returns_none(self):
        self.assertIsNone(self._run_with_error(requests.Timeout("timed out")))

    def test_requests_exception_returns_none(self):
        self.assertIsNone(self._run_with_error(requests.RequestException("network error")))

    def test_malformed_json_returns_none(self):
        with patch("epaper.price.client.HttpClient") as MockHttp, \
             patch("epaper.price.client.time.sleep"):
            MockHttp.return_value.get.return_value = "not valid json {"
            self.assertIsNone(BitcoinPriceClient().retrieve_data())


class TestBitcoinPriceClientRetry(unittest.TestCase):
    def test_succeeds_on_first_attempt_without_retrying(self):
        good_response = json.dumps({"USD": {"last": 50000}})
        with patch("epaper.price.client.HttpClient") as MockHttp, \
             patch("epaper.price.client.time.sleep") as mock_sleep:
            MockHttp.return_value.get.return_value = good_response
            result = BitcoinPriceClient().retrieve_data()

        self.assertIsNotNone(result)
        mock_sleep.assert_not_called()

    def test_retries_on_failure_and_returns_data_on_success(self):
        good_response = json.dumps({"USD": {"last": 50000}})
        with patch("epaper.price.client.HttpClient") as MockHttp, \
             patch("epaper.price.client.time.sleep") as mock_sleep:
            # Fail twice, succeed on third attempt
            MockHttp.return_value.get.side_effect = [
                ConnectionError("fail"),
                ConnectionError("fail"),
                good_response,
            ]
            result = BitcoinPriceClient().retrieve_data()

        self.assertIsNotNone(result)
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_called_with(RETRY_DELAY)

    def test_exhausts_all_retries_and_returns_none(self):
        with patch("epaper.price.client.HttpClient") as MockHttp, \
             patch("epaper.price.client.time.sleep") as mock_sleep:
            MockHttp.return_value.get.side_effect = ConnectionError("always fails")
            result = BitcoinPriceClient().retrieve_data()

        self.assertIsNone(result)
        self.assertEqual(MockHttp.return_value.get.call_count, MAX_RETRIES)
        self.assertEqual(mock_sleep.call_count, MAX_RETRIES - 1)  # no sleep after last attempt

    def test_no_sleep_after_last_failed_attempt(self):
        with patch("epaper.price.client.HttpClient") as MockHttp, \
             patch("epaper.price.client.time.sleep") as mock_sleep:
            MockHttp.return_value.get.side_effect = ConnectionError("fail")
            BitcoinPriceClient().retrieve_data()

        # sleep called between attempts, never after the last one
        sleep_calls = mock_sleep.call_count
        self.assertEqual(sleep_calls, MAX_RETRIES - 1)


if __name__ == "__main__":
    unittest.main()
