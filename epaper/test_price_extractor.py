import unittest

# run the unit test with
# python3 -m unittest test_price_extractor.py

from PriceExtractor import PriceExtractor

class TestPriceExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = PriceExtractor(currency="usd", symbol="$")

    def test_format_price_in_millions(self):
        self.assertEqual(self.extractor.format_price(1234567), "$1.234M")
        self.assertEqual(self.extractor.format_price(999999.99), "$.999M")
        self.assertEqual(self.extractor.format_price(100000), "$.1M")

    def test_format_price_in_thousands(self):
        self.assertEqual(self.extractor.format_price(99999), "$99.99k")
        self.assertEqual(self.extractor.format_price(50000), "$50.00k")
        self.assertEqual(self.extractor.format_price(1000), "$1.00k")

    def test_format_price_below_thousand(self):
        self.assertEqual(self.extractor.format_price(999), "$999.000")
        self.assertEqual(self.extractor.format_price(123.45), "$123.000")
        self.assertEqual(self.extractor.format_price(0.99), "$0.000")

if __name__ == "__main__":
    unittest.main()