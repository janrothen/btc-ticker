import sys
from pathlib import Path

from PIL import Image

_PKG_DIR = Path(__file__).parent
_LIB_DIR = _PKG_DIR / "lib"

if _LIB_DIR.exists():
    sys.path.insert(0, str(_LIB_DIR))

try:
    from waveshare_epd import epd2in13_V2
except ModuleNotFoundError:
    from epaper.lib import epd2in13_V2


class Display:
    """Hardware abstraction over the Waveshare epd2in13_V2 e-paper display.

    Handles initialisation, image rendering, and power management.
    The display is used in landscape orientation: physical width (250px)
    maps to EPD.height, physical height (122px) maps to EPD.width.
    """

    def __init__(self) -> None:
        self._epd = epd2in13_V2.EPD()
        self._epd.init(self._epd.FULL_UPDATE)
        self._epd.Clear(0xFF)
        self.width = self._epd.height  # 250 pixels
        self.height = self._epd.width  # 122 pixels

    def init(self) -> None:
        self._epd.init(self._epd.FULL_UPDATE)

    def clear(self) -> None:
        self._epd.Clear(0xFF)

    def show(self, image: Image.Image) -> None:
        self._epd.display(self._epd.getbuffer(image))

    def sleep(self) -> None:
        self._epd.sleep()
