import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from src.evaluation import calculate_price_metrics, evaluate_holdout, evaluate_walk_forward


class EvaluationMetricTests(unittest.TestCase):
    def test_metrics_use_aligned_prices_and_previous_close_for_direction(self):
        result = calculate_price_metrics(
            actual=[10, 20, 30], predicted=[11, 18, 33], previous_close=[9, 21, 29]
        )
        self.assertAlmostEqual(result["MAE"], 2.0)
        self.assertAlmostEqual(result["RMSE"], np.sqrt(14 / 3))
        self.assertAlmostEqual(result["MAPE"], 10.0)
        self.assertAlmostEqual(result["Directional Accuracy"], 100.0)

    def test_mape_excludes_prices_close_to_zero(self):
        result = calculate_price_metrics(actual=[10, 0], predicted=[11, 1], previous_close=[9, 1])
        self.assertEqual(result["mape_count"], 1)
        self.assertAlmostEqual(result["MAPE"], 10.0)

    def test_test_dates_follow_decision_dates_and_test_rows_are_not_fit(self):
        dates = pd.bdate_range("2024-01-01", periods=121)
        closes = 100 * (1.01 ** np.arange(len(dates)))
        prices = pd.DataFrame({"Close": closes}, index=dates)
        decision_dates = dates[:-1]
        returns = closes[1:] / closes[:-1] - 1
        frame = pd.DataFrame({"Feature": closes[:-1], "Target": returns}, index=decision_dates)

        fitted_sizes = []

        class FixedReturnModel:
            def fit(self, x, y):
                fitted_sizes.append(len(y))
                return self

            def predict(self, x):
                return np.full(len(x), .01)

        with patch("src.evaluation._candidate_models", return_value={"Test model": FixedReturnModel}):
            evaluation = evaluate_holdout(frame, prices)

        self.assertEqual(evaluation["model_key"], "Test model")
        self.assertEqual(evaluation["test_count"], 24)
        self.assertEqual(fitted_sizes, [78, 96])
        self.assertEqual(pd.Timestamp(evaluation["rows"]["Date"].iloc[0]), dates[97])
        self.assertAlmostEqual(evaluation["rows"]["Actual close"].iloc[0], closes[97])

    def test_evaluation_keeps_a_trained_model_even_when_validation_baseline_wins(self):
        dates = pd.bdate_range("2024-01-01", periods=121)
        closes = 100 * (1.01 ** np.arange(len(dates)))
        prices = pd.DataFrame({"Close": closes}, index=dates)
        frame = pd.DataFrame({"Feature": closes[:-1], "Target": closes[1:] / closes[:-1] - 1}, index=dates[:-1])

        class ZeroReturnModel:
            def fit(self, x, y):
                return self

            def predict(self, x):
                return np.zeros(len(x))

        with patch("src.evaluation._candidate_models", return_value={"Zero-return model": ZeroReturnModel}):
            evaluation = evaluate_holdout(frame, prices)
        self.assertEqual(evaluation["model_key"], "Zero-return model")
        self.assertAlmostEqual(evaluation["metrics"]["MAE"], evaluation["baseline_metrics"]["MAE"])

    def test_short_history_returns_clear_error(self):
        dates = pd.bdate_range("2024-01-01", periods=40)
        frame = pd.DataFrame({"Feature": np.arange(39), "Target": np.zeros(39)}, index=dates[:-1])
        prices = pd.DataFrame({"Close": np.arange(40) + 100}, index=dates)
        with self.assertRaisesRegex(ValueError, "not_enough_history"):
            evaluate_holdout(frame, prices)

    def test_walk_forward_uses_multiple_non_overlapping_test_windows(self):
        dates = pd.bdate_range("2024-01-01", periods=181)
        returns = .002 + .004*np.sin(np.arange(181)/5)
        closes = 100*np.cumprod(1+returns)
        prices = pd.DataFrame({"Close":closes},index=dates)
        frame = pd.DataFrame({"Feature":closes[:-1],"Target":closes[1:]/closes[:-1]-1},index=dates[:-1])

        class FixedModel:
            def fit(self,x,y):
                return self
            def predict(self,x):
                return np.full(len(x),.002)

        with patch("src.evaluation._candidate_models",return_value={"Fixed model":FixedModel}):
            result=evaluate_walk_forward(frame,prices)
        self.assertGreaterEqual(result["fold_count"],3)
        self.assertEqual(result["test_count"],len(result["rows"]))
        self.assertEqual(result["rows"]["Date"].nunique(),result["test_count"])
        self.assertIn("Mean-return baseline",result["rows"].columns)


if __name__ == "__main__":
    unittest.main()
