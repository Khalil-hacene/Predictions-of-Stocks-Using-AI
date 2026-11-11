"""Offline checks for the application's analysis and data-processing modules."""

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

from src import data_loader, fundamental, ml_models, pillar_history, prediction, scoring
from src.i18n import t
from src.ml_models import _lstm_sequences
from src.preprocessing import make_feature_frame, make_pillar_feature_frame
from src.sentiment import _lexical_score, analyze_news
from src.technical import add_indicators, analyze_technical, technical_chart


def _ohlcv(rows=320):
    dates = pd.bdate_range("2024-01-01", periods=rows)
    index = np.arange(rows, dtype=float)
    close = 100 + index * 0.08 + np.sin(index / 7)
    return pd.DataFrame(
        {
            "Open": close - 0.2,
            "High": close + 1.0,
            "Low": close - 1.0,
            "Close": close,
            "Volume": 1_000_000 + index * 100,
        },
        index=dates,
    )


class FundamentalAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.info = {
            "trailingPE": 20,
            "priceToBook": 3,
            "enterpriseToEbitda": 12,
            "profitMargins": 0.12,
            "returnOnEquity": 0.15,
            "returnOnCapitalEmployed": 0.13,
            "debtToEquity": 70,
            "currentRatio": 1.8,
            "interestCoverage": 6,
            "freeCashflow": 1_000_000_000,
            "marketCap": 10_000_000_000,
            "currentPrice": 100,
            "sharesOutstanding": 100_000_000,
            "totalDebt": 1_000_000_000,
            "totalCash": 500_000_000,
            "sector": "Technology",
        }

    def test_weights_sum_to_one_and_score_is_weighted_average(self):
        result = fundamental.analyze_fundamentals(self.info, "en")

        self.assertAlmostEqual(sum(result["weights"].values()), 1.0)
        present_weight = sum(result["weights"][key] for key in result["metric_scores"])
        expected = round(
            sum(
                result["metric_scores"][key] * result["weights"][key]
                for key in result["metric_scores"]
            )
            / present_weight
        )
        self.assertEqual(result["score"], expected)

    def test_fcf_grade_uses_yield_not_absolute_cash_dollars(self):
        small_company = {**self.info, "marketCap": 20_000_000_000}
        large_company = {**self.info, "marketCap": 100_000_000_000}

        small_grade = fundamental.analyze_fundamentals(small_company)["metric_scores"][
            "freeCashflow"
        ]
        large_grade = fundamental.analyze_fundamentals(large_company)["metric_scores"][
            "freeCashflow"
        ]

        self.assertGreater(small_grade, large_grade)

    def test_fcf_is_unavailable_when_market_cap_is_missing(self):
        result = fundamental.analyze_fundamentals(
            {key: value for key, value in self.info.items() if key != "marketCap"},
            "en",
        )

        self.assertNotIn("freeCashflow", result["metric_scores"])
        self.assertIn("freeCashflow", result["missing"])

    def test_peer_grade_uses_percentile_and_lower_multiple_is_better(self):
        info = {
            **self.info,
            "trailingPE": 15,
            "sector_peer_metrics": {"trailingPE": [10, 20, 30]},
        }
        result = fundamental.analyze_fundamentals(info, "en")

        self.assertAlmostEqual(result["metric_scores"]["trailingPE"], 66.666, places=2)
        self.assertEqual(result["peer_counts"]["trailingPE"], 3)

    def test_dcf_requires_cash_and_debt_inputs_and_excludes_financials(self):
        missing_cash = {
            key: value for key, value in self.info.items() if key != "totalCash"
        }

        self.assertIsNone(fundamental._dcf_range(missing_cash))
        self.assertIsNone(
            fundamental._dcf_range({**self.info, "sector": "Financial Services"})
        )
        self.assertIsNotNone(fundamental._dcf_range(self.info))

    def test_all_supported_languages_have_the_fcf_yield_label(self):
        for language in ("en", "fr", "ar"):
            self.assertNotEqual(t(language, "fcf_yield"), "fcf_yield")


class TechnicalAnalysisTests(unittest.TestCase):
    def test_indicators_and_chart_have_expected_values(self):
        indicators = add_indicators(_ohlcv())
        latest = indicators.iloc[-1]
        analysis = analyze_technical(indicators, "en")

        self.assertTrue(np.isfinite(latest["SMA20"]))
        self.assertTrue(np.isfinite(latest["SMA200"]))
        self.assertGreaterEqual(latest["RSI"], 0)
        self.assertLessEqual(latest["RSI"], 100)
        self.assertEqual(len(analysis["table"]), 7)
        self.assertIsInstance(analysis["score"], int)
        self.assertNotEqual(analysis["table"].iloc[-1, 1], t("en", "unavailable"))
        self.assertNotEqual(analysis["table"].iloc[-2, 1], t("en", "unavailable"))
        self.assertGreaterEqual(len(technical_chart(indicators, "TEST", "en").data), 5)

    def test_short_history_does_not_invent_atr_or_support_and_resistance(self):
        analysis = analyze_technical(add_indicators(_ohlcv(5)), "en")
        readings = analysis["table"][t("en", "technical_criterion")].tolist()
        values = analysis["table"][t("en", "technical_reading")].tolist()
        unavailable = t("en", "unavailable")

        self.assertEqual(values[readings.index(t("en", "tech_atr"))], unavailable)
        self.assertEqual(values[readings.index(t("en", "tech_levels"))], unavailable)


class NewsAndDataTests(unittest.TestCase):
    def test_price_loader_reports_provider_failures_as_data_unavailable(self):
        with patch("src.data_loader.yf.Ticker") as ticker_factory:
            ticker_factory.return_value.history.side_effect = TimeoutError("offline")

            with self.assertRaises(data_loader.DataUnavailable):
                data_loader.fetch_prices("TEST")

    def test_lexical_fallback_returns_both_signal_directions(self):
        positive, positive_label = _lexical_score("Company reports strong growth", "en")
        negative, negative_label = _lexical_score(
            "Company reports a steep decline", "en"
        )

        self.assertGreater(positive, 0)
        self.assertEqual(positive_label, t("en", "positive_label"))
        self.assertLess(negative, 0)
        self.assertEqual(negative_label, t("en", "negative_label"))

    def test_article_cleaning_filters_old_filler_and_duplicate_urls(self):
        now = datetime.now(timezone.utc)
        articles = [
            {
                "title": "Apple reports strong growth",
                "publishedAt": now.isoformat(),
                "url": "https://news/a?one",
            },
            {
                "title": "ETF buys 10,000 shares",
                "publishedAt": now.isoformat(),
                "url": "https://news/b",
            },
            {
                "title": "Apple results",
                "publishedAt": "2020-01-01T00:00:00Z",
                "url": "https://news/c",
            },
            {
                "title": "Apple copied story",
                "publishedAt": now.isoformat(),
                "url": "https://news/a?two",
            },
        ]

        cleaned = data_loader._clean_articles(articles, "AAPL", "Apple")

        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned[0]["title"], "Apple reports strong growth")

    def test_sentiment_removes_fillers_and_deduplicates_articles(self):
        date = datetime.now(timezone.utc).isoformat()
        articles = [
            {
                "title": "Company beats earnings with strong growth",
                "publishedAt": date,
                "source": {"name": "Reuters"},
                "url": "https://news/item",
            },
            {
                "title": "ETF buys shares",
                "publishedAt": date,
                "url": "https://news/etf",
            },
            {
                "title": "Company beats earnings with strong growth",
                "publishedAt": date,
                "url": "https://news/item?tracking=1",
            },
        ]

        with (
            patch("src.sentiment._detect_language", return_value="en"),
            patch(
                "src.sentiment._score",
                return_value=(0.8, t("en", "positive_label"), "FinBERT", "ready"),
            ),
        ):
            result = analyze_news(articles, "en")

        self.assertEqual(result["count"], 1)
        self.assertEqual(result["positive"], 1)
        self.assertEqual(result["score"], 0.8)
        self.assertEqual(result["method"], "FinBERT")

    def test_sentiment_weights_non_english_headlines_lower(self):
        date = datetime.now(timezone.utc).isoformat()
        articles = [
            {
                "title": "English headline",
                "publishedAt": date,
                "source": {"name": "Reuters"},
                "url": "https://news/en",
            },
            {
                "title": "Titre français",
                "publishedAt": date,
                "source": {"name": "Reuters"},
                "url": "https://news/fr",
            },
        ]

        with (
            patch("src.sentiment._detect_language", side_effect=["en", "fr"]),
            patch(
                "src.sentiment._score",
                return_value=(0.6, t("en", "positive_label"), "FinBERT", "ready"),
            ),
        ):
            result = analyze_news(articles, "en")

        self.assertEqual(result["articles"][0]["language_weight"], 1.0)
        self.assertEqual(result["articles"][1]["language_weight"], 0.5)


class ForecastAndFeatureTests(unittest.TestCase):
    def test_forecast_model_name_is_available_in_all_interface_languages(self):
        for language in ("en", "fr", "ar"):
            message = t(language, "model_used", model="Random Forest")
            self.assertIn("Random Forest", message)

    def test_model_comparison_uses_chronological_folds_and_purges_horizon_labels(self):
        dates = pd.bdate_range("2024-01-01", periods=240)
        feature = np.arange(240, dtype=float)
        target = 0.01 * np.sin(feature / 8)
        frame = pd.DataFrame({"Feature": feature, "Target": target}, index=dates)
        frame.attrs["horizon"] = 3
        frame.attrs["current_features"] = pd.Series({"Feature": 240.0})

        fitted_rows = []

        class ConstantEstimator:
            def fit(self, values, labels):
                fitted_rows.append(len(labels))
                self.value = float(np.mean(labels))
                return self

            def predict(self, values):
                return np.full(len(values), self.value)

        with (
            patch(
                "src.ml_models._make_model_factories",
                return_value=(
                    ml_models._NumpyScaler,
                    {"Régression linéaire": ConstantEstimator},
                ),
            ),
            patch("src.ml_models._has_tensorflow", return_value=False),
        ):
            result = ml_models.compare_models(frame, "en")

        self.assertEqual(result["fold_count"], 5)
        self.assertEqual(result["horizon"], 3)
        self.assertEqual(result["dates"].tolist(), sorted(result["dates"].tolist()))
        self.assertEqual(len(set(result["dates"])), result["validated_rows"])
        self.assertEqual(fitted_rows[0], 117)
        self.assertEqual(fitted_rows[-1], 240)

    def test_feature_target_and_current_inference_row_follow_selected_horizon(self):
        indicators = add_indicators(_ohlcv())
        horizon = 5
        frame = make_feature_frame(indicators, horizon=horizon)
        target_date = indicators.index[-horizon - 1]
        expected_return = (
            indicators["Close"].iloc[-1] / indicators["Close"].loc[target_date] - 1
        )

        self.assertEqual(frame.attrs["horizon"], horizon)
        self.assertEqual(frame.index[-1], target_date)
        self.assertAlmostEqual(frame["Target"].iloc[-1], expected_return)
        self.assertEqual(
            frame.attrs["current_features"]["Close"], indicators["Close"].iloc[-1]
        )

    def test_pillar_features_use_dated_snapshots_and_current_values_only_for_inference(
        self,
    ):
        indicators = add_indicators(_ohlcv())
        history = pd.DataFrame(
            {
                "symbol": "TEST",
                "session_date": indicators.index.strftime("%Y-%m-%d"),
                "fundamental_score": 60,
                "technical_score": 55,
                "sentiment_score": 0.2,
                "sentiment_count": 2,
            }
        )
        features = make_pillar_feature_frame(
            indicators, history, "TEST", 70, 65, 0.4, 3, horizon=1
        )

        self.assertFalse(features.empty)
        self.assertEqual(features.iloc[-1]["FundamentalScore"], 60)
        self.assertEqual(features.attrs["current_features"]["FundamentalScore"], 70)
        self.assertTrue(features.attrs["current_features"].notna().all())

    def test_lstm_sequences_include_the_feature_row_for_each_target(self):
        features = np.arange(10, dtype=float).reshape(-1, 1)
        targets = np.arange(10, dtype=float)

        indices, sequences, aligned_targets = _lstm_sequences(
            features, targets, window=3
        )

        self.assertEqual(indices.tolist(), list(range(2, 10)))
        np.testing.assert_array_equal(sequences[0].ravel(), [0, 1, 2])
        np.testing.assert_array_equal(aligned_targets, targets[2:])

    def test_forecast_price_intervals_and_probabilities_are_consistent(self):
        frame = pd.DataFrame({"Close": [100.0]})
        frame.attrs["current_close"] = 100.0
        frame.attrs["horizon"] = 5

        class FixedModel:
            def predict(self, features):
                return np.asarray([0.1])

        forecast = prediction.forecast_next_close(
            frame,
            {
                "best_name": "Linear",
                "best_model": FixedModel(),
                "last_x": np.asarray([[1.0]]),
                "display_model_name": "Linear",
                "horizon": 5,
                "residuals": np.asarray([-0.2, 0.0, 0.1]),
                "interval_50": 0.05,
                "interval_90": 0.2,
            },
        )

        self.assertAlmostEqual(forecast["price"], 110)
        self.assertAlmostEqual(forecast["price_change"], 10)
        self.assertAlmostEqual(forecast["interval_50_low"], 105)
        self.assertAlmostEqual(forecast["interval_50_high"], 115)
        self.assertEqual(forecast["horizon"], 5)
        self.assertAlmostEqual(
            forecast["probability_up"] + forecast["probability_down"], 1
        )


class VerdictAndHistoryTests(unittest.TestCase):
    def test_combined_score_normalizes_available_pillars_and_tracks_contributions(self):
        result = scoring.combine_analysis_signals(
            {"score": 100, "label": "Bullish"},
            {"score": 50, "label": "Neutral"},
            {"score": -1, "count": 5, "label": "Negative"},
            lang="en",
        )

        self.assertEqual(result["score"], 60)
        self.assertAlmostEqual(sum(result["normalized_weights"].values()), 1)
        self.assertEqual(result["contributions"]["fundamental"], 20)
        self.assertEqual(result["contributions"]["technical"], 0)
        self.assertEqual(result["contributions"]["sentiment"], -10)

    def test_learning_does_not_turn_negative_correlation_into_a_positive_vote(self):
        dates = pd.bdate_range("2024-01-01", periods=121)
        prices = pd.DataFrame({"Close": np.arange(121, dtype=float) + 100}, index=dates)
        history = pd.DataFrame(
            {
                "symbol": "TEST",
                "session_date": dates[:-1].strftime("%Y-%m-%d"),
                "fundamental_score": 100,
                "technical_score": 0,
                "sentiment_score": 0,
                "sentiment_count": 1,
            }
        )
        correlation_values = iter([0.9, -0.9, 0.1])

        def fake_corrcoef(*args):
            value = next(correlation_values)
            return np.asarray([[1.0, value], [value, 1.0]])

        with patch("src.scoring.np.corrcoef", side_effect=fake_corrcoef):
            weights, count = scoring._learn_backtest_weights(history, prices, "TEST")

        self.assertEqual(count, 120)
        self.assertIsNotNone(weights)
        self.assertGreater(weights["fundamental"], 0)
        self.assertEqual(weights["technical"], 0)

    def test_snapshot_is_first_write_for_each_symbol_and_session(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            path = Path(directory) / "pillar_history.csv"
            with patch.object(pillar_history, "HISTORY_PATH", path):
                first = pillar_history.record_pillar_snapshot(
                    "TEST", "2024-01-02", 60, 55, 0.2, 4
                )
                second = pillar_history.record_pillar_snapshot(
                    "TEST", "2024-01-02", 10, 15, -0.8, 2
                )

        self.assertEqual(len(first), 1)
        self.assertEqual(len(second), 1)
        self.assertEqual(second.iloc[0]["fundamental_score"], 60)


if __name__ == "__main__":
    unittest.main()
