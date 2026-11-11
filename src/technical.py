"""OHLCV indicators, graded directional signals and readable dark Plotly charts."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.i18n import t


def add_indicators(data):
    df = data.copy()
    close, high, low = df.Close, df.High, df.Low
    df["Returns"] = close.pct_change()
    for window in (20, 50, 200):
        df[f"SMA{window}"] = close.rolling(window, min_periods=window).mean()
    df["EMA12"] = close.ewm(span=12, adjust=False).mean()
    df["EMA26"] = close.ewm(span=26, adjust=False).mean()
    df["MACD"] = df.EMA12 - df.EMA26
    df["MACD_Signal"] = df.MACD.ewm(span=9, adjust=False).mean()
    df["MACDGap"] = df.MACD - df.MACD_Signal
    change = close.diff()
    gain = change.clip(lower=0).ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    loss = -change.clip(upper=0).ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI"] = 100 - 100 / (1 + rs)
    df.loc[(loss == 0) & (gain > 0), "RSI"] = 100
    df.loc[(loss == 0) & (gain == 0), "RSI"] = 50
    previous = close.shift(1)
    true_range = pd.concat(
        [high - low, (high - previous).abs(), (low - previous).abs()], axis=1
    ).max(axis=1)
    df["ATR"] = true_range.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    up = high.diff()
    down = -low.diff()
    plus_dm = up.where((up > down) & (up > 0), 0.0)
    minus_dm = down.where((down > up) & (down > 0), 0.0)
    atr_smooth = true_range.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    df["PlusDI"] = (
        100
        * plus_dm.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
        / atr_smooth.replace(0, np.nan)
    )
    df["MinusDI"] = (
        100
        * minus_dm.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
        / atr_smooth.replace(0, np.nan)
    )
    dx = (
        100
        * (df.PlusDI - df.MinusDI).abs()
        / (df.PlusDI + df.MinusDI).replace(0, np.nan)
    )
    df["ADX"] = dx.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    df["BB_Middle"] = close.rolling(20, min_periods=20).mean()
    deviation = close.rolling(20, min_periods=20).std()
    df["BB_Upper"] = df.BB_Middle + 2 * deviation
    df["BB_Lower"] = df.BB_Middle - 2 * deviation
    df["BB_PercentB"] = (close - df.BB_Lower) / (df.BB_Upper - df.BB_Lower).replace(
        0, np.nan
    )
    df["VolumeSMA20"] = df.Volume.rolling(20, min_periods=20).mean()
    df["High52"] = high.rolling(252, min_periods=252).max()
    df["DistanceHigh52"] = close / df.High52 - 1
    df["Support20"] = low.rolling(20, min_periods=20).min()
    df["Resistance20"] = high.rolling(20, min_periods=20).max()
    df["Volatility"] = df.Returns.rolling(20, min_periods=20).std() * np.sqrt(252)
    df["GoldenCross"] = (df.SMA50 > df.SMA200) & (
        df.SMA50.shift(1) <= df.SMA200.shift(1)
    )
    df["DeathCross"] = (df.SMA50 < df.SMA200) & (
        df.SMA50.shift(1) >= df.SMA200.shift(1)
    )
    return df


def _score(value, threshold, scale, higher=True):
    """Map distance from an indicator threshold to a continuous 0–100 score."""
    direction = 1 if higher else -1
    z = np.clip(direction * (value - threshold) / max(scale, 1e-9), -8, 8)
    return float(100 / (1 + np.exp(-z)))


def _rsi_grade(value):
    """Treat RSI extremes as caution zones instead of one-way bullish signals."""
    if value < 30:
        return 35 + max(0, value) / 30 * 5
    if value <= 50:
        return 40 + (value - 30) / 20 * 10
    if value <= 70:
        return 50 + (value - 50) / 20 * 10
    return max(35, 60 - (value - 70) * 0.83)


def analyze_technical(df, lang="fr"):
    row = df.iloc[-1]
    price = float(row.Close)
    atr = float(row.ATR) if pd.notna(row.ATR) and row.ATR > 0 else None
    specs = []

    def add(
        key,
        reading,
        value,
        threshold,
        scale,
        higher=True,
        *,
        descriptive=False,
        grade_override=None,
        valid_override=None,
    ):
        valid = (
            bool(valid_override)
            if valid_override is not None
            else value is not None and np.isfinite(value)
        )
        grade = (
            grade_override
            if valid and grade_override is not None
            else (
                _score(value, threshold, scale, higher)
                if valid and not descriptive
                else None
            )
        )
        specs.append((key, reading, grade, descriptive, valid))

    for window in (20, 50, 200):
        average = row.get(f"SMA{window}")
        distance = (price / average - 1) if pd.notna(average) and average else None
        add(
            f"tech_price_sma{window}",
            (
                f"{price:,.2f} / {average:,.2f} ({distance:+.1%})"
                if distance is not None
                else t(lang, "unavailable")
            ),
            distance,
            0,
            0.04,
        )
    macd_gap = (
        (row.MACD - row.MACD_Signal) / atr
        if pd.notna(row.MACD) and pd.notna(row.MACD_Signal) and atr
        else None
    )
    add(
        "tech_macd_signal",
        (
            f"{row.MACD:.3f} / {row.MACD_Signal:.3f}"
            if macd_gap is not None
            else t(lang, "unavailable")
        ),
        macd_gap,
        0,
        0.5,
    )
    rsi = float(row.RSI) if pd.notna(row.RSI) else None
    rsi_zone = (
        t(lang, "rsi_oversold")
        if rsi is not None and rsi < 30
        else (
            t(lang, "rsi_overbought")
            if rsi is not None and rsi > 70
            else t(lang, "rsi_neutral")
        )
    )
    # RSI is directional around 50; the zone is displayed separately and is not a pass/fail rule.
    add(
        "tech_rsi",
        f"{rsi:.1f} · {rsi_zone}" if rsi is not None else t(lang, "unavailable"),
        rsi,
        50,
        18,
        grade_override=_rsi_grade(rsi) if rsi is not None else None,
    )
    # ATR and local support/resistance describe risk/levels, not bullishness; no directional grade.
    support, resistance = row.Support20, row.Resistance20
    levels_available = pd.notna(support) and pd.notna(resistance)
    add(
        "tech_levels",
        (
            f"{support:,.2f} / {resistance:,.2f}"
            if levels_available
            else t(lang, "unavailable")
        ),
        None,
        0,
        1,
        descriptive=True,
        valid_override=levels_available,
    )
    atr_available = atr is not None and price > 0
    add(
        "tech_atr",
        f"{atr:,.2f} ({atr / price:.1%})" if atr_available else t(lang, "unavailable"),
        None,
        0,
        1,
        descriptive=True,
        valid_override=atr_available,
    )

    scored = [item[2] for item in specs if item[2] is not None]
    score = round(float(np.mean(scored))) if scored else None
    label_key = (
        "bullish"
        if score is not None and score >= 60
        else "bearish" if score is not None and score < 40 else "neutral"
    )
    rows = []
    for key, reading, grade, descriptive, valid in specs:
        if not valid:
            signal = f"⚪ {t(lang, 'unavailable')}"
            grade_text = t(lang, "unavailable")
        elif descriptive:
            signal = f"ℹ️ {t(lang, 'informational')}"
            grade_text = t(lang, "not_applicable")
        else:
            signal_key = (
                "positive" if grade >= 60 else "negative" if grade < 40 else "neutral"
            )
            signal = f"{'🟢' if signal_key == 'positive' else '🔴' if signal_key == 'negative' else '🟠'} {t(lang, signal_key)}"
            grade_text = f"{grade:.0f}/100"
        rows.append(
            {
                t(lang, "technical_criterion"): t(lang, key),
                t(lang, "technical_reading"): reading,
                t(lang, "technical_grade"): grade_text,
                t(lang, "signal_status"): signal,
            }
        )
    explanation = t(
        lang,
        "technical_graded_explanation",
        count=len(scored),
        score=score if score is not None else t(lang, "not_available"),
    )
    return {
        "score": score if score is not None else t(lang, "not_available"),
        "label": t(lang, label_key) if score is not None else t(lang, "unavailable"),
        "explanation": explanation,
        "scoring_method": explanation,
        "table": pd.DataFrame(rows),
        "passed": None,
        "available": len(scored),
    }


def technical_chart(df, symbol, lang="fr"):
    indicator_title = (
        "مؤشر القوة النسبية وMACD"
        if lang == "ar"
        else "RSI et MACD" if lang == "fr" else "RSI and MACD"
    )
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.055,
        row_heights=[0.58, 0.21, 0.21],
        subplot_titles=(t(lang, "chart_prices", symbol=symbol), "RSI", "MACD"),
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df.Close,
            name=t(lang, "chart_close"),
            line={"color": "#e6edf7", "width": 2},
        ),
        row=1,
        col=1,
    )
    for column, key in (
        ("SMA20", "chart_sma20"),
        ("SMA50", "chart_sma50"),
        ("SMA200", "chart_sma200"),
    ):
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df[column], name=t(lang, key), line={"width": 1.5}
            ),
            row=1,
            col=1,
        )
    for column, marker, color, label in (
        ("GoldenCross", "triangle-up", "#4bd19b", t(lang, "golden_cross")),
        ("DeathCross", "triangle-down", "#ff717b", t(lang, "death_cross")),
    ):
        points = df[df[column].fillna(False)]
        if not points.empty:
            fig.add_trace(
                go.Scatter(
                    x=points.index,
                    y=points.Close,
                    mode="markers",
                    name=label,
                    marker={"symbol": marker, "size": 12, "color": color},
                ),
                row=1,
                col=1,
            )
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df.RSI, name="RSI", line={"color": "#bb9cff", "width": 2}
        ),
        row=2,
        col=1,
    )
    fig.add_hline(y=70, line_dash="dot", line_color="#ff717b", row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="#f4c36b", row=2, col=1)
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df.MACD, name="MACD", line={"color": "#4bd19b", "width": 2}
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df.MACD_Signal,
            name=t(lang, "macd_signal_name"),
            line={"color": "#f4c36b", "width": 1.5},
        ),
        row=3,
        col=1,
    )
    fig.add_hline(y=0, line_color="#8092a8", row=3, col=1)
    fig.update_layout(
        template="plotly_dark",
        height=820,
        hovermode="x unified",
        legend_orientation="h",
        font={"color": "#d5dfeb"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(23,36,54,1)",
        margin={"t": 80, "b": 30},
    )
    fig.update_xaxes(gridcolor="#293b4f", zerolinecolor="#3b4c61")
    fig.update_yaxes(gridcolor="#293b4f", zerolinecolor="#3b4c61")
    fig.update_xaxes(title_text=t(lang, "chart_date"), row=3, col=1)
    return fig
