"""Combine fundamental, technical and sentiment pillars with visible weights."""

import numpy as np
import pandas as pd

from src.i18n import t

DEFAULT_WEIGHTS = {"fundamental": 0.40, "technical": 0.40, "sentiment": 0.20}


def overall_view(fund, tech, sentiment):
    return fund["label"], tech["label"], sentiment["label"]


def _score_direction(value, sentiment=False):
    try:
        score = float(value)
    except (TypeError, ValueError):
        return None
    return (
        float(np.clip(score, -1, 1))
        if sentiment
        else float(np.clip((score - 50) / 50, -1, 1))
    )


def _learn_backtest_weights(history, prices, symbol=None):
    """Learn nonnegative pillar weights only if they beat defaults out of time."""
    if history is None or history.empty or prices is None or "Close" not in prices:
        return None, 0
    data = history.copy()
    required = {
        "symbol",
        "session_date",
        "fundamental_score",
        "technical_score",
        "sentiment_score",
        "sentiment_count",
    }
    if not required.issubset(data.columns):
        return None, 0
    if symbol:
        data = data.loc[data["symbol"].astype(str).str.upper() == symbol.upper()].copy()
    data = data.loc[data["sentiment_count"].fillna(0) > 0].copy()
    close = prices["Close"].astype(float)
    returns = close.shift(-1) / close - 1
    return_map = pd.DataFrame(
        {
            "session_date": close.index.strftime("%Y-%m-%d"),
            "next_return": returns.to_numpy(),
        }
    )
    data = data.merge(return_map, on="session_date", how="inner").dropna()
    if len(data) < 100:
        return None, len(data)
    data = data.sort_values("session_date")
    x = np.column_stack(
        [
            (data["fundamental_score"].to_numpy(float) - 50) / 50,
            (data["technical_score"].to_numpy(float) - 50) / 50,
            data["sentiment_score"].to_numpy(float),
        ]
    )
    y = data["next_return"].to_numpy(float)
    split = int(len(data) * 0.7)
    if split < 60 or len(data) - split < 30:
        return None, len(data)
    correlations = np.asarray(
        [np.corrcoef(x[:split, i], y[:split])[0, 1] for i in range(3)]
    )
    # A negative relationship must not become a larger positive vote simply
    # because its absolute correlation is large. Ignore such pillars here;
    # learned weights only scale signals in their stated bullish direction.
    raw = np.maximum(np.nan_to_num(correlations, nan=0.0), 0.0)
    if raw.sum() <= 0:
        return None, len(data)
    learned = raw / raw.sum()
    defaults = np.asarray(list(DEFAULT_WEIGHTS.values()))
    validation_x, validation_y = x[split:], y[split:]
    learned_accuracy = np.mean(np.sign(validation_x @ learned) == np.sign(validation_y))
    default_accuracy = np.mean(
        np.sign(validation_x @ defaults) == np.sign(validation_y)
    )
    return (
        dict(zip(DEFAULT_WEIGHTS, learned))
        if learned_accuracy > default_accuracy
        else None
    ), len(data)


def combine_analysis_signals(
    fund, tech, sentiment, lang="fr", history=None, prices=None, symbol=None
):
    """Combine available scores; use learned weights only after a successful temporal comparison."""
    scores = {
        "fundamental": _score_direction(fund.get("score")),
        "technical": _score_direction(tech.get("score")),
        "sentiment": (
            _score_direction(sentiment.get("score"), sentiment=True)
            if sentiment.get("count", 0)
            else None
        ),
    }
    weights, sample_count = _learn_backtest_weights(history, prices, symbol=symbol)
    learned = weights is not None
    weights = weights or DEFAULT_WEIGHTS.copy()
    active = {key: value for key, value in scores.items() if value is not None}
    weight_sum = sum(weights[key] for key in active)
    normalized = (
        {key: weights[key] / weight_sum for key in active} if weight_sum else {}
    )
    combined = sum(scores[key] * normalized[key] for key in active) if active else 0.0
    score = 50 * (combined + 1)
    direction = 1 if score >= 60 else -1 if score < 40 else 0
    label_key = (
        "bullish" if direction > 0 else "bearish" if direction < 0 else "neutral"
    )
    # This is a score-strength indicator, not a probability of a profitable trade.
    confidence = round(abs(score - 50) * 2)
    contributions = {
        key: (scores[key] * normalized[key] * 50 if key in normalized else None)
        for key in scores
    }
    return {
        "direction": direction,
        "score": round(score),
        "label": t(lang, label_key) if active else t(lang, "unavailable"),
        "confidence": confidence if active else None,
        "confidence_kind": "score_strength",
        "weights": weights,
        "normalized_weights": normalized,
        "contributions": contributions,
        "weight_source": "learned" if learned else "default",
        "history_count": sample_count,
        "available_count": len(active),
        "total_count": 3,
    }
