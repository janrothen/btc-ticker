import logging
import random
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

_PKG_DIR = Path(__file__).parent
_LIB_DIR = _PKG_DIR / "lib"
_MEDIA_DIR = _PKG_DIR / "media"

if _LIB_DIR.exists():
    sys.path.insert(0, str(_LIB_DIR))

try:
    from waveshare_epd import epd2in13_V2
except ModuleNotFoundError:
    from epaper.lib import epd2in13_V2

FONT_FILE = _MEDIA_DIR / "UbuntuBoldItalic-Rg86.ttf"
IMAGE_FILE = _MEDIA_DIR / "bitcoin122x122_b.bmp"
FONT_SIZE = 48  # 48 points = 64 pixels
PRICE_REFRESH_INTERVAL = 300  # seconds

WHITE = 255
BLACK = 0


class PriceTicker:
    def __init__(self, price_client, price_extractor) -> None:
        self.price_client = price_client
        self.price_extractor = price_extractor
        self._running = True
        self._epd = None
        self.width = 0
        self.height = 0
        self._init_display()

    def _init_display(self) -> None:
        self._epd = epd2in13_V2.EPD()
        self._epd.init(self._epd.FULL_UPDATE)
        self._epd.Clear(0xFF)
        self.width = self._epd.height   # 250 pixels
        self.height = self._epd.width   # 122 pixels

    def start(self) -> None:
        try:
            self._display_image()
            time.sleep(3)
            self._display_price()
        except Exception as ex:
            logging.error(ex)
        finally:
            self.stop()

    def stop(self) -> None:
        logging.info("shutting down")
        if not self._running:
            return
        self._running = False
        self._epd.init(self._epd.FULL_UPDATE)
        self._epd.Clear(0xFF)
        self._epd.sleep()

    def _display_image(self) -> None:
        image = Image.open(IMAGE_FILE)
        padding_left = (self.width - image.size[0]) // 2
        frame = Image.new("1", (self.width, self.height))
        frame.paste(image, (padding_left, 0))
        self._epd.display(self._epd.getbuffer(frame))

    def _display_price(self) -> None:
        font = ImageFont.truetype(str(FONT_FILE), FONT_SIZE)
        last_refresh = 0.0  # trigger immediate refresh on first iteration

        while self._running:
            if time.monotonic() - last_refresh >= PRICE_REFRESH_INTERVAL:
                self._epd.init(self._epd.FULL_UPDATE)
                self._epd.Clear(0xFF)

                bg = random.choice([BLACK, WHITE])
                fg = WHITE if bg == BLACK else BLACK

                frame = Image.new("1", (self.width, self.height))
                draw = ImageDraw.Draw(frame)
                draw.rectangle((0, 0, self.width, self.height), fill=bg)

                price = self.price_extractor.formatted_price_from_data(
                    self.price_client.retrieve_data()
                )
                x = self.width // 2
                y = self.height // 2
                draw.text((x, y), price, font=font, fill=fg, anchor="mm")

                self._epd.display(self._epd.getbuffer(frame))
                self._epd.sleep()
                last_refresh = time.monotonic()

            time.sleep(1)
