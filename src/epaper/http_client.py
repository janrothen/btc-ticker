import json

import requests

DEFAULT_TIMEOUT = 10  # seconds


class HttpClient:
    """Thin wrapper around requests that enforces a timeout and raises
    ConnectionError for any non-2xx response."""

    def __init__(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        self.timeout = timeout

    def get(self, url: str) -> str:
        return self._check(requests.get(url, timeout=self.timeout))

    def post(self, url: str, json_data: object | None = None) -> str:
        data = json.dumps(json_data) if json_data else None
        return self._check(requests.post(url, data=data, timeout=self.timeout))

    def put(self, url: str, json_data: object | None = None) -> str:
        data = json.dumps(json_data) if json_data else None
        return self._check(requests.put(url, data=data, timeout=self.timeout))

    def delete(self, url: str) -> str:
        return self._check(requests.delete(url, timeout=self.timeout))

    def _check(self, r: requests.Response) -> str:
        if not (200 <= r.status_code < 300):
            raise ConnectionError(f"\nCode: {r.status_code}\nResult: {r.text}")
        return r.text
