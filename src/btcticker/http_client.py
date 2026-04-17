import json

import requests

DEFAULT_TIMEOUT = 10  # seconds


class HttpError(Exception):
    def __init__(self, status_code: int, body: str) -> None:
        super().__init__(f"HTTP {status_code}: {body}")
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

    def post(self, url: str, json_data: object | None = None) -> str:
        return self._check(requests.post(url, json=json_data, timeout=self.timeout))

    def put(self, url: str, json_data: object | None = None) -> str:
        return self._check(requests.put(url, json=json_data, timeout=self.timeout))

    def delete(self, url: str) -> str:
        return self._check(requests.delete(url, timeout=self.timeout))

    def _check(self, r: requests.Response) -> str:
        if not (200 <= r.status_code < 300):
            raise HttpError(r.status_code, r.text)
        return r.text
