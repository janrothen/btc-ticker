import sys
from pathlib import Path

from PIL import Image

_PKG_DIR = Path(__file__).parent
_LIB_DIR = _PKG_DIR / "lib"

# The vendored epd2in13_V2.py imports epdconfig as a bare sibling (not via the
# package), so the lib directory must be on sys.path for that import to resolve.
if _LIB_DIR.exists():
    sys.path.insert(0, str(_LIB_DIR))

try:
    from waveshare_epd import epd2in13_V2
except ModuleNotFoundError:
    import os as _os

    _real_exists = _os.path.exists

    def _patched_exists(path: str) -> bool:
        # On Linux 6.6+ (Debian Trixie) the BCM gpiomem driver was renamed
        # from gpiomem-bcm2835 to rpi-gpiomem, breaking epdconfig.py's
        # platform detection which would otherwise fall through to JetsonNano.
        if path == "/sys/bus/platform/drivers/gpiomem-bcm2835":
            return _real_exists("/sys/bus/platform/drivers/rpi-gpiomem")
        return _real_exists(path)

    _os.path.exists = _patched_exists
    try:
        from btcticker.lib import epd2in13_V2
    finally:
        _os.path.exists = _real_exists


class Display:
    """Hardware abstraction over the Waveshare epd2in13_V2 e-paper display.

    Handles initialisation, image rendering, and power management.
    The display is used in landscape orientation: physical width (250px)
    maps to EPD.height, physical height (122px) maps to EPD.width.
    """

    def __init__(self) -> None:
        self._epd = epd2in13_V2.EPD()
        self.width = self._epd.height  # 250 pixels
        self.height = self._epd.width  # 122 pixels

    def open(self) -> None:
        """Initialize the hardware and clear the screen to a known state."""
        self.init()
        self.clear()

    def init(self) -> None:
        self._epd.init(self._epd.FULL_UPDATE)

    def clear(self) -> None:
        self._epd.Clear(0xFF)

    def show(self, image: Image.Image) -> None:
        self._epd.display(self._epd.getbuffer(image))

    def sleep(self) -> None:
        self._epd.sleep()
