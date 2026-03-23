import json
from enum import Enum

import requests


class Method(Enum):
    GET = 1
    POST = 2
    PUT = 3
    DELETE = 4


DEFAULT_TIMEOUT = 10  # seconds


class HttpClient:
    def __init__(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        self.timeout = timeout

    def get(self, url: str) -> str:
        return self._perform(Method.GET, url)

    def post(self, url: str, json_data=None) -> str:
        return self._perform(Method.POST, url, json_data)

    def put(self, url: str, json_data=None) -> str:
        return self._perform(Method.PUT, url, json_data)

    def delete(self, url: str) -> str:
        return self._perform(Method.DELETE, url)

    def _perform(self, method: Method, url: str, json_data=None) -> str:
        data = json.dumps(json_data) if json_data else None

        if method == Method.GET:
            r = requests.get(url, timeout=self.timeout)
        elif method == Method.POST:
            r = requests.post(url, data=data, timeout=self.timeout)
        elif method == Method.PUT:
            r = requests.put(url, data=data, timeout=self.timeout)
        elif method == Method.DELETE:
            r = requests.delete(url, timeout=self.timeout)

        if r.status_code not in (200, 201):
            raise ConnectionError(f"\nCode: {r.status_code}\nResult: {r.text}\nData: {data}")

        return r.text
