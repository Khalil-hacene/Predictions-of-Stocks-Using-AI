"""Graded company fundamentals with explicit availability and valuation caveats."""
import math

import numpy as np
import pandas as pd

from src.i18n import t


# Weights apply to available, comparable metrics only. Missing values are shown
# explicitly and do not silently receive a score.
WEIGHTS = {
    "trailingPE": 0.08, "priceToBook": 0.06, "enterpriseToEbitda": 0.08,
    "dcf_margin_of_safety": 0.14, "profitMargins": 0.10,
    "returnOnEquity": 0.10, "returnOnCapitalEmployed": 0.10,
    "debtToEquity": 0.08, "currentRatio": 0.06,
    "interestCoverage": 0.06, "freeCashflow": 0.14,
}


def _number(value):
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def _sigmoid_score(value, center, scale, higher_is_better=True):
    """Smooth, transparent fallback score; provider peer percentiles take priority."""
    direction = 1 if higher_is_better else -1
    z = max(-8, min(8, direction * (value - center) / max(scale, 1e-9)))
    return 100 / (1 + math.exp(-z))


def _dcf_range(info):
    """Small three-scenario equity value estimate using current FCF (not guidance)."""
    if "financial" in str(info.get("sector", "")).lower():
        return None
    fcf = _number(info.get("freeCashflow"))
    shares = _number(info.get("sharesOutstanding"))
    price = _number(info.get("currentPrice") or info.get("regularMarketPrice"))
    debt = _number(info.get("totalDebt")) or 0
    cash = _number(info.get("totalCash")) or 0
    if not fcf or fcf <= 0 or not shares or shares <= 0 or not price:
        return None
    scenarios = []
    # Scenarios use deliberately conservative assumptions, capped terminal growth,
    # and a ten-year explicit period. They are illustrations, not provider targets.
    for growth, discount, terminal in ((0.00, 0.12, 0.01), (0.05, 0.10, 0.02), (0.10, 0.09, 0.025)):
        pv = sum(fcf * (1 + growth) ** year / (1 + discount) ** year for year in range(1, 11))
        terminal_fcf = fcf * (1 + growth) ** 10 * (1 + terminal)
        terminal_value = terminal_fcf / max(discount - terminal, 0.01)
        pv += terminal_value / (1 + discount) ** 10
        scenarios.append(max(0, (pv - debt + cash) / shares))
    low, base, high = sorted(scenarios)
    margin = (base - price) / price
    position=np.clip((price-low)/max(high-low,1e-9),0,1)
    score=100*(1-position)
    return {"low": low, "base": base, "high": high, "margin": margin, "score": score, "price_position": float(position)}


def _history_trends(info):
    """Show multi-year statement trends only when enough dated data is available."""
    annual_income=info.get("_annual_income")
    annual_cashflow=info.get("_annual_cashflow")
    quarterly_income=info.get("_quarterly_income")
    quarterly_cashflow=info.get("_quarterly_cashflow")

    def series(frame,candidates):
        if not isinstance(frame,pd.DataFrame) or frame.empty:
            return None
        row=next((name for name in candidates if name in frame.index),None)
        return pd.to_numeric(frame.loc[row],errors="coerce").dropna().sort_index() if row else None

    def change(values):
        if values is None or len(values)<3:
            return None
        first,last=float(values.iloc[0]),float(values.iloc[-1])
        return (last-first)/abs(first) if first else None

    income=annual_income if isinstance(annual_income,pd.DataFrame) and annual_income.shape[1]>=3 else quarterly_income
    cash=annual_cashflow if isinstance(annual_cashflow,pd.DataFrame) and annual_cashflow.shape[1]>=3 else quarterly_cashflow
    revenue=series(income,("Total Revenue","Operating Revenue"))
    earnings=series(income,("Net Income","Net Income Common Stockholders"))
    fcf=series(cash,("Free Cash Flow",))
    if income is quarterly_income:
        revenue=revenue.iloc[-20:] if revenue is not None else None
        earnings=earnings.iloc[-20:] if earnings is not None else None
        revenue=revenue.groupby(np.arange(len(revenue))//4).sum() if revenue is not None and len(revenue)>=12 else None
        earnings=earnings.groupby(np.arange(len(earnings))//4).sum() if earnings is not None and len(earnings)>=12 else None
    if cash is quarterly_cashflow:
        fcf=fcf.iloc[-20:] if fcf is not None else None
        fcf=fcf.groupby(np.arange(len(fcf))//4).sum() if fcf is not None and len(fcf)>=12 else None
    margins=(earnings/revenue).dropna() if earnings is not None and revenue is not None else None
    return {"revenue":change(revenue),"earnings":change(earnings),"margin":change(margins),"fcf":change(fcf)}


def analyze_fundamentals(info, lang="fr"):
    """Return continuous 0–100 metric grades and a weighted aggregate.

    If the data provider includes `sector_peer_metrics`, rank metrics by empirical
    sector percentile. Otherwise use disclosed smooth heuristics and mark the peer
    comparison unavailable; this avoids presenting fake percentile ranks.
    """
    labels = {
        "trailingPE": "pe", "priceToBook": "pb", "enterpriseToEbitda": "ev_ebitda",
        "dcf_margin_of_safety": "dcf_mos", "profitMargins": "margin",
        "returnOnEquity": "roe", "returnOnCapitalEmployed": "roic",
        "debtToEquity": "debt_equity", "currentRatio": "current_ratio",
        "interestCoverage": "interest_coverage", "freeCashflow": "free_cash",
    }
    kinds = {"trailingPE":"num","priceToBook":"num","enterpriseToEbitda":"num",
             "dcf_margin_of_safety":"pct","profitMargins":"pct","returnOnEquity":"pct",
             "returnOnCapitalEmployed":"pct","debtToEquity":"num","currentRatio":"num",
             "interestCoverage":"num","freeCashflow":"money"}
    values = {key: _number(info.get(key)) for key in WEIGHTS if key != "dcf_margin_of_safety"}
    dcf = _dcf_range(info)
    values["dcf_margin_of_safety"] = dcf["margin"] if dcf else None

    # Sector peer values must come from comparable companies and the same provider.
    peer_data = info.get("sector_peer_metrics") or {}
    peer_counts = {}
    rows = []
    metric_scores = {}
    for key, weight in WEIGHTS.items():
        value = values.get(key)
        peers = [_number(x) for x in peer_data.get(key, [])]
        peers = [x for x in peers if x is not None and value is not None]
        if value is None or (key in ("trailingPE", "priceToBook", "enterpriseToEbitda") and value <= 0):
            score = None
            display_value = t(lang, "unavailable")
            grade = t(lang, "unavailable")
        else:
            if key == "dcf_margin_of_safety":
                score=dcf["score"]
                grade=f"{score:.0f}/100 · {t(lang, 'dcf_range_grade')}"
            elif peers:
                percentile = 100 * (sum(x < value for x in peers) + .5 * sum(x == value for x in peers)) / len(peers)
                # Lower valuation multiples are generally more attractive; all other
                # metrics are ranked high-to-low. Percentile is a peer-relative grade.
                score = 100 - percentile if key in ("trailingPE", "priceToBook", "enterpriseToEbitda", "debtToEquity") else percentile
                peer_counts[key] = len(peers)
                grade = f"{score:.0f}/100 · {percentile:.0f}e {t(lang, 'peer_percentile')}"
            else:
                settings = {
                    "trailingPE": (20, 20, False), "priceToBook": (3, 3, False),
                    "enterpriseToEbitda": (12, 10, False), "dcf_margin_of_safety": (0.10, 0.35, True),
                    "profitMargins": (0.10, 0.15, True), "returnOnEquity": (0.12, 0.20, True),
                    "returnOnCapitalEmployed": (0.12, 0.20, True), "debtToEquity": (100, 120, False),
                    "currentRatio": (1.5, 1.5, True), "interestCoverage": (5, 5, True),
                    "freeCashflow": (0, max(abs(value) * .5, 1), True),
                }
                center, scale, higher = settings[key]
                score = _sigmoid_score(value, center, scale, higher)
                grade = f"{score:.0f}/100 · {t(lang, 'heuristic_score')}"
            metric_scores[key] = score
            shown = value * 100 if kinds[key] == "pct" else value
            display_value = f"{shown:,.2f}%" if kinds[key] == "pct" else f"${shown:,.0f}" if kinds[key] == "money" else f"{shown:,.2f}"
        rows.append({
            t(lang, "table_metric"): t(lang, labels[key]),
            t(lang, "table_value"): display_value,
            t(lang, "metric_grade"): grade,
            t(lang, "metric_weight"): f"{weight:.0%}",
            t(lang, "data_warning"): "" if score is not None else t(lang, "metric_missing_warning"),
        })

    present_weight = sum(WEIGHTS[key] for key in metric_scores)
    score = round(sum(metric_scores[key] * WEIGHTS[key] for key in metric_scores) / present_weight) if present_weight else None
    # Financial institutions have structurally different leverage and cash flows;
    # negative FCF also makes a conventional DCF unusable.
    sector = str(info.get("sector", "")).lower()
    dcf_note = None
    if "financial" in sector or _number(info.get("freeCashflow")) is not None and _number(info.get("freeCashflow")) <= 0:
        dcf_note = t(lang, "dcf_unreliable")
    trends = _history_trends(info)
    quarter = info.get("mostRecentQuarter")
    try:
        quarter = pd.to_datetime(quarter, unit="s", utc=True).strftime("%Y-%m-%d") if quarter else t(lang, "unavailable")
    except (TypeError, ValueError, OverflowError):
        quarter = str(quarter) if quarter else t(lang, "unavailable")
    label_key = "positive" if score is not None and score >= 60 else "negative" if score is not None and score < 40 else "neutral"
    if score is None:
        label_key = "unavailable"
    explanation = t(lang, "fundamental_weighted_explanation", score=score if score is not None else t(lang, "not_available"), available=len(metric_scores), total=len(WEIGHTS), weight=present_weight * 100)
    if not peer_counts:
        explanation += " " + t(lang, "peer_data_unavailable")
    return {
        "table": pd.DataFrame(rows), "score": score if score is not None else t(lang, "not_available"),
        "label": t(lang, label_key), "explanation": explanation, "scoring_method": explanation,
        "passed": len(metric_scores), "available": len(metric_scores), "metric_scores": metric_scores,
        "weights": WEIGHTS.copy(), "peer_counts": peer_counts, "quarter": quarter,
        "trends": trends, "dcf": dcf, "dcf_note": dcf_note,
        "missing": [key for key in WEIGHTS if key not in metric_scores],
    }
