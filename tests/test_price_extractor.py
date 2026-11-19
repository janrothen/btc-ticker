import unittest

from btcticker.price.price_extractor import PriceExtractor


class TestPriceExtractor(unittest.TestCase):
    def setUp(self) -> None:
        self.extractor = PriceExtractor(currency="USD", symbol="$")

    def test_format_price_in_millions(self):
        self.assertEqual(self.extractor.format_price(1234567), "$1.234M")
        self.assertEqual(self.extractor.format_price(1230000), "$1.23M")
        self.assertEqual(self.extractor.format_price(1000000), "$1M")
        self.assertEqual(self.extractor.format_price(999999.99), "$0.999M")
        self.assertEqual(self.extractor.format_price(100000), "$0.1M")

    def test_format_price_in_thousands(self):
        self.assertEqual(self.extractor.format_price(99999), "$99.99k")
        self.assertEqual(self.extractor.format_price(50010), "$50.01k")
        self.assertEqual(self.extractor.format_price(50100), "$50.1k")
        self.assertEqual(self.extractor.format_price(50000), "$50k")
        self.assertEqual(self.extractor.format_price(1000), "$1k")

    def test_format_price_truncates_exactly_despite_float_representation(self):
        # Regression: truncating via float math dropped the last digit for
        # values like 1130 (1.13 * 100 -> 112.999... -> "$1.12k").
        self.assertEqual(self.extractor.format_price(1130), "$1.13k")
        self.assertEqual(self.extractor.format_price(2010), "$2.01k")
        self.assertEqual(self.extractor.format_price(1_130_000), "$1.13M")

    def test_format_price_below_thousand(self):
        self.assertEqual(self.extractor.format_price(999), "$999")
        self.assertEqual(self.extractor.format_price(123.45), "$123")
        self.assertEqual(self.extractor.format_price(0.99), "$0")

    def test_format_price_zero(self):
        self.assertEqual(self.extractor.format_price(0), "$0")

    def test_price_zero_in_data_is_displayed_not_na(self):
        self.assertEqual(
            self.extractor.formatted_price_from_data({"USD": {"last": 0}}), "$0"
        )

    def test_unknown_currency_returns_na(self):
        extractor = PriceExtractor("XYZ", "X")
        self.assertEqual(
            extractor.formatted_price_from_data({"USD": {"last": 50000}}), "N/A"
        )

    def test_invalid_last_values_return_na(self):
        # Untrusted API values must degrade to "N/A", never crash the loop.
        for bad in ["84500", True, None, float("nan"), float("inf"), -1, [1], {}]:
            with self.subTest(value=bad):
                self.assertEqual(
                    self.extractor.formatted_price_from_data({"USD": {"last": bad}}),
                    "N/A",
                )

    def test_huge_integer_price_returns_na_instead_of_crashing(self):
        self.assertEqual(
            self.extractor.formatted_price_from_data({"USD": {"last": 10**400}}),
            "N/A",
        )

    def test_large_but_representable_price_is_formatted(self):
        result = self.extractor.formatted_price_from_data({"USD": {"last": 10**300}})
        self.assertTrue(result.startswith("$") and result.endswith("M"))

    def test_missing_last_key_returns_na(self):
        extractor = PriceExtractor("USD", "$")
        self.assertEqual(
            extractor.formatted_price_from_data({"USD": {"buy": 50000}}), "N/A"
        )


if __name__ == "__main__":
    unittest.main()
