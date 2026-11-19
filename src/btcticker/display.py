from PIL import Image

try:
    from waveshare_epd import epd2in13_V2 as _epd_driver
except ModuleNotFoundError as e:
    # Only rewrite the error when the driver itself is missing; a missing
    # dependency of the driver (e.g. lgpio, spidev) keeps its own message.
    if e.name not in ("waveshare_epd", "waveshare_epd.epd2in13_V2"):
        raise
    raise ModuleNotFoundError(
        "waveshare_epd is not installed; run ./deploy/install.sh "
        '(or pip install -e ".[rpi]") on the Raspberry Pi'
    ) from e


class Display:
    """Hardware abstraction over the Waveshare epd2in13_V2 e-paper display.

    Handles initialisation, image rendering, and power management.
    The display is used in landscape orientation: physical width (250px)
    maps to EPD.height, physical height (122px) maps to EPD.width.
    """

    def __init__(self) -> None:
        self._epd = _epd_driver.EPD()
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
