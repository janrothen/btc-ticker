import unittest
from unittest.mock import MagicMock, patch


def _make_ticker():
    """Return a PriceTicker with mocked collaborators."""
    mock_display = MagicMock()
    mock_display.width = 250
    mock_display.height = 122
    mock_renderer = MagicMock()
    mock_client = MagicMock()
    mock_extractor = MagicMock()

    from btcticker.price_ticker import PriceTicker

    ticker = PriceTicker(
        display=mock_display,
        renderer=mock_renderer,
        price_client=mock_client,
        price_extractor=mock_extractor,
    )

    return ticker, mock_display, mock_renderer, mock_client, mock_extractor


class TestPriceTickerStart(unittest.TestCase):
    def setUp(self) -> None:
        (
            self.ticker,
            self.mock_display,
            self.mock_renderer,
            _,
            _,
        ) = _make_ticker()

    def test_start_renders_intro_and_shows_on_display(self):
        intro_frame = MagicMock()
        self.mock_renderer.render_intro.return_value = intro_frame
        with patch("btcticker.price_ticker.time.sleep"):
            self.ticker.start()

        self.mock_renderer.render_intro.assert_called_once_with()
        self.mock_display.show.assert_called_once_with(intro_frame)

    def test_start_pauses_before_price_loop(self):
        from btcticker.price_ticker import INTRO_PAUSE_SECONDS

        with patch("btcticker.price_ticker.time.sleep") as mock_sleep:
            self.ticker.start()

        mock_sleep.assert_called_once_with(INTRO_PAUSE_SECONDS)


class TestPriceTickerStop(unittest.TestCase):
    def setUp(self) -> None:
        (
            self.ticker,
            self.mock_display,
            _,
            _,
            _,
        ) = _make_ticker()

    def test_stop_only_shuts_down_display_once(self):
        self.ticker.stop()
        self.ticker.stop()  # second call must be a no-op
        self.assertEqual(self.mock_display.sleep.call_count, 1)

    def test_stop_sets_stopped_true(self):
        self.assertFalse(self.ticker._stopped)
        self.ticker.stop()
        self.assertTrue(self.ticker._stopped)

    def test_stop_logs_shutdown_only_once(self):
        import logging as _logging

        with self.assertLogs("root", level=_logging.INFO) as cm:
            self.ticker.stop()
            self.ticker.stop()
        shutdown_logs = [m for m in cm.output if "shutting down" in m]
        self.assertEqual(len(shutdown_logs), 1)

    def test_stop_swallows_display_errors(self):
        self.mock_display.init.side_effect = OSError("SPI error")
        try:
            self.ticker.stop()
        except Exception as e:
            self.fail(f"stop() raised {e}")


class TestPriceTickerRefreshTiming(unittest.TestCase):
    def setUp(self) -> None:
        (
            self.ticker,
            self.mock_display,
            self.mock_renderer,
            self.mock_client,
            self.mock_extractor,
        ) = _make_ticker()

    def _run_tick(self, monotonic_values):
        with (
            patch(
                "btcticker.price_ticker.time.monotonic", side_effect=monotonic_values
            ),
            patch("btcticker.price_ticker.time.sleep"),
        ):
            self.ticker.tick()

    def test_first_tick_always_refreshes(self):
        self._run_tick([9999.0, 9999.0])
        self.mock_display.show.assert_called_once()

    def test_no_refresh_within_interval(self):
        from btcticker.price_ticker import DEFAULT_REFRESH_INTERVAL

        t1 = 9999.0
        self._run_tick([t1, t1])

        t2 = t1 + DEFAULT_REFRESH_INTERVAL - 1
        self._run_tick([t2])
        self.assertEqual(self.mock_display.show.call_count, 1)

    def test_refresh_after_interval_elapsed(self):
        from btcticker.price_ticker import DEFAULT_REFRESH_INTERVAL

        t1 = 9999.0
        self._run_tick([t1, t1])

        t2 = t1 + DEFAULT_REFRESH_INTERVAL
        self._run_tick([t2, t2])
        self.assertEqual(self.mock_display.show.call_count, 2)


class TestPriceTickerRefreshFlow(unittest.TestCase):
    def setUp(self) -> None:
        (
            self.ticker,
            self.mock_display,
            self.mock_renderer,
            self.mock_client,
            self.mock_extractor,
        ) = _make_ticker()

    def test_price_pipeline_feeds_renderer_then_display(self):
        raw = {"USD": {"last": 50000}}
        self.mock_client.retrieve_data.return_value = raw
        self.mock_extractor.formatted_price_from_data.return_value = "$50k"
        rendered_frame = MagicMock()
        self.mock_renderer.render_price.return_value = rendered_frame

        with (
            patch("btcticker.price_ticker.time.monotonic", return_value=9999.0),
            patch("btcticker.price_ticker.time.sleep"),
        ):
            self.ticker.tick()

        self.mock_extractor.formatted_price_from_data.assert_called_once_with(raw)
        self.mock_renderer.render_price.assert_called_once_with("$50k")
        self.mock_display.show.assert_called_once_with(rendered_frame)

    def test_display_hardware_sequence(self):
        """init → show → sleep on refresh."""
        self.mock_renderer.render_price.return_value = MagicMock()

        with (
            patch("btcticker.price_ticker.time.monotonic", return_value=9999.0),
            patch("btcticker.price_ticker.time.sleep"),
        ):
            self.ticker.tick()

        # Verify call ordering on the display mock.
        call_names = [c[0] for c in self.mock_display.method_calls]
        self.assertEqual(call_names, ["init", "show", "sleep"])


if __name__ == "__main__":
    unittest.main()
