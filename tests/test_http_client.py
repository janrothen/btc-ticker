import json
import unittest
from unittest.mock import MagicMock, patch

from btcticker.http_client import DEFAULT_TIMEOUT, HttpClient, HttpError


class TestHttpClientStatusCodes(unittest.TestCase):
    def _mock_response(self, status_code=200, text="{}"):
        mock = MagicMock()
        mock.status_code = status_code
        mock.text = text
        return mock

    def test_2xx_codes_do_not_raise(self):
        for code in (200, 201, 204, 206):
            with patch(
                "btcticker.http_client.requests.get",
                return_value=self._mock_response(code),
            ):
                HttpClient().get("http://example.com")  # must not raise

    def test_4xx_raises_http_error(self):
        with (
            patch(
                "btcticker.http_client.requests.get",
                return_value=self._mock_response(404),
            ),
            self.assertRaises(HttpError),
        ):
            HttpClient().get("http://example.com")

    def test_5xx_raises_http_error(self):
        with (
            patch(
                "btcticker.http_client.requests.get",
                return_value=self._mock_response(500),
            ),
            self.assertRaises(HttpError),
        ):
            HttpClient().get("http://example.com")

    def test_http_error_carries_status_code_and_body(self):
        with (
            patch(
                "btcticker.http_client.requests.get",
                return_value=self._mock_response(503, "unavailable"),
            ),
            self.assertRaises(HttpError) as ctx,
        ):
            HttpClient().get("http://example.com")
        self.assertEqual(ctx.exception.status_code, 503)
        self.assertEqual(ctx.exception.body, "unavailable")

    def test_http_error_message_does_not_start_with_newline(self):
        error = HttpError(500, "boom")
        self.assertFalse(str(error).startswith("\n"))
        self.assertIn("500", str(error))
        self.assertIn("boom", str(error))


class TestHttpClientGetJson(unittest.TestCase):
    def _mock_response(self, status_code=200, text="{}"):
        mock = MagicMock()
        mock.status_code = status_code
        mock.text = text
        return mock

    def test_parses_valid_json_body(self):
        with patch(
            "btcticker.http_client.requests.get",
            return_value=self._mock_response(200, '{"a": 1}'),
        ):
            self.assertEqual(HttpClient().get_json("http://example.com"), {"a": 1})

    def test_raises_json_decode_error_on_malformed_body(self):
        with (
            patch(
                "btcticker.http_client.requests.get",
                return_value=self._mock_response(200, "not json {"),
            ),
            self.assertRaises(json.JSONDecodeError),
        ):
            HttpClient().get_json("http://example.com")

    def test_raises_json_decode_error_on_empty_body(self):
        with (
            patch(
                "btcticker.http_client.requests.get",
                return_value=self._mock_response(200, ""),
            ),
            self.assertRaises(json.JSONDecodeError),
        ):
            HttpClient().get_json("http://example.com")

    def test_raises_http_error_on_non_2xx(self):
        with (
            patch(
                "btcticker.http_client.requests.get",
                return_value=self._mock_response(500, "boom"),
            ),
            self.assertRaises(HttpError),
        ):
            HttpClient().get_json("http://example.com")


class TestHttpClientTimeout(unittest.TestCase):
    def _mock_response(self, status_code=200, text="{}"):
        mock = MagicMock()
        mock.status_code = status_code
        mock.text = text
        return mock

    def test_get_passes_default_timeout(self):
        with patch(
            "btcticker.http_client.requests.get", return_value=self._mock_response()
        ) as mock_get:
            HttpClient().get("http://example.com")
            mock_get.assert_called_once_with(
                "http://example.com", timeout=DEFAULT_TIMEOUT
            )

    def test_post_passes_default_timeout(self):
        with patch(
            "btcticker.http_client.requests.post", return_value=self._mock_response()
        ) as mock_post:
            HttpClient().post("http://example.com")
            mock_post.assert_called_once_with(
                "http://example.com", json=None, timeout=DEFAULT_TIMEOUT
            )

    def test_put_passes_default_timeout(self):
        with patch(
            "btcticker.http_client.requests.put", return_value=self._mock_response()
        ) as mock_put:
            HttpClient().put("http://example.com")
            mock_put.assert_called_once_with(
                "http://example.com", json=None, timeout=DEFAULT_TIMEOUT
            )

    def test_delete_passes_default_timeout(self):
        with patch(
            "btcticker.http_client.requests.delete", return_value=self._mock_response()
        ) as mock_delete:
            HttpClient().delete("http://example.com")
            mock_delete.assert_called_once_with(
                "http://example.com", timeout=DEFAULT_TIMEOUT
            )

    def test_custom_timeout_is_used(self):
        with patch(
            "btcticker.http_client.requests.get", return_value=self._mock_response()
        ) as mock_get:
            HttpClient(timeout=30).get("http://example.com")
            mock_get.assert_called_once_with("http://example.com", timeout=30)

    def test_timeout_raises_connection_error(self):
        import requests as req

        with (
            patch("btcticker.http_client.requests.get", side_effect=req.Timeout),
            self.assertRaises(req.Timeout),
        ):
            HttpClient().get("http://example.com")


if __name__ == "__main__":
    unittest.main()
