import sys
import types
import unittest
from unittest.mock import MagicMock, patch


def _make_mock_epd2in13_module():
    """Return a fake epd2in13_V2 module so the ARM .so is never loaded."""
    mod = types.ModuleType("epaper.lib.epd2in13_V2")
    mock_epd_instance = MagicMock()
    mock_epd_instance.FULL_UPDATE = "FULL_UPDATE"
    mock_epd_instance.height = 250
    mock_epd_instance.width = 122
    mod.EPD = MagicMock(return_value=mock_epd_instance)
    return mod, mock_epd_instance


def _make_ticker():
    fake_mod, mock_epd = _make_mock_epd2in13_module()
    sys.modules.setdefault("epaper.lib.epdconfig", MagicMock())
    sys.modules["epaper.lib.epd2in13_V2"] = fake_mod
    sys.modules.pop("epaper.display", None)

    with patch("epaper.display.ImageFont.truetype", return_value=MagicMock()):
        from epaper.display import PriceTicker
        ticker = PriceTicker(price_client=MagicMock(), price_extractor=MagicMock())

    return ticker, mock_epd


class TestPriceTickerStop(unittest.TestCase):
    def setUp(self):
        self.ticker, self.mock_epd = _make_ticker()

    def test_stop_only_shuts_down_hardware_once(self):
        self.ticker.stop()
        self.ticker.stop()  # second call must be a no-op
        self.assertEqual(self.mock_epd.sleep.call_count, 1)

    def test_stop_sets_stopped_true(self):
        self.assertFalse(self.ticker._stopped)
        self.ticker.stop()
        self.assertTrue(self.ticker._stopped)


class TestPriceTickerRefreshTiming(unittest.TestCase):
    def setUp(self):
        self.ticker, self.mock_epd = _make_ticker()

    def _run_tick(self, monotonic_values):
        with patch("epaper.display.time.monotonic", side_effect=monotonic_values), \
             patch("epaper.display.time.sleep"), \
             patch("epaper.display.Image.new", return_value=MagicMock()), \
             patch("epaper.display.ImageDraw.Draw", return_value=MagicMock()):
            self.ticker.tick()

    def test_first_tick_always_refreshes(self):
        """_last_refresh starts at 0.0 so the first tick always triggers a refresh."""
        self._run_tick([9999.0, 9999.0])
        self.mock_epd.display.assert_called_once()

    def test_no_refresh_within_interval(self):
        """A second tick within the interval must not trigger another refresh."""
        from epaper.display import PRICE_REFRESH_INTERVAL
        t1 = 9999.0
        self._run_tick([t1, t1])  # first tick: refreshes, sets _last_refresh = t1

        t2 = t1 + PRICE_REFRESH_INTERVAL - 1
        self._run_tick([t2])      # second tick: too early, no refresh
        self.assertEqual(self.mock_epd.display.call_count, 1)

    def test_refresh_after_interval_elapsed(self):
        """A tick after the full interval must trigger a refresh."""
        from epaper.display import PRICE_REFRESH_INTERVAL
        t1 = 9999.0
        self._run_tick([t1, t1])  # first tick refreshes

        t2 = t1 + PRICE_REFRESH_INTERVAL
        self._run_tick([t2, t2])  # second tick: interval elapsed, refreshes again
        self.assertEqual(self.mock_epd.display.call_count, 2)


class TestPriceTickerTextCentering(unittest.TestCase):
    def setUp(self):
        self.ticker, _ = _make_ticker()
        self.mock_draw = MagicMock()
        self.ticker.price_extractor.formatted_price_from_data.return_value = "$84.99k"

    def test_price_drawn_at_canvas_center_with_mm_anchor(self):
        expected_x = self.ticker.width // 2   # 125
        expected_y = self.ticker.height // 2  # 61

        with patch("epaper.display.time.monotonic", return_value=9999.0), \
             patch("epaper.display.time.sleep"), \
             patch("epaper.display.Image.new", return_value=MagicMock()), \
             patch("epaper.display.ImageDraw.Draw", return_value=self.mock_draw):
            self.ticker.tick()

        self.mock_draw.text.assert_called_once()
        args, kwargs = self.mock_draw.text.call_args
        self.assertEqual(args[0], (expected_x, expected_y))
        self.assertEqual(kwargs.get("anchor"), "mm")


if __name__ == "__main__":
    unittest.main()
