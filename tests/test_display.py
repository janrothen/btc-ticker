import sys
import types
import unittest
from unittest.mock import MagicMock


def _stub_epd_module():
    """Stub out the ARM driver so tests run on any platform."""
    mock_epd_instance = MagicMock()
    mock_epd_instance.FULL_UPDATE = "FULL_UPDATE"
    mock_epd_instance.height = 250
    mock_epd_instance.width = 122

    mod = types.ModuleType("btcticker.lib.epd2in13_V2")
    mod.EPD = MagicMock(return_value=mock_epd_instance)

    sys.modules.setdefault("btcticker.lib.epdconfig", MagicMock())
    sys.modules["btcticker.lib.epd2in13_V2"] = mod
    sys.modules.pop("btcticker.display", None)

    return mock_epd_instance


class TestDisplay(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_epd = _stub_epd_module()
        from btcticker.display import Display

        self.display = Display()

    def test_width_and_height_reflect_landscape_orientation(self):
        # EPD.height (250) becomes display width; EPD.width (122) becomes display height
        self.assertEqual(self.display.width, 250)
        self.assertEqual(self.display.height, 122)

    def test_init_calls_epd_init(self):
        self.mock_epd.init.reset_mock()
        self.display.init()
        self.mock_epd.init.assert_called_once_with("FULL_UPDATE")

    def test_clear_calls_epd_clear(self):
        self.mock_epd.Clear.reset_mock()
        self.display.clear()
        self.mock_epd.Clear.assert_called_once_with(0xFF)

    def test_show_passes_image_buffer_to_epd(self):
        fake_image = MagicMock()
        self.display.show(fake_image)
        self.mock_epd.getbuffer.assert_called_with(fake_image)
        self.mock_epd.display.assert_called_with(self.mock_epd.getbuffer.return_value)

    def test_sleep_calls_epd_sleep(self):
        self.mock_epd.sleep.reset_mock()
        self.display.sleep()
        self.mock_epd.sleep.assert_called_once()


if __name__ == "__main__":
    unittest.main()
