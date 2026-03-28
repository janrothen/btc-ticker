import json
import logging
import time

import requests

from epaper.config import config
from epaper.http_client import HttpClient

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds between attempts


class BitcoinPriceClient:
    """Fetches the current Bitcoin price from the configured ticker endpoint.

    The endpoint is expected to return a JSON object keyed by currency code,
    e.g. {"USD": {"last": 84500.0, ...}, "CHF": {"last": 75000.0, ...}}.
    """

    def retrieve_data(self) -> dict | None:
        """Fetch price data, retrying up to MAX_RETRIES times on failure.

        Returns the parsed JSON dict on success, or None if all attempts fail.
        """
        endpoint = config()["bitcoin"]["price"]["service_endpoint"]
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                result = HttpClient().get(endpoint)
                if result:
                    return json.loads(result)
            except (
                ConnectionError,
                requests.RequestException,
                json.JSONDecodeError,
            ) as e:
                logging.warning(
                    "Price fetch attempt %d/%d failed: %s", attempt, MAX_RETRIES, e
                )
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
        logging.error("All %d price fetch attempts failed", MAX_RETRIES)
        return None
