"""Store dated analysis snapshots used to train the three-pillar ML model."""

from pathlib import Path

import numpy as np
import pandas as pd

HISTORY_PATH = Path(__file__).resolve().parent.parent / "data" / "pillar_history.csv"
HISTORY_COLUMNS = [
    "symbol",
    "session_date",
    "fundamental_score",
    "technical_score",
    "sentiment_score",
    "sentiment_count",
]


def load_pillar_history():
    """Load the local, date-stamped snapshots collected by the app."""
    if not HISTORY_PATH.exists():
        return pd.DataFrame(columns=HISTORY_COLUMNS)

    history = pd.read_csv(HISTORY_PATH)
    for column in HISTORY_COLUMNS:
        if column not in history:
            history[column] = np.nan
    return history[HISTORY_COLUMNS]


def record_pillar_snapshot(
    symbol,
    session_date,
    fundamental_score,
    technical_score,
    sentiment_score,
    sentiment_count,
):
    """Record the first known signal snapshot for a ticker and market session.

    Keeping the first observation prevents a later rerun from replacing a historic
    signal with information published after its next-session outcome was known.
    """
    session_key = pd.Timestamp(session_date).strftime("%Y-%m-%d")
    history = load_pillar_history()
    key_exists = (
        history["symbol"].astype(str).str.upper().eq(symbol.upper())
        & history["session_date"].astype(str).eq(session_key)
    ).any()

    if key_exists:
        return history

    sentiment_value = (
        float(sentiment_score)
        if sentiment_count and sentiment_score is not None
        else np.nan
    )
    snapshot = pd.DataFrame(
        [
            {
                "symbol": symbol.upper(),
                "session_date": session_key,
                "fundamental_score": _numeric_or_nan(fundamental_score),
                "technical_score": _numeric_or_nan(technical_score),
                "sentiment_score": sentiment_value,
                "sentiment_count": int(sentiment_count or 0),
            }
        ]
    )
    history = pd.concat([history, snapshot], ignore_index=True)
    history = history.drop_duplicates(subset=["symbol", "session_date"], keep="first")
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    history.to_csv(HISTORY_PATH, index=False)
    return history


def _numeric_or_nan(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return np.nan
