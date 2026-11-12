"""AI Stock Analyzer — Streamlit dashboard entry point."""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import importlib
from datetime import datetime, timezone
from src.data_loader import (
    DataUnavailable,
    fetch_fundamentals,
    fetch_news,
    fetch_prices,
)
from src.fundamental import analyze_fundamentals
from src.technical import add_indicators, analyze_technical, technical_chart
from src.sentiment import analyze_news
import src.preprocessing as preprocessing
import src.ml_models as ml_models
from src.pillar_history import load_pillar_history, record_pillar_snapshot
from src.prediction import forecast_next_close
from src.scoring import combine_analysis_signals, overall_view
from src.i18n import t
from src.evaluation import evaluate_holdout, evaluate_walk_forward
from src.stocks import STOCKS

# Streamlit hot-reloads this entry point, but imported translation modules can stay
# cached. Reload the small dictionary so language changes always use current strings.
import src.i18n as i18n

preprocessing = importlib.reload(preprocessing)
ml_models = importlib.reload(ml_models)
make_feature_frame = preprocessing.make_feature_frame
make_pillar_feature_frame = preprocessing.make_pillar_feature_frame
minimum_pillar_rows = preprocessing.minimum_pillar_rows
compare_models = ml_models.compare_models

i18n = importlib.reload(i18n)
t = i18n.t


@st.cache_data(ttl=900, show_spinner=False)
def _load_prices(symbol, period, lang):
    return fetch_prices(symbol, period, lang), datetime.now(timezone.utc)


@st.cache_data(ttl=900, show_spinner=False)
def _load_fundamentals(symbol):
    return fetch_fundamentals(symbol), datetime.now(timezone.utc)


@st.cache_data(ttl=900, show_spinner=False)
def _load_news(symbol, company):
    return fetch_news(symbol, company), datetime.now(timezone.utc)


@st.cache_data(ttl=900, show_spinner=False)
def _evaluate_model(prices, features):
    return evaluate_holdout(features, prices)


@st.cache_data(ttl=900, show_spinner=False)
def _evaluate_walk_forward(prices, features):
    return evaluate_walk_forward(features, prices)


def _money(value, lang="fr"):
    """Format a market value, showing a clear fallback for missing data."""
    try:
        return f"${float(value):,.0f}" if value is not None else t(lang, "unavailable")
    except (TypeError, ValueError):
        return t(lang, "unavailable")


def _signal_tone(label, lang):
    if label in {t(lang, "positive"), t(lang, "positive_label"), t(lang, "bullish")}:
        return "positive"
    if label in {t(lang, "negative"), t(lang, "negative_label"), t(lang, "bearish")}:
        return "negative"
    if label in {t(lang, "neutral"), t(lang, "neutral_label")}:
        return "neutral"
    return "unavailable"


def _signal_badge(label, tone):
    return f'<span class="signal-badge signal-{tone}">{label}</span>'


def _style_signal_cell(value):
    value = str(value)
    if "🟢" in value:
        return "color: #74e0a8; font-weight: 700"
    if "🔴" in value:
        return "color: #ff9097; font-weight: 700"
    if "⚪" in value or "ℹ️" in value:
        return "color: #a9b8c9; font-weight: 650"
    return ""


LANGUAGE_CODES = {"Français": "fr", "English": "en", "العربية": "ar"}
LANGUAGE_LABELS = {code: label for label, code in LANGUAGE_CODES.items()}

selected_language = st.session_state.get("language_selector", "Français")
lang = LANGUAGE_CODES.get(selected_language, "fr")
st.set_page_config(page_title=t(lang, "app_title"), page_icon="📈", layout="wide")
st.markdown(
    """
<style>
    :root {font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif}
    .stApp, [data-testid='stAppViewContainer'] {background:#0d1420;color:#edf4fb}
    .block-container {padding:1.6rem 2.2rem 3.5rem;max-width:1460px}
    [data-testid='stHeader'] {background:rgba(13,20,32,.92)}
    [data-testid='stDeployButton'] {display:none}
    #MainMenu {visibility:hidden}
    [data-testid='stSidebar'] {background:#111c2b;border-right:1px solid #26384c}
    [data-testid='stSidebar'] [data-testid='stMarkdownContainer'] p,
    [data-testid='stSidebar'] [data-testid='stWidgetLabel'] p,
    [data-testid='stSidebar'] h1, [data-testid='stSidebar'] h2,
    [data-testid='stSidebar'] h3, [data-testid='stSidebar'] label {color:#eaf1f8}
    [data-testid='stSidebar'] [data-testid='stCaptionContainer'] {color:#91a2b6}
    [data-testid='stSidebar'] [data-testid='stButton'] button[kind='secondary'] {background:#1c2c40 !important;color:#edf4fb !important;border:1px solid #34485e !important;opacity:1 !important}
    [data-testid='stSidebar'] [data-testid='stButton'] button[kind='secondary'] p,
    [data-testid='stSidebar'] [data-testid='stButton'] button[kind='secondary'] span {color:#edf4fb !important;opacity:1 !important}
    [data-testid='stSidebar'] [data-testid='stButton'] button[kind='secondary']:hover {background:#294155 !important;border-color:#63d4bb !important;color:#ffffff !important}
    [data-testid='stMetric'] {background:#172436;padding:1.05rem 1.15rem;border:1px solid #293b4f;border-radius:16px;box-shadow:0 8px 24px rgba(0,0,0,.16);min-height:112px}
    [data-testid='stMetricLabel'] p {color:#91a2b6;font-size:.82rem;font-weight:600}
    [data-testid='stMetricValue'] {color:#edf4fb;font-size:1.55rem;font-weight:750}
    [data-testid='stMetricDelta'] {font-size:.84rem}
    [data-testid='stTabs'] [role='tablist'] {gap:.5rem;border-bottom:1px solid #293b4f}
    [data-testid='stTabs'] button {font-weight:650;color:#91a2b6;padding:.72rem 1rem;border-radius:10px 10px 0 0}
    [data-testid='stTabs'] button[aria-selected='true'] {color:#63d4bb;border-bottom:3px solid #63d4bb;background:#172d35}
    [data-testid='stRadio'] [role='radiogroup'] {display:flex;flex-wrap:wrap;gap:.55rem;padding:.55rem;margin:.2rem 0 1.25rem;border:1px solid #293b4f;border-radius:15px;background:#111c2b}
    [data-testid='stRadio'] [role='radiogroup'] label {margin:0;padding:.58rem .9rem;border:1px solid #293b4f;border-radius:10px;background:#172436;color:#a9b8c9;transition:all .15s ease}
    [data-testid='stRadio'] [role='radiogroup'] label:has(input:checked) {background:#1d433e;border-color:#3c947f;color:#87e3c8}
    [data-testid='stRadio'] [role='radiogroup'] label:has(input:checked) p {color:#87e3c8;font-weight:700}
    [data-testid='stRadio'] [role='radiogroup'] label:hover {border-color:#63d4bb;color:#edf4fb}
    .hero {position:relative;overflow:hidden;padding:1.45rem 1.75rem;margin:.25rem 0 1.35rem;border:1px solid #293b4f;border-radius:18px;background:linear-gradient(110deg,#172436 0%,#142333 62%,#173a37 100%);box-shadow:0 8px 24px rgba(0,0,0,.18)}
    .hero:after {content:"";position:absolute;width:180px;height:180px;right:5%;top:-115px;border-radius:50%;background:#2c6659;opacity:.55}
    .hero-kicker {position:relative;z-index:1;margin:0 0 .35rem;color:#63d4bb;font-size:.72rem;font-weight:750;letter-spacing:.12em;text-transform:uppercase}
    .hero h1 {position:relative;z-index:1;margin:0 0 .32rem;color:#edf4fb;font-size:1.9rem;letter-spacing:-.035em}
    .hero p {position:relative;z-index:1;margin:0;color:#a8b8c9;font-size:.96rem}
    .section-title {font-size:1.22rem;font-weight:750;letter-spacing:-.02em;margin:.35rem 0 .8rem;color:#edf4fb}
    .conclusion {padding:1.2rem 1.4rem;border:1px solid #293b4f;border-left:4px solid #63d4bb;border-radius:14px;background:#172436;color:#d8e3ee;line-height:1.75;box-shadow:0 6px 20px rgba(0,0,0,.16)}
    .sentiment-badge {display:inline-flex;align-items:center;margin-top:.25rem;padding:.2rem .65rem;border-radius:999px;font-size:.78rem;font-weight:700}
    .sentiment-positive {background:#173d32;color:#74e0a8}
    .sentiment-negative {background:#45262d;color:#ff9097}
    .sentiment-neutral {background:#433821;color:#f4c36b}
    .signal-badge {display:inline-flex;align-items:center;margin:.3rem 0 .1rem;padding:.23rem .7rem;border-radius:999px;font-size:.8rem;font-weight:750;line-height:1.35}
    .signal-positive {background:#173d32;color:#74e0a8}
    .signal-negative {background:#45262d;color:#ff9097}
    .signal-neutral {background:#433821;color:#f4c36b}
    .signal-unavailable {background:#293545;color:#a9b8c9}
    .signal-text {font-weight:750}
    .signal-text.signal-positive {background:transparent;color:#74e0a8}
    .signal-text.signal-negative {background:transparent;color:#ff9097}
    .signal-text.signal-neutral {background:transparent;color:#f4c36b}
    div[data-testid='stDataFrame'] {border:1px solid #293b4f;border-radius:12px;overflow:hidden;background:#172436}
    .stAlert {border-radius:12px}
    [data-testid='stPlotlyChart'] {padding:.35rem;border:1px solid #293b4f;border-radius:14px;background:#172436;box-shadow:0 5px 16px rgba(0,0,0,.14)}
    [data-testid='stButton'] button, [data-testid='stDownloadButton'] button {border-radius:10px;font-weight:650}
    hr {border-color:#293b4f}
    @media(max-width:760px) {.block-container{padding:1rem .9rem 2rem}.hero{padding:1.2rem}.hero h1{font-size:1.55rem}[data-testid='stMetric']{padding:.8rem;min-height:98px}[data-testid='stTabs'] button{padding:.6rem .55rem;font-size:.82rem}}
</style>
""",
    unsafe_allow_html=True,
)
if lang == "ar":
    st.markdown(
        """
    <style>
        .stApp, [data-testid='stAppViewContainer'], [data-testid='stSidebar'],
        .block-container, [data-testid='stMarkdownContainer'],
        [data-testid='stCaptionContainer'], [data-testid='stWidgetLabel'],
        [data-testid='stMetric'], [data-testid='stTabs'] {direction:rtl;text-align:right}
        [data-testid='stTabs'] [role='tablist'] {flex-direction:row-reverse}
        [data-testid='stMetricValue'] {direction:ltr;text-align:right}
        .hero:after {right:auto;left:5%}
    </style>
    """,
        unsafe_allow_html=True,
    )
st.markdown(
    f'<div class="hero"><div class="hero-kicker">{t(lang,"market_label")}</div><h1>📈 {t(lang,"app_title")}</h1><p>{t(lang,"hero")}</p></div>',
    unsafe_allow_html=True,
)
with st.sidebar:
    language_options = list(LANGUAGE_CODES)
    selected_language = st.selectbox(
        t(lang, "language"),
        language_options,
        index=language_options.index(LANGUAGE_LABELS.get(lang, "Français")),
        key="language_selector",
    )
    lang = LANGUAGE_CODES[selected_language]
    st.header(t(lang, "analysis"))
    st.caption(t(lang, "choose"))
    stock_options = [f"{ticker} — {company}" for ticker, company in STOCKS]
    st.caption(t(lang, "stock_universe", count=len(stock_options)))
    selected_stock = st.selectbox(
        t(lang, "stock"),
        stock_options,
        index=0,
        help=t(lang, "stock_help"),
        key="selected_stock",
    )
    symbol = selected_stock.split(" — ", 1)[0]
    period_codes = ["6mo", "1y", "2y", "5y", "10y"]
    period_labels = [t(lang, label) for label in ["p6", "p1", "p2", "p5", "p10"]]
    default_period = st.session_state.get("period_code", "2y")
    selected_period_label = st.selectbox(
        t(lang, "history"),
        period_labels,
        index=period_codes.index(default_period),
        key=f"selected_period_{lang}",
    )
    period = period_codes[period_labels.index(selected_period_label)]
    st.session_state["period_code"] = period
    forecast_unit = st.selectbox(
        t(lang, "forecast_horizon_unit"),
        options=["days", "weeks", "months"],
        format_func=lambda unit: t(lang, f"horizon_unit_{unit}"),
        key="forecast_unit",
    )
    horizon_lengths = {"days": [1, 3, 5], "weeks": [1, 2, 4], "months": [1, 3, 6]}
    forecast_length = st.selectbox(
        t(lang, "forecast_horizon_length"),
        options=horizon_lengths[forecast_unit],
        format_func=lambda length: t(lang, f"horizon_{forecast_unit}_{length}"),
        key=f"forecast_length_{forecast_unit}",
    )
    forecast_horizon = (
        forecast_length * {"days": 1, "weeks": 5, "months": 21}[forecast_unit]
    )
    horizon_label = t(lang, f"horizon_{forecast_unit}_{forecast_length}")
    analyze = st.button(t(lang, "run"), type="primary", use_container_width=True)
    refresh = st.button(
        t(lang, "refresh"), use_container_width=True, help=t(lang, "refresh_help")
    )
    st.divider()
    st.caption(t(lang, "third_party"))

if analyze or refresh:
    normalized_symbol = symbol.replace(".", "").replace("-", "")
    if not symbol or not normalized_symbol.isalnum():
        st.error(t(lang, "invalid_symbol"))
        st.stop()

    st.session_state["analysis_symbol"] = symbol
    st.session_state["analysis_period"] = period
    try:
        if refresh:
            _load_prices.clear()
            _load_fundamentals.clear()
            _load_news.clear()
        with st.spinner(t(lang, "loading", symbol=symbol)):
            prices, prices_fetched_at = _load_prices(symbol, period, lang)
            info, fundamentals_fetched_at = _load_fundamentals(symbol)
            articles, news_fetched_at = _load_news(
                symbol, info.get("shortName", symbol)
            )
        st.session_state["analysis_data"] = {
            "prices": prices,
            "prices_fetched_at": prices_fetched_at,
            "info": info,
            "fundamentals_fetched_at": fundamentals_fetched_at,
            "articles": articles,
            "news_fetched_at": news_fetched_at,
        }
    except DataUnavailable as exc:
        st.error(str(exc))
        st.stop()
    except Exception as exc:
        st.error(t(lang, "generic_error", error=exc))
        st.stop()

if "analysis_data" in st.session_state:
    symbol = st.session_state["analysis_symbol"]
    data = st.session_state["analysis_data"]
    prices = data["prices"]
    prices_fetched_at = data["prices_fetched_at"]
    info = data["info"]
    fundamentals_fetched_at = data["fundamentals_fetched_at"]
    articles = data["articles"]
    news_fetched_at = data["news_fetched_at"]
    enriched = add_indicators(prices)
    fund = analyze_fundamentals(info, lang)
    tech = analyze_technical(enriched, lang)
    with st.spinner(t(lang, "sentiment_loading")):
        sentiment = analyze_news(articles, lang)
    latest = enriched.iloc[-1]
    previous = enriched.iloc[-2] if len(enriched) > 1 else latest
    delta = (latest.Close / previous.Close - 1) * 100 if previous.Close else 0
    fundamental_label, technical_label, sentiment_label = overall_view(
        fund, tech, sentiment
    )
    try:
        pillar_history = record_pillar_snapshot(
            symbol=symbol,
            session_date=enriched.index[-1],
            fundamental_score=fund.get("score"),
            technical_score=tech.get("score"),
            sentiment_score=sentiment.get("score"),
            sentiment_count=sentiment.get("count", 0),
        )
    except Exception as exc:
        pillar_history = load_pillar_history()
        st.warning(t(lang, "pillar_history_save_error", error=exc))
    verdict = combine_analysis_signals(
        fund,
        tech,
        sentiment,
        lang=lang,
        history=pillar_history,
        prices=prices,
        symbol=symbol,
    )

    pillar_features = make_pillar_feature_frame(
        indicators=enriched,
        history=pillar_history,
        symbol=symbol,
        fundamental_score=fund.get("score"),
        technical_score=tech.get("score"),
        sentiment_score=sentiment.get("score"),
        sentiment_count=sentiment.get("count", 0),
        horizon=forecast_horizon,
    )
    st.subheader(f"{info.get('shortName',symbol)}  ·  {symbol}")
    st.caption(t(lang, "quick_view"))
    a, b, c, d = st.columns(4)
    a.metric(t(lang, "close"), f"${latest.Close:,.2f}", f"{delta:+.2f}%")
    b.metric(t(lang, "daily_change"), f"{delta:+.2f}%")
    c.metric(t(lang, "volume"), f"{latest.Volume:,.0f}")
    d.metric(t(lang, "market_cap"), _money(info.get("marketCap"), lang))
    market_date = prices.index[-1]
    if hasattr(market_date, "strftime"):
        market_date = market_date.strftime("%d/%m/%Y" if lang == "fr" else "%Y-%m-%d")
    time_format = "%d/%m/%Y à %H:%M UTC" if lang == "fr" else "%Y-%m-%d %H:%M UTC"
    st.caption(
        t(
            lang,
            "data_status",
            market_date=market_date,
            prices_time=prices_fetched_at.strftime(time_format),
            fundamentals_time=fundamentals_fetched_at.strftime(time_format),
            news_time=news_fetched_at.strftime(time_format),
        )
    )
    st.caption(t(lang, "data_sources_note"))
    forecast = None
    results = None
    pillar_ml_ready = False
    pillar_status = t(lang, "unavailable")
    pillar_minimum = minimum_pillar_rows(forecast_horizon)
    forecast_error = None
    with st.spinner(t(lang, "spinner")):
        try:
            price_features = make_feature_frame(enriched, horizon=forecast_horizon)
            current_pillar_features = pillar_features.attrs["current_features"]
            pillar_ml_ready = (
                len(pillar_features) >= pillar_minimum
                and current_pillar_features.notna().all()
            )
            if pillar_ml_ready:
                features = pillar_features
                pillar_status = t(lang, "pillar_model_ready", count=len(features))
            else:
                features = price_features
                if len(pillar_features) < pillar_minimum:
                    pillar_status = t(
                        lang,
                        "pillar_model_collecting",
                        count=len(pillar_features),
                        needed=pillar_minimum,
                    )
                else:
                    pillar_status = t(lang, "pillar_model_missing_signal")
            results = compare_models(features, lang)
            forecast = forecast_next_close(features, results)
        except Exception as exc:
            forecast_error = exc

    active_section = st.radio(
        t(lang, "navigation_label"),
        options=["overview", "technical", "news", "forecast", "evaluation_tab"],
        format_func=lambda section: t(lang, section),
        horizontal=True,
        label_visibility="collapsed",
        key="active_section",
    )
    if active_section == "overview":
        st.markdown(
            f'<div class="section-title">{t(lang,"scores")}</div>',
            unsafe_allow_html=True,
        )
        s1, s2, s3 = st.columns(3)
        fundamental_value = (
            f"{fund['score']}/100"
            if isinstance(fund["score"], (int, float))
            else t(lang, "unavailable")
        )
        technical_value = (
            f"{tech['score']}/100"
            if isinstance(tech["score"], (int, float))
            else t(lang, "unavailable")
        )
        s1.metric(t(lang, "fundamentals"), fundamental_value)
        s1.markdown(
            _signal_badge(fund["label"], _signal_tone(fund["label"], lang)),
            unsafe_allow_html=True,
        )
        s2.metric(t(lang, "technical_score"), technical_value)
        s2.markdown(
            _signal_badge(tech["label"], _signal_tone(tech["label"], lang)),
            unsafe_allow_html=True,
        )
        sentiment_value = (
            f"{sentiment['score']:+.2f}"
            if sentiment["count"]
            else t(lang, "unavailable")
        )
        s3.metric(t(lang, "sentiment"), sentiment_value)
        s3.markdown(
            _signal_badge(sentiment["label"], _signal_tone(sentiment["label"], lang)),
            unsafe_allow_html=True,
        )
        st.markdown(f"#### {t(lang, 'combined_verdict')}")
        verdict_columns = st.columns(3)
        verdict_columns[0].metric(t(lang, "verdict_signal"), verdict["label"])
        verdict_columns[1].metric(
            t(lang, "verdict_score"),
            (
                f"{verdict['score']}/100"
                if verdict["confidence"] is not None
                else t(lang, "unavailable")
            ),
        )
        verdict_columns[2].metric(
            t(lang, "verdict_confidence"),
            (
                f"{verdict['confidence']}%"
                if verdict["confidence"] is not None
                else t(lang, "unavailable")
            ),
            help=t(lang, "verdict_confidence_help"),
        )
        contribution_parts = []
        for key in ("fundamental", "technical", "sentiment"):
            weight = verdict["normalized_weights"].get(key, 0)
            contribution = verdict["contributions"].get(key)
            contribution_parts.append(
                f"{t(lang, 'pillar_' + key)} {weight:.0%} ({contribution:+.1f})"
                if contribution is not None
                else f"{t(lang, 'pillar_' + key)} {t(lang,'unavailable')}"
            )
        st.caption(
            t(
                lang,
                "verdict_method",
                source=t(lang, "weights_" + verdict["weight_source"]),
                history=verdict["history_count"],
                parts=" · ".join(contribution_parts),
            )
        )
        st.markdown(f"#### {t(lang,'fundamentals_table')}")
        st.caption(t(lang, "fundamental_quarter", quarter=fund["quarter"]))
        if fund.get("dcf"):
            dcf = fund["dcf"]
            st.caption(
                t(
                    lang,
                    "dcf_range",
                    low=dcf["low"],
                    base=dcf["base"],
                    high=dcf["high"],
                    margin=dcf["margin"] * 100,
                    currency=info.get("currency") or "",
                )
            )
        compact_fundamentals = fund["table"][
            [t(lang, "table_metric"), t(lang, "table_value")]
        ]
        st.dataframe(compact_fundamentals, use_container_width=True, hide_index=True)
        if fund.get("dcf_note"):
            st.warning(fund["dcf_note"])
        trend_rows = [
            {
                t(lang, "trend_metric"): t(
                    lang,
                    {
                        "revenue": "revenue_trend",
                        "earnings": "earnings_trend",
                        "margin": "margin_trend",
                        "fcf": "fcf_trend",
                    }[key],
                ),
                t(lang, "trend_value"): (
                    f"{value:+.1%}" if value is not None else t(lang, "unavailable")
                ),
            }
            for key, value in fund["trends"].items()
        ]
        with st.expander(t(lang, "fundamental_trends")):
            st.dataframe(
                pd.DataFrame(trend_rows), use_container_width=True, hide_index=True
            )
        if forecast is None:
            ai_label = t(lang, "unavailable")
        elif forecast["change"] > 0:
            ai_label = t(lang, "bullish")
        elif forecast["change"] < 0:
            ai_label = t(lang, "bearish")
        else:
            ai_label = t(lang, "neutral")
        fundamental_display = _signal_badge(
            fundamental_label, _signal_tone(fundamental_label, lang)
        )
        technical_display = _signal_badge(
            technical_label, _signal_tone(technical_label, lang)
        )
        sentiment_display = _signal_badge(
            sentiment_label, _signal_tone(sentiment_label, lang)
        )
        forecast_display = _signal_badge(ai_label, _signal_tone(ai_label, lang))
        conclusion_parts = [
            t(
                lang,
                "conclusion_main",
                symbol=symbol,
                fund=fundamental_display,
                technical=technical_display,
                sentiment=sentiment_display,
            )
        ]
        if forecast is not None:
            forecast_sentence = t(
                lang,
                "conclusion_forecast",
                model=forecast["model"],
                change=forecast["change"],
                price=forecast["price"],
                horizon=horizon_label,
            )
            conclusion_parts.append(
                f'<span class="signal-text signal-{_signal_tone(ai_label, lang)}">{forecast_sentence}</span>'
            )
        else:
            conclusion_parts.append(t(lang, "forecast_missing"))
        if not sentiment["count"]:
            conclusion_parts.append(t(lang, "news_missing"))
        conclusion_html = " ".join(conclusion_parts)
        conclusion_html += (
            f"<br><br><b>{t(lang, 'summary')}:</b> "
            f"{t(lang, 'summary_line', fund=fundamental_display, technical=technical_display, sentiment=sentiment_display, forecast=forecast_display)}"
        )
        st.divider()
        st.markdown(
            f'<div class="section-title">{t(lang,"conclusion")}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="conclusion">{conclusion_html}</div>', unsafe_allow_html=True
        )
    elif active_section == "technical":
        st.markdown(
            f'<div class="section-title">{t(lang,"technical_title")}</div>',
            unsafe_allow_html=True,
        )
        technical_value = (
            f"{tech['score']}/100"
            if isinstance(tech["score"], (int, float))
            else t(lang, "unavailable")
        )
        st.metric(t(lang, "technical_score"), technical_value)
        st.markdown(
            _signal_badge(tech["label"], _signal_tone(tech["label"], lang)),
            unsafe_allow_html=True,
        )
        st.info(tech["scoring_method"])
        st.dataframe(tech["table"], use_container_width=True, hide_index=True)
        st.plotly_chart(
            technical_chart(enriched, symbol, lang), use_container_width=True
        )
        with st.expander(t(lang, "last_sessions")):
            st.dataframe(
                enriched.tail(10).reset_index(),
                use_container_width=True,
                hide_index=True,
            )
    elif active_section == "news":
        st.markdown(
            f'<div class="section-title">{t(lang,"news_title")}</div>',
            unsafe_allow_html=True,
        )
        if sentiment["count"]:
            st.metric(t(lang, "sentiment_avg"), f"{sentiment['score']:+.2f}")
            sentiment_class = (
                "sentiment-positive"
                if sentiment["score"] > 0.15
                else (
                    "sentiment-negative"
                    if sentiment["score"] < -0.15
                    else "sentiment-neutral"
                )
            )
            st.markdown(
                f'<span class="sentiment-badge {sentiment_class}">{sentiment["label"]}</span>',
                unsafe_allow_html=True,
            )
            news_dates = [
                datetime.fromisoformat(item["publishedAt"].replace("Z", "+00:00"))
                for item in articles
                if item.get("publishedAt")
            ]
            if news_dates:
                date_fmt = "%d/%m/%Y" if lang == "fr" else "%Y-%m-%d"
                if lang == "fr":
                    news_range = f"du {min(news_dates).strftime(date_fmt)} au {max(news_dates).strftime(date_fmt)}"
                elif lang == "ar":
                    news_range = f"من {min(news_dates).strftime(date_fmt)} إلى {max(news_dates).strftime(date_fmt)}"
                else:
                    news_range = f"{min(news_dates).strftime(date_fmt)} to {max(news_dates).strftime(date_fmt)}"
            else:
                news_range = t(lang, "unavailable")
            st.caption(
                t(
                    lang,
                    "news_count",
                    count=sentiment["count"],
                    date_range=news_range,
                    method=sentiment["method"],
                )
            )
            st.caption(t(lang, "original_headlines"))
            st.caption(t(lang, "sentiment_language_hint"))
            st.caption(t(lang, "sentiment_scale_note"))
            if sentiment.get("non_english_count", 0):
                st.info(
                    t(
                        lang,
                        "sentiment_non_english_count",
                        count=sentiment["non_english_count"],
                    )
                )
            if sentiment.get("model_status") == "missing_dependencies":
                st.warning(t(lang, "finbert_missing"))
            elif sentiment.get("model_status") not in (None, "ready"):
                st.warning(t(lang, "finbert_load_error"))
                with st.expander(t(lang, "finbert_error_details")):
                    st.code(sentiment["model_status"])
            if sentiment["method"] != "FinBERT":
                st.info(t(lang, "lexical_warning"))
            p1, p2, p3 = st.columns(3)
            p1.metric(t(lang, "positives"), sentiment["positive"])
            p2.metric(t(lang, "neutrals"), sentiment["neutral"])
            p3.metric(t(lang, "negatives"), sentiment["negative"])
            with st.expander(t(lang, "top_headlines")):
                for item in sentiment["top_articles"]:
                    language_tag = (
                        f" · ⚠ {item['language']}"
                        if item.get("language") not in (None, "en", "unknown")
                        else ""
                    )
                    st.markdown(
                        f"- **[{item['title']}]({item['url']})** · {item['label']} · {item['source']}{language_tag}"
                    )
            for item in sentiment["articles"]:
                with st.container(border=True):
                    st.markdown(f"**[{item['title']}]({item['url']})**")
                    language_tag = (
                        f" · ⚠ {item['language']}"
                        if item.get("language") not in (None, "en", "unknown")
                        else ""
                    )
                    st.caption(
                        f"{item['date']} · {item['source']} · {item['label']} ({item['score']:+.2f}){language_tag}"
                    )
        else:
            st.info(sentiment["message"])
    elif active_section == "forecast":
        st.markdown(
            f'<div class="section-title">{t(lang, "forecast_title", horizon=horizon_label)}</div>',
            unsafe_allow_html=True,
        )
        if forecast_error is not None:
            st.warning(t(lang, "forecast_error", error=forecast_error))
        elif forecast is not None and results is not None:
            st.caption(t(lang, "model_used", model=forecast["model"]))
            st.caption(pillar_status)
            price_column, predicted_column, change_column = st.columns(3)
            price_column.metric(
                t(lang, "forecast_current_price"),
                f"${forecast['current_price']:,.2f}",
            )
            predicted_column.metric(
                t(lang, "forecast_price", horizon=horizon_label),
                f"${forecast['price']:,.2f}",
            )
            change_column.metric(
                t(lang, "forecast_change"),
                f"${forecast['price_change']:+,.2f}",
                f"{forecast['change']:+.2f}%",
            )

            chart_history_window = max(60, min(forecast["horizon"], 126))
            recent_prices = enriched.tail(chart_history_window)
            last_date = pd.Timestamp(recent_prices.index[-1])
            forecast_date = last_date + pd.offsets.BDay(forecast["horizon"])
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=recent_prices.index,
                    y=recent_prices["Close"],
                    mode="lines",
                    name=t(lang, "forecast_chart_history"),
                    line={"color": "#2878b5", "width": 2.5},
                    hovertemplate=(
                        "%{x|%b %d, %Y}<br>$%{y:,.2f}<extra>%{fullData.name}</extra>"
                    ),
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=[forecast_date],
                    y=[forecast["price"]],
                    mode="markers",
                    name=t(lang, "forecast_chart_prediction"),
                    marker={
                        "size": 12,
                        "color": "#1d8178",
                        "line": {"color": "white", "width": 2},
                    },
                    error_y={
                        "type": "data",
                        "symmetric": False,
                        "array": [
                            max(0, forecast["interval_90_high"] - forecast["price"])
                        ],
                        "arrayminus": [
                            max(0, forecast["price"] - forecast["interval_90_low"])
                        ],
                        "visible": True,
                        "color": "#f4c36b",
                        "thickness": 2,
                        "width": 7,
                    },
                    hovertemplate=(
                        "%{x|%b %d, %Y}<br>$%{y:,.2f}<extra>%{fullData.name}</extra>"
                    ),
                )
            )
            fig.update_layout(
                title=t(lang, "forecast_chart_title"),
                xaxis_title=t(lang, "chart_date"),
                yaxis_title=t(lang, "chart_close_price"),
                template="plotly_dark",
                font={"color": "#d5dfeb"},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#172436",
                legend={"orientation": "h", "y": 1.08},
                hovermode="x unified",
                height=360,
                margin={"l": 12, "r": 18, "t": 60, "b": 12},
                xaxis={
                    "showgrid": False,
                    "rangeslider": {"visible": False},
                },
                yaxis={"gridcolor": "#e8eef3", "tickprefix": "$", "ticksuffix": ""},
            )
            st.plotly_chart(fig, use_container_width=True)
            interval_columns = st.columns(3)
            interval_columns[0].metric(
                t(lang, "interval_50"),
                f"${forecast['interval_50_low']:,.2f} – ${forecast['interval_50_high']:,.2f}",
            )
            interval_columns[1].metric(
                t(lang, "interval_90"),
                f"${forecast['interval_90_low']:,.2f} – ${forecast['interval_90_high']:,.2f}",
            )
            interval_columns[2].metric(
                t(lang, "probability_up"),
                f"{forecast['probability_up']:.0%} / {forecast['probability_down']:.0%}",
                help=t(lang, "probability_pair"),
            )
            st.caption(t(lang, "forecast_interval_note"))

    elif active_section == "evaluation_tab":
        st.markdown(
            f'<div class="section-title">{t(lang,"evaluation_title")}</div>',
            unsafe_allow_html=True,
        )
        st.caption(t(lang, "evaluation_description"))
        st.info(t(lang, "evaluation_split"))
        try:
            evaluation_pillar_features = make_pillar_feature_frame(
                indicators=enriched,
                history=pillar_history,
                symbol=symbol,
                fundamental_score=fund.get("score"),
                technical_score=tech.get("score"),
                sentiment_score=sentiment.get("score"),
                sentiment_count=sentiment.get("count", 0),
                horizon=1,
            )
            evaluation_current_features = evaluation_pillar_features.attrs[
                "current_features"
            ]
            evaluation_pillar_ready = (
                len(evaluation_pillar_features) >= 100
                and evaluation_current_features.notna().all()
            )
            evaluation_features = (
                evaluation_pillar_features
                if evaluation_pillar_ready
                else make_feature_frame(enriched, horizon=1)
            )
            with st.spinner(t(lang, "spinner")):
                evaluation = _evaluate_model(prices, evaluation_features)
                walk_forward = _evaluate_walk_forward(prices, evaluation_features)
            currency = info.get("currency") or t(lang, "evaluation_currency_unknown")
            metrics = evaluation["metrics"]
            baseline = evaluation["baseline_metrics"]
            mean_baseline = evaluation["mean_baseline_metrics"]
            metric_columns = st.columns(6)
            metric_columns[0].metric(
                t(lang, "evaluation_mae"),
                f"{currency} {metrics['MAE']:,.2f}",
                help=t(lang, "evaluation_mae_help"),
            )
            metric_columns[1].metric(
                t(lang, "evaluation_rmse"),
                f"{currency} {metrics['RMSE']:,.2f}",
                help=t(lang, "evaluation_rmse_help"),
            )
            mape_value = (
                f"{metrics['MAPE']:.2f}%"
                if np.isfinite(metrics["MAPE"])
                else t(lang, "not_available")
            )
            metric_columns[2].metric(
                t(lang, "evaluation_mape"),
                mape_value,
                help=t(lang, "evaluation_mape_help"),
            )
            mase_value = (
                f"{metrics['MASE']:.2f}"
                if np.isfinite(metrics["MASE"])
                else t(lang, "not_available")
            )
            metric_columns[3].metric(
                t(lang, "evaluation_mase"),
                mase_value,
                help=t(lang, "evaluation_mase_help"),
            )
            metric_columns[4].metric(
                t(lang, "evaluation_direction"),
                f"{metrics['Directional Accuracy']:.1f}%",
                help=t(lang, "evaluation_direction_help"),
            )
            metric_columns[5].metric(
                t(lang, "evaluation_samples"), f"{evaluation['test_count']}"
            )

            period_format = "%d/%m/%Y" if lang == "fr" else "%Y-%m-%d"
            test_start = evaluation["period_start"].strftime(period_format)
            test_end = evaluation["period_end"].strftime(period_format)
            st.caption(
                t(
                    lang,
                    "evaluation_period",
                    start=test_start,
                    end=test_end,
                    count=evaluation["test_count"],
                    train=evaluation["train_count"],
                    validation=evaluation["validation_count"],
                    test=evaluation["test_count"],
                )
            )
            st.caption(t(lang, "evaluation_validation_choice"))

            selected_name = (
                t(lang, "linear")
                if evaluation["model_key"] == "Régression linéaire"
                else (
                    t(lang, "linear_numpy")
                    if evaluation["model_key"] == "Régression linéaire (NumPy)"
                    else (
                        t(lang, "forest")
                        if evaluation["model_key"] == "Forêt aléatoire"
                        else (
                            t(lang, "boosting")
                            if evaluation["model_key"] == "Gradient boosting"
                            else t(lang, "zero_baseline")
                        )
                    )
                )
            )
            rows = evaluation["rows"].copy()
            actual_label = t(lang, "evaluation_actual")
            predicted_label = t(lang, "evaluation_predicted")
            baseline_label = t(lang, "evaluation_benchmark")
            date_label = t(lang, "evaluation_date")
            price_chart = go.Figure()
            price_chart.add_trace(
                go.Scatter(
                    x=rows["Date"],
                    y=rows["Actual close"],
                    name=actual_label,
                    mode="lines",
                )
            )
            price_chart.add_trace(
                go.Scatter(
                    x=rows["Date"],
                    y=rows["Predicted close"],
                    name=f"{predicted_label} · {selected_name}",
                    mode="lines",
                )
            )
            price_chart.add_trace(
                go.Scatter(
                    x=rows["Date"],
                    y=rows["Last-close baseline"],
                    name=baseline_label,
                    mode="lines",
                    line={"dash": "dot"},
                )
            )
            price_chart.add_trace(
                go.Scatter(
                    x=rows["Date"],
                    y=rows["Mean-return baseline"],
                    name=t(lang, "evaluation_mean_return"),
                    mode="lines",
                    line={"dash": "dash"},
                )
            )
            price_chart.add_trace(
                go.Scatter(
                    x=rows["Date"],
                    y=rows["Always-up baseline"],
                    name=t(lang, "evaluation_always_up"),
                    mode="lines",
                    line={"dash": "dashdot"},
                )
            )
            price_chart.add_trace(
                go.Scatter(
                    x=rows["Date"],
                    y=rows["Moving-average baseline"],
                    name=t(lang, "evaluation_sma_baseline"),
                    mode="lines",
                    line={"dash": "longdash"},
                )
            )
            price_chart.update_layout(
                title=t(lang, "evaluation_chart_title"),
                xaxis_title=date_label,
                yaxis_title=f"{t(lang,'close')} ({currency})",
                template="plotly_dark",
                font={"color": "#d5dfeb"},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#172436",
                legend={"orientation": "h"},
            )
            st.plotly_chart(price_chart, use_container_width=True)

            return_chart = go.Figure()
            return_chart.add_trace(
                go.Scatter(
                    x=rows["Date"],
                    y=rows["Actual return (%)"],
                    name=t(lang, "evaluation_return_actual"),
                    mode="lines",
                )
            )
            return_chart.add_trace(
                go.Scatter(
                    x=rows["Date"],
                    y=rows["Predicted return (%)"],
                    name=t(lang, "evaluation_return_predicted"),
                    mode="lines",
                )
            )
            return_chart.add_hline(y=0, line_dash="dot", line_color="#8293a7")
            return_chart.update_layout(
                title=t(lang, "evaluation_return_title"),
                xaxis_title=date_label,
                yaxis_title=t(lang, "evaluation_return_actual"),
                template="plotly_dark",
                font={"color": "#d5dfeb"},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#172436",
                legend={"orientation": "h"},
            )
            st.plotly_chart(return_chart, use_container_width=True)

            st.markdown(f"#### {t(lang,'evaluation_walk_title')}")
            wf_metrics = walk_forward["metrics"]
            wf_baseline = walk_forward["baseline_metrics"]
            wf_mean = walk_forward["mean_baseline_metrics"]
            wf_always = walk_forward["always_up_metrics"]
            wf_sma = walk_forward["sma_metrics"]
            st.caption(
                t(
                    lang,
                    "evaluation_walk_note",
                    folds=walk_forward["fold_count"],
                    count=walk_forward["test_count"],
                )
            )
            walk_table = pd.DataFrame(
                [
                    {
                        t(lang, "table_model"): name,
                        t(lang, "evaluation_mae"): f"{currency} {metric['MAE']:,.2f}",
                        t(lang, "evaluation_rmse"): f"{currency} {metric['RMSE']:,.2f}",
                        t(
                            lang, "evaluation_direction"
                        ): f"{metric['Directional Accuracy']:.1f}%",
                        t(lang, "evaluation_samples"): metric["count"],
                    }
                    for name, metric in (
                        (selected_name, wf_metrics),
                        (baseline_label, wf_baseline),
                        (t(lang, "evaluation_always_up"), wf_always),
                        (t(lang, "evaluation_sma_baseline"), wf_sma),
                    )
                ]
            )
            st.dataframe(walk_table, use_container_width=True, hide_index=True)
            backtest = walk_forward["backtest"]
            st.markdown(f"#### {t(lang, 'evaluation_backtest')}")
            bt_columns = st.columns(3)
            bt_columns[0].metric(
                t(lang, "backtest_sharpe"),
                (
                    f"{backtest['Sharpe']:.2f}"
                    if np.isfinite(backtest["Sharpe"])
                    else t(lang, "not_available")
                ),
            )
            bt_columns[1].metric(
                t(lang, "backtest_drawdown"),
                (
                    f"{backtest['Max Drawdown']:.1%}"
                    if np.isfinite(backtest["Max Drawdown"])
                    else t(lang, "not_available")
                ),
            )
            bt_columns[2].metric(
                t(lang, "backtest_win_rate"),
                (
                    f"{backtest['Win Rate']:.1f}%"
                    if np.isfinite(backtest["Win Rate"])
                    else t(lang, "not_available")
                ),
            )
            st.caption(
                t(
                    lang,
                    "backtest_costs",
                    fees=backtest["Fees bps"],
                    slippage=backtest["Slippage bps"],
                )
            )
            wf_rows = walk_forward["rows"]
            wf_chart = go.Figure()
            wf_chart.add_trace(
                go.Scatter(
                    x=wf_rows["Date"],
                    y=wf_rows["Actual close"],
                    name=actual_label,
                    mode="lines",
                )
            )
            wf_chart.add_trace(
                go.Scatter(
                    x=wf_rows["Date"],
                    y=wf_rows["Predicted close"],
                    name=f"{predicted_label} · walk-forward",
                    mode="lines",
                )
            )
            wf_chart.add_trace(
                go.Scatter(
                    x=wf_rows["Date"],
                    y=wf_rows["Last-close baseline"],
                    name=baseline_label,
                    mode="lines",
                    line={"dash": "dot"},
                )
            )
            wf_chart.add_trace(
                go.Scatter(
                    x=wf_rows["Date"],
                    y=wf_rows["Always-up baseline"],
                    name=t(lang, "evaluation_always_up"),
                    mode="lines",
                    line={"dash": "dashdot"},
                )
            )
            wf_chart.add_trace(
                go.Scatter(
                    x=wf_rows["Date"],
                    y=wf_rows["Moving-average baseline"],
                    name=t(lang, "evaluation_sma_baseline"),
                    mode="lines",
                    line={"dash": "longdash"},
                )
            )
            wf_chart.update_layout(
                title=t(lang, "evaluation_walk_title"),
                xaxis_title=date_label,
                yaxis_title=f"{t(lang,'close')} ({currency})",
                template="plotly_dark",
                font={"color": "#d5dfeb"},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#172436",
                legend={"orientation": "h"},
            )
            st.plotly_chart(wf_chart, use_container_width=True)

            error_column, error_distribution_column = st.columns(2)
            error_column.markdown(f"#### {t(lang,'evaluation_error_title')}")
            error_chart = go.Figure(
                go.Scatter(
                    x=rows["Date"],
                    y=rows["Error"],
                    mode="lines+markers",
                    name=t(lang, "evaluation_error"),
                )
            )
            error_chart.add_hline(y=0, line_dash="dash", line_color="#8da2bd")
            error_chart.update_layout(
                xaxis_title=date_label,
                yaxis_title=f"{t(lang,'evaluation_error')} ({currency})",
                template="plotly_dark",
                font={"color": "#d5dfeb"},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#172436",
            )
            error_column.plotly_chart(error_chart, use_container_width=True)
            error_distribution_column.markdown(
                f"#### {t(lang,'evaluation_distribution_title')}"
            )
            histogram = go.Figure(
                go.Histogram(
                    x=rows["Error"], nbinsx=20, name=t(lang, "evaluation_error")
                )
            )
            histogram.update_layout(
                xaxis_title=f"{t(lang,'evaluation_error')} ({currency})",
                yaxis_title=t(lang, "evaluation_report_observations"),
                template="plotly_dark",
                font={"color": "#d5dfeb"},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#172436",
            )
            error_distribution_column.plotly_chart(histogram, use_container_width=True)

            comparison_rows = []
            for name, values in (
                (selected_name, metrics),
                (baseline_label, baseline),
                (t(lang, "evaluation_always_up"), evaluation["always_up_metrics"]),
                (t(lang, "evaluation_sma_baseline"), evaluation["sma_metrics"]),
                (t(lang, "evaluation_mean_return"), mean_baseline),
            ):
                comparison_rows.append(
                    {
                        t(lang, "table_model"): name,
                        t(lang, "evaluation_mae"): f"{currency} {values['MAE']:,.2f}",
                        t(lang, "evaluation_rmse"): f"{currency} {values['RMSE']:,.2f}",
                        t(lang, "evaluation_mape"): (
                            f"{values['MAPE']:.2f}%"
                            if np.isfinite(values["MAPE"])
                            else t(lang, "not_available")
                        ),
                        t(lang, "evaluation_mase"): (
                            f"{values['MASE']:.2f}"
                            if np.isfinite(values["MASE"])
                            else t(lang, "not_available")
                        ),
                        t(
                            lang, "evaluation_direction"
                        ): f"{values['Directional Accuracy']:.1f}%",
                    }
                )
            st.markdown(f"#### {t(lang,'evaluation_comparison_title')}")
            st.dataframe(
                pd.DataFrame(comparison_rows), use_container_width=True, hide_index=True
            )

            st.markdown(f"#### {t(lang,'evaluation_worst')}")
            worst = rows.nlargest(5, "Absolute error")[
                ["Date", "Actual close", "Predicted close", "Error", "Absolute error"]
            ].rename(
                columns={
                    "Date": date_label,
                    "Actual close": actual_label,
                    "Predicted close": predicted_label,
                    "Error": t(lang, "evaluation_error"),
                    "Absolute error": t(lang, "evaluation_abs_error"),
                }
            )
            st.dataframe(worst, use_container_width=True, hide_index=True)

            by_month = rows.copy()
            by_month[t(lang, "evaluation_month")] = pd.to_datetime(
                by_month["Date"]
            ).dt.strftime("%Y-%m")
            monthly = by_month.groupby(t(lang, "evaluation_month"), as_index=False).agg(
                **{
                    t(lang, "evaluation_month_mae"): ("Absolute error", "mean"),
                    t(lang, "evaluation_month_bias"): ("Error", "mean"),
                }
            )
            monthly = monthly.nlargest(5, t(lang, "evaluation_month_mae")).copy()
            monthly[t(lang, "evaluation_month_mae")] = monthly[
                t(lang, "evaluation_month_mae")
            ].map(lambda value: f"{currency} {value:,.2f}")
            monthly[t(lang, "evaluation_month_bias")] = monthly[
                t(lang, "evaluation_month_bias")
            ].map(lambda value: f"{currency} {value:+,.2f}")
            st.markdown(f"#### {t(lang,'evaluation_monthly_worst')}")
            st.dataframe(monthly, use_container_width=True, hide_index=True)

            better_count = sum(
                metrics["MAE"] < value["MAE"] for value in (baseline, mean_baseline)
            )
            st.info(
                t(
                    lang,
                    "evaluation_score_summary",
                    better=better_count,
                    total=2,
                    folds=walk_forward["fold_count"],
                    rows=walk_forward["test_count"],
                )
            )
            if not np.isfinite(metrics["MAPE"]):
                st.caption(t(lang, "evaluation_mape_na"))
            elif metrics["mape_count"] < metrics["count"]:
                st.caption(
                    t(
                        lang,
                        "evaluation_mape_partial",
                        count=metrics["mape_count"],
                        total=metrics["count"],
                    )
                )
            st.caption(t(lang, "evaluation_disclaimer"))
            st.markdown(f"#### {t(lang, 'known_limitations')}")
            st.info(t(lang, "known_limitations_text"))

            report = {
                t(lang, "symbol"): symbol,
                t(lang, "evaluation_report_period"): f"{test_start} — {test_end}",
                t(lang, "evaluation_report_model"): selected_name,
                t(lang, "evaluation_report_observations"): evaluation["test_count"],
                t(lang, "evaluation_report_train"): evaluation["train_count"],
                t(lang, "evaluation_report_validation"): evaluation["validation_count"],
                t(lang, "evaluation_report_currency"): currency,
                t(lang, "evaluation_report_mae"): metrics["MAE"],
                t(lang, "evaluation_report_rmse"): metrics["RMSE"],
                t(lang, "evaluation_report_mape"): metrics["MAPE"],
                t(lang, "evaluation_report_direction"): metrics["Directional Accuracy"],
                t(lang, "evaluation_report_baseline_mae"): baseline["MAE"],
                t(lang, "evaluation_report_baseline_rmse"): baseline["RMSE"],
                t(lang, "evaluation_report_baseline_mape"): baseline["MAPE"],
                t(lang, "evaluation_report_baseline_direction"): baseline[
                    "Directional Accuracy"
                ],
                t(lang, "evaluation_report_mean_baseline_mae"): mean_baseline["MAE"],
                t(lang, "evaluation_report_mean_baseline_rmse"): mean_baseline["RMSE"],
                t(lang, "evaluation_report_mean_baseline_mape"): mean_baseline["MAPE"],
                t(lang, "evaluation_report_mean_baseline_direction"): mean_baseline[
                    "Directional Accuracy"
                ],
                t(lang, "evaluation_report_mase"): metrics["MASE"],
                t(lang, "evaluation_report_walk_folds"): walk_forward["fold_count"],
                t(lang, "evaluation_report_walk_observations"): walk_forward[
                    "test_count"
                ],
                t(
                    lang, "evaluation_report_walk_period"
                ): f"{walk_forward['period_start'].strftime(period_format)} — {walk_forward['period_end'].strftime(period_format)}",
                t(lang, "evaluation_report_walk_mae"): wf_metrics["MAE"],
                t(lang, "evaluation_report_walk_rmse"): wf_metrics["RMSE"],
                t(lang, "evaluation_report_walk_mape"): wf_metrics["MAPE"],
                t(lang, "evaluation_report_walk_direction"): wf_metrics[
                    "Directional Accuracy"
                ],
                t(lang, "evaluation_report_walk_baseline_mae"): wf_baseline["MAE"],
                t(lang, "evaluation_report_walk_mean_mae"): wf_mean["MAE"],
                t(lang, "evaluation_report_summary"): t(
                    lang,
                    "evaluation_score_summary",
                    better=better_count,
                    total=2,
                    folds=walk_forward["fold_count"],
                    rows=walk_forward["test_count"],
                ),
                t(lang, "evaluation_report_limits"): t(lang, "evaluation_disclaimer"),
            }
            report_df = pd.DataFrame([report])
            export_rows = rows.rename(
                columns={
                    "Date": date_label,
                    "Actual close": actual_label,
                    "Predicted close": predicted_label,
                    "Last-close baseline": baseline_label,
                    "Mean-return baseline": t(lang, "evaluation_mean_return"),
                    "Actual return (%)": t(lang, "evaluation_return_actual"),
                    "Predicted return (%)": t(lang, "evaluation_return_predicted"),
                    "Return error (percentage points)": t(
                        lang, "evaluation_return_error"
                    ),
                    "Selected model": t(lang, "evaluation_report_model"),
                    "Fold": t(lang, "evaluation_walk_fold"),
                    "Error": t(lang, "evaluation_error"),
                    "Absolute error": t(lang, "evaluation_abs_error"),
                    "Percentage error": t(lang, "evaluation_pct_error"),
                    "Direction correct": t(lang, "evaluation_direction_correct"),
                }
            )
            downloads = st.columns(2)
            downloads[0].download_button(
                t(lang, "evaluation_export_report"),
                report_df.to_csv(index=False).encode("utf-8-sig"),
                file_name=f"{symbol.lower()}_evaluation_report.csv",
                mime="text/csv",
                use_container_width=True,
            )
            downloads[1].download_button(
                t(lang, "evaluation_export_rows"),
                export_rows.to_csv(index=False).encode("utf-8-sig"),
                file_name=f"{symbol.lower()}_evaluation_test.csv",
                mime="text/csv",
                use_container_width=True,
            )
        except Exception as exc:
            error_messages = {
                "not_enough_history": "evaluation_insufficient_history",
                "not_enough_aligned_prices": "evaluation_no_aligned_prices",
                "not_enough_walk_forward_history": "evaluation_walk_insufficient",
                "no_labelled_rows": "evaluation_no_labelled_rows",
                "no_closing_prices": "evaluation_no_closing_prices",
                "no_feature_rows": "evaluation_no_feature_rows",
            }
            error_key = error_messages.get(str(exc))
            st.warning(
                t(lang, error_key) if error_key else t(lang, "evaluation_tab_error")
            )
            if not error_key:
                with st.expander(t(lang, "evaluation_error_details")):
                    st.code(f"{type(exc).__name__}: {exc}")
else:
    st.info(t(lang, "prompt", run=t(lang, "run")))
