import random
from functools import cached_property
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

_MEDIA_DIR = Path(__file__).parent / "media"

FONT_FILE = _MEDIA_DIR / "UbuntuBoldItalic-Rg86.ttf"
LOGO_FILE = _MEDIA_DIR / "bitcoin122x122_b.bmp"
FONT_SIZE = 48  # 48 points = 64 pixels

WHITE = 255
BLACK = 0


class FrameRenderer:
    """Builds monochrome frames sized for the e-paper display.

    The renderer is a pure PIL concern: it knows nothing about the
    display hardware or the price pipeline. It takes the canvas
    dimensions up front and produces ready-to-show Image objects.
    """

    def __init__(self, width: int, height: int) -> None:
        self._width = width
        self._height = height

    @cached_property
    def _font(self) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(str(FONT_FILE), FONT_SIZE)

    @cached_property
    def _logo(self) -> Image.Image:
        return Image.open(LOGO_FILE)

    def render_intro(self) -> Image.Image:
        padding_left = (self._width - self._logo.size[0]) // 2
        frame = Image.new("1", (self._width, self._height))
        frame.paste(self._logo, (padding_left, 0))
        return frame

    def render_price(self, text: str) -> Image.Image:
        bg = random.choice([BLACK, WHITE])
        fg = WHITE if bg == BLACK else BLACK

        frame = Image.new("1", (self._width, self._height))
        draw = ImageDraw.Draw(frame)
        draw.rectangle((0, 0, self._width, self._height), fill=bg)

        x = self._width // 2
        y = self._height // 2
        draw.text((x, y), text, font=self._font, fill=fg, anchor="mm")
        return frame
