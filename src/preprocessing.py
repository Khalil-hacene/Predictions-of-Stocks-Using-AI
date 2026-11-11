"""Build leakage-aware features for next-session return prediction."""

import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "Close",
    "Volume",
    "Returns",
    "SMA20",
    "SMA50",
    "RSI",
    "MACD",
    "Volatility",
    "SMA200",
    "ADX",
    "PlusDI",
    "MinusDI",
    "BB_PercentB",
    "ATR",
    "VolumeSMA20",
    "DistanceHigh52",
    "MACDGap",
]
PILLAR_FEATURE_COLUMNS = [
    "FundamentalScore",
    "TechnicalScore",
    "SentimentScore",
    "SentimentCount",
]


def make_feature_frame(indicators, horizon=1):
    """Create labelled history and preserve the newest row for live inference."""
    horizon = int(horizon)
    if horizon < 1:
        raise ValueError("The forecast horizon must be at least one session.")

    # Skip indicators with too little history so short selected periods can still
    # produce a model; never impute unavailable market history as a real value.
    available_columns = [
        column
        for column in FEATURE_COLUMNS
        if column in indicators.columns and indicators[column].notna().sum() >= 30
    ]
    if not available_columns:
        available_columns = [
            column for column in ("Close", "Volume", "Returns") if column in indicators
        ]
    features = indicators[available_columns].copy()
    current_features = features.iloc[-1].copy()

    features["Target"] = indicators["Close"].shift(-horizon) / indicators["Close"] - 1
    features = features.replace([np.inf, -np.inf], np.nan).dropna()

    # The newest session has no next-session label, so it is only used at inference.
    features.attrs["current_features"] = current_features
    features.attrs["current_close"] = float(current_features["Close"])
    features.attrs["horizon"] = horizon
    features.attrs["feature_columns"] = available_columns
    features.attrs["inference_sequence_features"] = (
        indicators[available_columns].tail(30).to_numpy(dtype=float)
    )
    return features


def make_pillar_feature_frame(
    indicators,
    history,
    symbol,
    fundamental_score,
    technical_score,
    sentiment_score,
    sentiment_count,
    horizon=1,
):
    """Add only dated, previously recorded fundamental and news features.

    Rows without a known fundamental snapshot or a dated sentiment score are
    excluded. The newest live row is kept separately for next-session inference.
    """
    features = make_feature_frame(indicators, horizon=horizon)
    current_features = features.attrs["current_features"].copy()

    ticker_history = history.loc[
        history["symbol"].astype(str).str.upper() == symbol.upper()
    ].copy()
    if ticker_history.empty:
        ticker_history = pd.DataFrame(columns=["session_date", *PILLAR_FEATURE_COLUMNS])

    ticker_history["session_date"] = pd.to_datetime(
        ticker_history["session_date"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")
    ticker_history = ticker_history.dropna(subset=["session_date"])
    ticker_history = ticker_history.drop_duplicates("session_date", keep="first")
    ticker_history = ticker_history.set_index("session_date")

    session_dates = pd.Series(features.index.strftime("%Y-%m-%d"), index=features.index)
    feature_map = {
        "FundamentalScore": "fundamental_score",
        "TechnicalScore": "technical_score",
        "SentimentScore": "sentiment_score",
        "SentimentCount": "sentiment_count",
    }
    for feature_name, history_name in feature_map.items():
        if history_name in ticker_history:
            features[feature_name] = session_dates.map(ticker_history[history_name])
        else:
            features[feature_name] = np.nan

    features = features.dropna(subset=PILLAR_FEATURE_COLUMNS).copy()
    current_features["FundamentalScore"] = _numeric_or_nan(fundamental_score)
    current_features["TechnicalScore"] = _numeric_or_nan(technical_score)
    current_features["SentimentScore"] = (
        _numeric_or_nan(sentiment_score) if sentiment_count else np.nan
    )
    current_features["SentimentCount"] = int(sentiment_count or 0)

    features.attrs["current_features"] = current_features
    features.attrs["current_close"] = float(indicators["Close"].iloc[-1])
    features.attrs["horizon"] = int(horizon)
    if int(horizon) == 1 and len(features) >= 29:
        features.attrs["inference_sequence_features"] = np.vstack(
            [
                features.drop(columns="Target").tail(29).to_numpy(dtype=float),
                current_features.to_numpy(dtype=float),
            ]
        )
    return features


def _numeric_or_nan(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return np.nan
