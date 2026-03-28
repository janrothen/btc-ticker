import unittest

from epaper.price.price_extractor import PriceExtractor


class TestPriceExtractor(unittest.TestCase):
    def setUp(self) -> None:
        self.extractor = PriceExtractor(currency="USD", symbol="$")

    def test_format_price_in_millions(self):
        self.assertEqual(self.extractor.format_price(1234567), "$1.234M")
        self.assertEqual(self.extractor.format_price(1230000), "$1.23M")
        self.assertEqual(self.extractor.format_price(1000000), "$1M")
        self.assertEqual(self.extractor.format_price(999999.99), "$.999M")
        self.assertEqual(self.extractor.format_price(100000), "$.1M")

    def test_format_price_in_thousands(self):
        self.assertEqual(self.extractor.format_price(99999), "$99.99k")
        self.assertEqual(self.extractor.format_price(50010), "$50.01k")
        self.assertEqual(self.extractor.format_price(50100), "$50.1k")
        self.assertEqual(self.extractor.format_price(50000), "$50k")
        self.assertEqual(self.extractor.format_price(1000), "$1k")

    def test_format_price_below_thousand(self):
        self.assertEqual(self.extractor.format_price(999), "$999")
        self.assertEqual(self.extractor.format_price(123.45), "$123")
        self.assertEqual(self.extractor.format_price(0.99), "$0")

    def test_unknown_currency_returns_na(self):
        extractor = PriceExtractor("XYZ", "X")
        self.assertEqual(
            extractor.formatted_price_from_data({"USD": {"last": 50000}}), "N/A"
        )

    def test_missing_last_key_returns_na(self):
        extractor = PriceExtractor("USD", "$")
        self.assertEqual(
            extractor.formatted_price_from_data({"USD": {"buy": 50000}}), "N/A"
        )


if __name__ == "__main__":
    unittest.main()
