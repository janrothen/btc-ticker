import unittest
from unittest.mock import patch

from PIL import Image

from btcticker.frame_renderer import BLACK, WHITE, FrameRenderer


class TestRenderIntro(unittest.TestCase):
    def setUp(self) -> None:
        self.renderer = FrameRenderer(width=250, height=122)

    def test_returns_frame_with_configured_dimensions(self):
        frame = self.renderer.render_intro()
        self.assertEqual(frame.size, (250, 122))

    def test_frame_is_monochrome_mode(self):
        self.assertEqual(self.renderer.render_intro().mode, "1")

    def test_logo_is_cached_across_calls(self):
        with patch(
            "btcticker.frame_renderer.Image.open", wraps=Image.open
        ) as mock_open:
            self.renderer.render_intro()
            self.renderer.render_intro()
        self.assertEqual(mock_open.call_count, 1)


class TestRenderPrice(unittest.TestCase):
    def setUp(self) -> None:
        self.renderer = FrameRenderer(width=250, height=122)

    def test_returns_frame_with_configured_dimensions(self):
        frame = self.renderer.render_price("$50k")
        self.assertEqual(frame.size, (250, 122))

    def test_frame_is_monochrome_mode(self):
        self.assertEqual(self.renderer.render_price("$50k").mode, "1")

    def test_background_is_one_of_black_or_white(self):
        # Sample center pixel with forced choice.
        with patch("btcticker.frame_renderer.random.choice", return_value=BLACK):
            frame = self.renderer.render_price("$50k")
            # corner pixel is background (text is centered)
            self.assertEqual(frame.getpixel((0, 0)), BLACK)

        with patch("btcticker.frame_renderer.random.choice", return_value=WHITE):
            frame = self.renderer.render_price("$50k")
            self.assertEqual(frame.getpixel((0, 0)), WHITE)

    def test_font_is_cached_across_calls(self):
        with patch(
            "btcticker.frame_renderer.ImageFont.truetype",
            wraps=__import__("PIL.ImageFont", fromlist=["truetype"]).truetype,
        ) as mock_truetype:
            self.renderer.render_price("$50k")
            self.renderer.render_price("$99k")
        self.assertEqual(mock_truetype.call_count, 1)


if __name__ == "__main__":
    unittest.main()
