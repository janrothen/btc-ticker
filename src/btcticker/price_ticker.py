import logging
import random
import time
from functools import cached_property
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from btcticker.display import Display
from btcticker.price.protocols import PriceFormatter, PriceSource

_MEDIA_DIR = Path(__file__).parent / "media"

FONT_FILE = _MEDIA_DIR / "UbuntuBoldItalic-Rg86.ttf"
IMAGE_FILE = _MEDIA_DIR / "bitcoin122x122_b.bmp"
FONT_SIZE = 48  # 48 points = 64 pixels
DEFAULT_REFRESH_INTERVAL = 300  # seconds

WHITE = 255
BLACK = 0


class PriceTicker:
    """Orchestrates price refresh cycles on the e-paper display.

    Handles timing, price fetching, frame rendering, and delegating
    all hardware operations to the Display instance.
    """

    def __init__(
        self,
        display: Display,
        price_client: PriceSource,
        price_extractor: PriceFormatter,
        refresh_interval: int = DEFAULT_REFRESH_INTERVAL,
    ) -> None:
        self.display = display
        self.price_client = price_client
        self.price_extractor = price_extractor
        self._refresh_interval = refresh_interval
        self._stopped = False
        self._last_refresh = float("-inf")  # guarantees refresh on first tick()

    @cached_property
    def _font(self) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(str(FONT_FILE), FONT_SIZE)

    def start(self) -> None:
        """Display the intro image and pause before the price loop begins."""
        image = Image.open(IMAGE_FILE)
        padding_left = (self.display.width - image.size[0]) // 2
        frame = Image.new("1", (self.display.width, self.display.height))
        frame.paste(image, (padding_left, 0))
        self.display.show(frame)
        time.sleep(3)

    def tick(self) -> None:
        """Run one iteration of the price refresh loop. Call repeatedly from main."""
        if time.monotonic() - self._last_refresh >= self._refresh_interval:
            self.display.init()

            bg = random.choice([BLACK, WHITE])
            fg = WHITE if bg == BLACK else BLACK

            frame = Image.new("1", (self.display.width, self.display.height))
            draw = ImageDraw.Draw(frame)
            draw.rectangle((0, 0, self.display.width, self.display.height), fill=bg)

            price = self.price_extractor.formatted_price_from_data(
                self.price_client.retrieve_data()
            )
            x = self.display.width // 2
            y = self.display.height // 2
            draw.text((x, y), price, font=self._font, fill=fg, anchor="mm")

            self.display.show(frame)
            self.display.sleep()
            self._last_refresh = time.monotonic()
        else:
            time.sleep(1)

    def stop(self) -> None:
        if self._stopped:
            return
        self._stopped = True
        logging.info("shutting down")
        try:
            self.display.init()
            self.display.clear()
            self.display.sleep()
        except Exception:
            logging.exception("display shutdown failed")
