import sys
import types
import unittest
from unittest.mock import MagicMock, patch, call


def _make_mock_epd2in13_module():
    """Return a fake epd2in13_V2 module so the ARM .so is never loaded."""
    mod = types.ModuleType("epaper.lib.epd2in13_V2")
    mock_epd_instance = MagicMock()
    mock_epd_instance.FULL_UPDATE = "FULL_UPDATE"
    mock_epd_instance.height = 250
    mock_epd_instance.width = 122
    mod.EPD = MagicMock(return_value=mock_epd_instance)
    return mod, mock_epd_instance


class TestPriceTickerStop(unittest.TestCase):
    def setUp(self):
        # Stub out the driver modules before display.py is imported
        fake_mod, self.mock_epd = _make_mock_epd2in13_module()
        sys.modules.setdefault("epaper.lib.epdconfig", MagicMock())
        sys.modules["epaper.lib.epd2in13_V2"] = fake_mod

        # Remove cached display module so our stubs take effect
        sys.modules.pop("epaper.display", None)

        from epaper.display import PriceTicker
        self.ticker = PriceTicker(price_client=MagicMock(), price_extractor=MagicMock())

    def test_stop_only_shuts_down_hardware_once(self):
        self.ticker.stop()
        self.ticker.stop()  # second call must be a no-op

        self.assertEqual(self.mock_epd.sleep.call_count, 1)

    def test_stop_sets_running_false(self):
        self.assertTrue(self.ticker._running)
        self.ticker.stop()
        self.assertFalse(self.ticker._running)


class TestPriceTickerRefreshTiming(unittest.TestCase):
    def setUp(self):
        fake_mod, self.mock_epd = _make_mock_epd2in13_module()
        sys.modules.setdefault("epaper.lib.epdconfig", MagicMock())
        sys.modules["epaper.lib.epd2in13_V2"] = fake_mod
        sys.modules.pop("epaper.display", None)

        from epaper.display import PriceTicker
        self.mock_draw = MagicMock()
        self.ticker = PriceTicker(
            price_client=MagicMock(),
            price_extractor=MagicMock(formatted_price_from_data=MagicMock(return_value="$84.99k")),
        )

    def test_price_drawn_at_canvas_center_with_mm_anchor(self):
        expected_x = self.ticker.width // 2   # 125
        expected_y = self.ticker.height // 2  # 61

        with patch("epaper.display.time.monotonic", return_value=9999.0), \
             patch("epaper.display.time.sleep", side_effect=lambda _: self.ticker.stop()), \
             patch("epaper.display.ImageFont.truetype", return_value=MagicMock()), \
             patch("epaper.display.Image.new", return_value=MagicMock()), \
             patch("epaper.display.ImageDraw.Draw", return_value=self.mock_draw):
            self.ticker._display_price()

        self.mock_draw.text.assert_called_once()
        args, kwargs = self.mock_draw.text.call_args
        self.assertEqual(args[0], (expected_x, expected_y))
        self.assertEqual(kwargs.get("anchor"), "mm")


if __name__ == "__main__":
    unittest.main()
