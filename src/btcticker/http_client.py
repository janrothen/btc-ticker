import json

import requests

# Raising this affects the worst-case fetch time bounded by the systemd
# watchdog; see the retry constants in price/bitcoin_price_client.py.
DEFAULT_TIMEOUT = 10  # seconds

# The error message ends up in the journal; cap how much of an arbitrary
# server response body is echoed there. The full body stays on `.body`.
MAX_ERROR_BODY_CHARS = 200


class HttpError(Exception):
    def __init__(self, status_code: int, body: str) -> None:
        excerpt = body[:MAX_ERROR_BODY_CHARS]
        if len(body) > MAX_ERROR_BODY_CHARS:
            excerpt += "..."
        super().__init__(f"HTTP {status_code}: {excerpt!r}")
        self.status_code = status_code
        self.body = body


class HttpClient:
    """Thin wrapper around requests that enforces a timeout and raises
    HttpError for any non-2xx response."""

    def __init__(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        self.timeout = timeout

    def get(self, url: str) -> str:
        return self._check(requests.get(url, timeout=self.timeout))

    def get_json(self, url: str) -> object:
        """Fetch `url` and parse the response body as JSON.

        Raises HttpError on non-2xx responses, json.JSONDecodeError on
        malformed or empty bodies.
        """
        return json.loads(self.get(url))

    def _check(self, r: requests.Response) -> str:
        if not (200 <= r.status_code < 300):
            raise HttpError(r.status_code, r.text)
        return r.text
