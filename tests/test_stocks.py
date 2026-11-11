import unittest

from src.stocks import STOCKS


class StockUniverseTests(unittest.TestCase):
    def test_stock_selector_has_at_least_100_unique_equities(self):
        symbols = [symbol for symbol, _ in STOCKS]
        self.assertGreaterEqual(len(symbols), 100)
        self.assertEqual(len(symbols), len(set(symbols)))


if __name__ == "__main__":
    unittest.main()
