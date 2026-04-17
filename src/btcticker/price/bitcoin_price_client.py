import json
import logging
import time

import requests

from btcticker.http_client import HttpClient, HttpError

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds between attempts


class BitcoinPriceClient:
    """Fetches the current Bitcoin price from the configured ticker endpoint.

    The endpoint is expected to return a JSON object keyed by currency code,
    e.g. {"USD": {"last": 84500.0, ...}, "CHF": {"last": 75000.0, ...}}.
    """

    def __init__(self, endpoint: str, http_client: HttpClient | None = None) -> None:
        self._endpoint = endpoint
        self._http = http_client or HttpClient()

    def retrieve_data(self) -> dict | None:
        """Fetch price data, retrying up to MAX_RETRIES times on failure.

        Returns the parsed JSON dict on success, or None if all attempts fail.
        """
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                result = self._http.get(self._endpoint)
                if result:
                    return json.loads(result)
                logging.warning(
                    "Price fetch attempt %d/%d returned empty response",
                    attempt,
                    MAX_RETRIES,
                )
            except (
                HttpError,
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
