import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests

from btcticker.http_client import HttpError
from btcticker.price.bitcoin_price_client import (
    MAX_RETRIES,
    RETRY_DELAY,
    BitcoinPriceClient,
)
from btcticker.price.mock import BitcoinPriceClientMock
from btcticker.price.price_extractor import PriceExtractor

FIXTURE = Path(__file__).parent / "mock_data.json"
TEST_ENDPOINT = "https://example.test/ticker"


def _make_client(side_effect=None, return_value=None, **kwargs):
    mock_http = MagicMock()
    if side_effect is not None:
        mock_http.get_json.side_effect = side_effect
    elif return_value is not None:
        mock_http.get_json.return_value = return_value
    client = BitcoinPriceClient(TEST_ENDPOINT, http_client=mock_http, **kwargs)
    return client, mock_http


class TestPriceExtractorIntegration(unittest.TestCase):
    def setUp(self) -> None:
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
        client, _ = _make_client(side_effect=side_effect)
        with patch("btcticker.price.bitcoin_price_client.time.sleep"):
            return client.retrieve_data()

    def test_http_error_returns_none(self):
        self.assertIsNone(self._run_with_error(HttpError(503, "service unavailable")))

    def test_requests_timeout_returns_none(self):
        self.assertIsNone(self._run_with_error(requests.Timeout("timed out")))

    def test_requests_exception_returns_none(self):
        self.assertIsNone(
            self._run_with_error(requests.RequestException("network error"))
        )

    def test_malformed_json_returns_none(self):
        self.assertIsNone(
            self._run_with_error(json.JSONDecodeError("bad", "not valid {", 0))
        )


class TestBitcoinPriceClientRetry(unittest.TestCase):
    def test_succeeds_on_first_attempt_without_retrying(self):
        client, _ = _make_client(return_value={"USD": {"last": 50000}})
        with patch("btcticker.price.bitcoin_price_client.time.sleep") as mock_sleep:
            result = client.retrieve_data()

        self.assertEqual(result, {"USD": {"last": 50000}})
        mock_sleep.assert_not_called()

    def test_retries_on_failure_and_returns_data_on_success(self):
        good = {"USD": {"last": 50000}}
        client, _ = _make_client(
            side_effect=[HttpError(503, "fail"), HttpError(503, "fail"), good]
        )
        with patch("btcticker.price.bitcoin_price_client.time.sleep") as mock_sleep:
            result = client.retrieve_data()

        self.assertEqual(result, good)
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_called_with(RETRY_DELAY)

    def test_exhausts_all_retries_and_returns_none(self):
        client, mock_http = _make_client(side_effect=HttpError(503, "always fails"))
        with patch("btcticker.price.bitcoin_price_client.time.sleep") as mock_sleep:
            result = client.retrieve_data()

        self.assertIsNone(result)
        self.assertEqual(mock_http.get_json.call_count, MAX_RETRIES)
        self.assertEqual(mock_sleep.call_count, MAX_RETRIES - 1)

    def test_no_sleep_after_last_failed_attempt(self):
        client, _ = _make_client(side_effect=HttpError(503, "fail"))
        with patch("btcticker.price.bitcoin_price_client.time.sleep") as mock_sleep:
            client.retrieve_data()

        self.assertEqual(mock_sleep.call_count, MAX_RETRIES - 1)

    def test_injected_max_retries_overrides_default(self):
        client, mock_http = _make_client(
            side_effect=HttpError(503, "fail"), max_retries=5
        )
        with patch("btcticker.price.bitcoin_price_client.time.sleep"):
            client.retrieve_data()
        self.assertEqual(mock_http.get_json.call_count, 5)

    def test_injected_retry_delay_overrides_default(self):
        client, _ = _make_client(
            side_effect=[HttpError(503, "fail"), {"USD": {"last": 1}}],
            retry_delay=42,
        )
        with patch("btcticker.price.bitcoin_price_client.time.sleep") as mock_sleep:
            client.retrieve_data()
        mock_sleep.assert_called_once_with(42)


if __name__ == "__main__":
    unittest.main()
