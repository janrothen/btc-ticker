import unittest
from unittest.mock import MagicMock, patch


def _make_ticker():
    """Return a PriceTicker with a mocked Display and dummy client/extractor."""
    mock_display = MagicMock()
    mock_display.width = 250
    mock_display.height = 122

    with patch("btcticker.price_ticker.ImageFont.truetype", return_value=MagicMock()):
        from btcticker.price_ticker import PriceTicker

        ticker = PriceTicker(
            display=mock_display,
            price_client=MagicMock(),
            price_extractor=MagicMock(),
        )

    return ticker, mock_display


class TestPriceTickerStart(unittest.TestCase):
    def setUp(self) -> None:
        self.ticker, self.mock_display = _make_ticker()

    def test_start_shows_image_on_display(self):
        from btcticker.price_ticker import IMAGE_FILE

        mock_image = MagicMock()
        mock_image.size = (122, 122)
        with (
            patch(
                "btcticker.price_ticker.Image.open", return_value=mock_image
            ) as mock_open,
            patch("btcticker.price_ticker.Image.new", return_value=MagicMock()),
            patch("btcticker.price_ticker.time.sleep"),
        ):
            self.ticker.start()

        mock_open.assert_called_once_with(IMAGE_FILE)
        self.mock_display.show.assert_called_once()

    def test_start_pauses_before_price_loop(self):
        mock_image = MagicMock()
        mock_image.size = (122, 122)
        with (
            patch("btcticker.price_ticker.Image.open", return_value=mock_image),
            patch("btcticker.price_ticker.Image.new", return_value=MagicMock()),
            patch("btcticker.price_ticker.time.sleep") as mock_sleep,
        ):
            self.ticker.start()

        mock_sleep.assert_called_once_with(3)


class TestPriceTickerStop(unittest.TestCase):
    def setUp(self) -> None:
        self.ticker, self.mock_display = _make_ticker()

    def test_stop_only_shuts_down_display_once(self):
        self.ticker.stop()
        self.ticker.stop()  # second call must be a no-op
        self.assertEqual(self.mock_display.sleep.call_count, 1)

    def test_stop_sets_stopped_true(self):
        self.assertFalse(self.ticker._stopped)
        self.ticker.stop()
        self.assertTrue(self.ticker._stopped)

    def test_stop_swallows_display_errors(self):
        self.mock_display.init.side_effect = OSError("SPI error")
        try:
            self.ticker.stop()  # must not raise
        except Exception as e:
            self.fail(f"stop() raised {e}")


class TestPriceTickerRefreshTiming(unittest.TestCase):
    def setUp(self) -> None:
        self.ticker, self.mock_display = _make_ticker()

    def _run_tick(self, monotonic_values):
        with (
            patch(
                "btcticker.price_ticker.time.monotonic", side_effect=monotonic_values
            ),
            patch("btcticker.price_ticker.time.sleep"),
            patch("btcticker.price_ticker.Image.new", return_value=MagicMock()),
            patch("btcticker.price_ticker.ImageDraw.Draw", return_value=MagicMock()),
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


class TestPriceTickerTextCentering(unittest.TestCase):
    def setUp(self) -> None:
        self.ticker, _ = _make_ticker()
        self.mock_draw = MagicMock()
        self.ticker.price_extractor.formatted_price_from_data.return_value = "$84.99k"

    def test_price_drawn_at_canvas_center_with_mm_anchor(self):
        expected_x = self.ticker.display.width // 2  # 125
        expected_y = self.ticker.display.height // 2  # 61

        with (
            patch("btcticker.price_ticker.time.monotonic", return_value=9999.0),
            patch("btcticker.price_ticker.time.sleep"),
            patch("btcticker.price_ticker.Image.new", return_value=MagicMock()),
            patch("btcticker.price_ticker.ImageDraw.Draw", return_value=self.mock_draw),
        ):
            self.ticker.tick()

        self.mock_draw.text.assert_called_once()
        args, kwargs = self.mock_draw.text.call_args
        self.assertEqual(args[0], (expected_x, expected_y))
        self.assertEqual(kwargs.get("anchor"), "mm")


if __name__ == "__main__":
    unittest.main()
