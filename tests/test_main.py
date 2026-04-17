import sys
import types
import unittest
from unittest.mock import MagicMock, PropertyMock, call, patch

# Stub hardware drivers before btcticker.__main__ is imported.
# btcticker.__main__ has module-level `from btcticker.display import Display`, which
# in turn loads the vendored epd2in13_V2 driver that requires Pi hardware.
sys.modules.setdefault("btcticker.lib.epdconfig", MagicMock())
if "btcticker.lib.epd2in13_V2" not in sys.modules:
    _epd_mod = types.ModuleType("btcticker.lib.epd2in13_V2")
    _epd_mod.EPD = MagicMock()
    sys.modules["btcticker.lib.epd2in13_V2"] = _epd_mod
sys.modules.pop("btcticker.display", None)
sys.modules.pop("btcticker.__main__", None)


_DEFAULT_CONFIG = {
    "bitcoin": {"price": {"service_endpoint": "https://example.test/ticker"}}
}


def _run_main(
    mock_ticker,
    mock_shutdown,
    mock_sd_notify,
    extra_config=None,
    mock_display_cls=None,
    mock_price_client_cls=None,
):
    cfg = extra_config if extra_config is not None else _DEFAULT_CONFIG
    display_cls = mock_display_cls or MagicMock()
    price_client_cls = mock_price_client_cls or MagicMock()
    with (
        patch("btcticker.__main__.Display", display_cls),
        patch("btcticker.__main__.BitcoinPriceClient", price_client_cls),
        patch("btcticker.__main__.PriceExtractor"),
        patch("btcticker.__main__.PriceTicker", return_value=mock_ticker),
        patch("btcticker.__main__.GracefulShutdown", return_value=mock_shutdown),
        patch("btcticker.__main__.sd_notify", mock_sd_notify),
        patch("btcticker.__main__.config", return_value=cfg),
    ):
        from btcticker.__main__ import main

        main()


class TestMain(unittest.TestCase):
    def setUp(self):
        self.mock_ticker = MagicMock()
        self.mock_sd_notify = MagicMock()
        self.mock_shutdown = MagicMock()

    def _run(self, kill_now_sequence, **kwargs):
        type(self.mock_shutdown).kill_now = PropertyMock(side_effect=kill_now_sequence)
        _run_main(self.mock_ticker, self.mock_shutdown, self.mock_sd_notify, **kwargs)

    def test_ticker_start_is_called(self):
        self._run([True])
        self.mock_ticker.start.assert_called_once()

    def test_display_opened_before_ticker_start(self):
        mock_display_cls = MagicMock()
        mock_display = mock_display_cls.return_value
        type(self.mock_shutdown).kill_now = PropertyMock(return_value=True)
        _run_main(
            self.mock_ticker,
            self.mock_shutdown,
            self.mock_sd_notify,
            mock_display_cls=mock_display_cls,
        )
        mock_display.open.assert_called_once()

    def test_sd_notify_ready(self):
        self._run([True])
        self.mock_sd_notify.assert_any_call("READY=1")

    def test_tick_called_once_per_loop_iteration(self):
        self._run([False, False, True])
        self.assertEqual(self.mock_ticker.tick.call_count, 2)

    def test_watchdog_notified_each_iteration(self):
        self._run([False, False, True])
        watchdog_calls = [
            c for c in self.mock_sd_notify.call_args_list if c == call("WATCHDOG=1")
        ]
        self.assertEqual(len(watchdog_calls), 2)

    def test_ticker_stop_called_on_clean_exit(self):
        self._run([True])
        self.mock_ticker.stop.assert_called_once()

    def test_ticker_stop_called_on_exception(self):
        self.mock_ticker.start.side_effect = RuntimeError("boom")
        type(self.mock_shutdown).kill_now = PropertyMock(return_value=True)
        with self.assertRaises(SystemExit):
            _run_main(self.mock_ticker, self.mock_shutdown, self.mock_sd_notify)
        self.mock_ticker.stop.assert_called_once()

    def test_sys_exit_1_on_exception(self):
        self.mock_ticker.start.side_effect = RuntimeError("boom")
        type(self.mock_shutdown).kill_now = PropertyMock(return_value=True)
        with self.assertRaises(SystemExit) as ctx:
            _run_main(self.mock_ticker, self.mock_shutdown, self.mock_sd_notify)
        self.assertEqual(ctx.exception.code, 1)

    def test_config_currency_and_symbol_passed_to_price_extractor(self):
        cfg = {
            "bitcoin": {
                "price": {
                    "currency": "CHF",
                    "symbol": "CHF ",
                    "service_endpoint": "https://example.test/ticker",
                }
            }
        }
        mock_extractor_cls = MagicMock()
        type(self.mock_shutdown).kill_now = PropertyMock(return_value=True)
        with (
            patch("btcticker.__main__.Display"),
            patch("btcticker.__main__.BitcoinPriceClient"),
            patch("btcticker.__main__.PriceExtractor", mock_extractor_cls),
            patch("btcticker.__main__.PriceTicker", return_value=self.mock_ticker),
            patch(
                "btcticker.__main__.GracefulShutdown", return_value=self.mock_shutdown
            ),
            patch("btcticker.__main__.sd_notify", self.mock_sd_notify),
            patch("btcticker.__main__.config", return_value=cfg),
        ):
            from btcticker.__main__ import main

            main()
        mock_extractor_cls.assert_called_once_with("CHF", "CHF ")

    def test_service_endpoint_passed_to_price_client(self):
        cfg = {"bitcoin": {"price": {"service_endpoint": "https://my.ticker/api"}}}
        mock_client_cls = MagicMock()
        type(self.mock_shutdown).kill_now = PropertyMock(return_value=True)
        _run_main(
            self.mock_ticker,
            self.mock_shutdown,
            self.mock_sd_notify,
            extra_config=cfg,
            mock_price_client_cls=mock_client_cls,
        )
        mock_client_cls.assert_called_once_with("https://my.ticker/api")


if __name__ == "__main__":
    unittest.main()
