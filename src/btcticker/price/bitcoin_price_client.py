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

    def __init__(
        self,
        endpoint: str,
        http_client: HttpClient | None = None,
        max_retries: int = MAX_RETRIES,
        retry_delay: int = RETRY_DELAY,
    ) -> None:
        self._endpoint = endpoint
        self._http = http_client or HttpClient()
        self._max_retries = max_retries
        self._retry_delay = retry_delay

    def retrieve_data(self) -> dict | None:
        """Fetch price data, retrying up to max_retries times on failure.

        Returns the parsed JSON dict on success, or None if all attempts fail.
        """
        for attempt in range(1, self._max_retries + 1):
            try:
                return self._http.get_json(self._endpoint)
            except (
                HttpError,
                requests.RequestException,
                json.JSONDecodeError,
            ) as e:
                logging.warning(
                    "Price fetch attempt %d/%d failed: %s",
                    attempt,
                    self._max_retries,
                    e,
                )
            if attempt < self._max_retries:
                time.sleep(self._retry_delay)
        logging.error("All %d price fetch attempts failed", self._max_retries)
        return None
