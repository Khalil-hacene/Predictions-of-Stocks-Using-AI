"""External market data access; missing data is reported rather than invented."""

import os
from pathlib import Path
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
import re
from urllib.parse import urlsplit, urlunsplit
import xml.etree.ElementTree as ET
import requests
import yfinance as yf
from src.i18n import t

# yfinance normally writes its timezone cache to the user profile. Keep the
# cache inside this project so the app can run in restricted environments.
_CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "yfinance-cache"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)
yf.set_tz_cache_location(str(_CACHE_DIR))


class DataUnavailable(RuntimeError):
    pass


def fetch_prices(symbol, period="2y", lang="fr"):
    try:
        data = yf.Ticker(symbol).history(period=period, auto_adjust=True)
    except Exception as exc:
        error = t(lang, "price_fetch_error", symbol=symbol, error=exc)
        raise DataUnavailable(error) from exc
    if data is None or data.empty:
        raise DataUnavailable(t(lang, "price_missing", symbol=symbol))
    needed = ["Open", "High", "Low", "Close", "Volume"]
    if any(c not in data for c in needed):
        raise DataUnavailable(t(lang, "price_incomplete"))
    return data[needed].dropna(subset=["Close"])


def fetch_fundamentals(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}
        # Yahoo's screener can return sector peers and comparable ratios in one
        # request. Failure is non-fatal; the score then labels its heuristic fallback.
        sector = info.get("sector")
        if sector:
            try:
                query = yf.EquityQuery(
                    "and",
                    [
                        yf.EquityQuery("eq", ["sector", sector]),
                        yf.EquityQuery("eq", ["region", "us"]),
                    ],
                )
                result = yf.screen(
                    query, size=100, sortField="intradaymarketcap", sortAsc=False
                )
                quote_fields = {
                    "trailingPE": "trailingPE",
                    "priceToBook": "priceToBook",
                    "enterpriseToEbitda": "enterpriseToEbitda",
                    "profitMargins": "profitMargins",
                    "returnOnEquity": "returnOnEquity",
                    "returnOnCapitalEmployed": "returnOnCapitalEmployed",
                    "debtToEquity": "debtToEquity",
                    "currentRatio": "currentRatio",
                    "interestCoverage": "interestCoverage",
                }
                peers = {key: [] for key in quote_fields}
                peers["freeCashflowYield"] = []
                for quote in result.get("quotes", []):
                    if str(quote.get("symbol", "")).upper() == symbol.upper():
                        continue
                    for metric, field in quote_fields.items():
                        value = quote.get(field)
                        if isinstance(value, (int, float)) and value == value:
                            peers[metric].append(float(value))
                    peer_cash_flow = quote.get("freeCashflow")
                    peer_market_cap = quote.get("marketCap")
                    if (
                        isinstance(peer_cash_flow, (int, float))
                        and isinstance(peer_market_cap, (int, float))
                        and peer_market_cap > 0
                    ):
                        peers["freeCashflowYield"].append(
                            float(peer_cash_flow) / float(peer_market_cap)
                        )
                info["sector_peer_metrics"] = {
                    key: values for key, values in peers.items() if len(values) >= 3
                }
                info["sector_peer_count"] = max(
                    (len(values) for values in info["sector_peer_metrics"].values()),
                    default=0,
                )
            except Exception:
                info["sector_peer_metrics"] = {}
        # Quarterly statements provide dated trend context where Yahoo exposes it.
        # Their period end is not the publication date, so they are never used as
        # historical point-in-time ML features.
        try:
            info["_quarterly_income"] = ticker.quarterly_financials
        except Exception:
            info["_quarterly_income"] = None
        try:
            info["_quarterly_cashflow"] = ticker.quarterly_cashflow
        except Exception:
            info["_quarterly_cashflow"] = None
        try:
            info["_annual_income"] = ticker.income_stmt
        except Exception:
            info["_annual_income"] = None
        try:
            info["_annual_cashflow"] = ticker.cashflow
        except Exception:
            info["_annual_cashflow"] = None
        return info
    except Exception:
        return {}


NEWS_MAX_AGE_DAYS = 30
_FILLER_HEADLINE = re.compile(
    r"\b(?:etf|exchange.traded.fund|fund)\b.{0,100}\b(?:buys?|purchases?|adds?|acquires?|sells?|sold|shares|stake|holdings?)\b|"
    r"\b(?:vanguard|invesco|proshares|direxion|ishares|blackrock|state.street|spdr|first.trust)\b.{0,120}\b(?:buys?|purchases?|adds?|acquires?|sells?|sold|shares|stake|holdings?)\b|"
    r"\b(?:llc|capital|advisors?|holdings?|trust|management)\b.{0,100}\b(?:buys?|purchases?|adds?|acquires?|sells?|sold|shares|stake|holdings?)\b|"
    r"\bshares?\b.{0,50}\b(?:sold|purchased|acquired|bought|added|lifted)\b|\bstake\b.{0,70}\b(?:lifted|raised|lowered|sold|bought|added|acquired)\b|"
    r"\b(?:buys?|purchases?|adds?|acquires?|sells?|sold)\b.{0,50}\b(?:\d[\d,.]*\s+)?shares?\b",
    re.IGNORECASE,
)


def _parse_published(value):
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, timezone.utc)
    if not value or not isinstance(value, str) or value == "Date indisponible":
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = parsedate_to_datetime(value)
        except (TypeError, ValueError, OverflowError):
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _canonical_url(url):
    if not url or url == "#":
        return ""
    parts = urlsplit(url.strip())
    return urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), "", "")
    )


def _is_relevant(article, symbol, company_name):
    text = f"{article.get('title', '')} {article.get('description', '')}".casefold()
    if re.search(rf"(?<![a-z0-9]){re.escape(symbol.casefold())}(?![a-z0-9])", text):
        return True
    # Company names are often longer than stock symbols and less ambiguous.
    return any(
        len(token) >= 4
        and re.search(rf"(?<![a-z0-9]){re.escape(token.casefold())}(?![a-z0-9])", text)
        for token in re.findall(r"[\w-]+", company_name)
    )


def _clean_articles(articles, symbol, company_name, *, source_scoped=False, limit=20):
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=NEWS_MAX_AGE_DAYS)
    kept, seen_titles, seen_urls = [], set(), set()
    for article in articles:
        title = (article.get("title") or "").strip()
        published = _parse_published(article.get("publishedAt"))
        if (
            not title
            or published is None
            or published < cutoff
            or published > now + timedelta(days=1)
        ):
            continue
        if _FILLER_HEADLINE.search(f"{title} {article.get('description', '')}"):
            continue
        if not source_scoped and not _is_relevant(article, symbol, company_name):
            continue
        title_key = re.sub(r"[^a-z0-9]+", " ", title.casefold()).strip()
        url = _canonical_url(article.get("url", ""))
        if title_key in seen_titles or (url and url in seen_urls):
            continue
        seen_titles.add(title_key)
        if url:
            seen_urls.add(url)
        item = dict(article)
        item["publishedAt"] = published.isoformat()
        kept.append(item)
    kept.sort(key=lambda item: item["publishedAt"], reverse=True)
    return kept[:limit]


def fetch_news(symbol, company_name=""):
    """Return relevant, dated, deduplicated articles from the last 30 days."""
    # Yahoo Finance news needs no API key.
    try:
        raw_articles = yf.Ticker(symbol).get_news(count=40, tab="news") or []
        articles = []
        for raw in raw_articles:
            item = raw.get("content") or raw
            provider = item.get("provider") or item.get("source") or {}
            provider_name = (
                provider
                if isinstance(provider, str)
                else provider.get("displayName") or provider.get("name")
            )
            click_url = item.get("clickThroughUrl") or {}
            canonical_url = item.get("canonicalUrl") or {}
            published = (
                item.get("pubDate")
                or item.get("publishedAt")
                or item.get("providerPublishTime")
            )
            title = item.get("title")
            if title:
                articles.append(
                    {
                        "title": title,
                        "description": item.get("summary")
                        or item.get("description")
                        or "",
                        "publishedAt": published,
                        "source": {
                            "name": provider_name
                            or item.get("publisher")
                            or "Yahoo Finance"
                        },
                        "url": click_url.get("url")
                        or canonical_url.get("url")
                        or item.get("link")
                        or "#",
                    }
                )
        cleaned = _clean_articles(articles, symbol, company_name, source_scoped=True)
        if cleaned:
            return cleaned
    except Exception:
        pass

    # Public Google News RSS fallback; it does not require an API key.
    try:
        response = requests.get(
            "https://news.google.com/rss/search",
            params={
                "q": f'"{company_name}" stock OR {symbol} when:30d',
                "hl": "en-US",
                "gl": "US",
                "ceid": "US:en",
            },
            headers={"User-Agent": "AI-Stock-Analyzer/1.0"},
            timeout=12,
        )
        response.raise_for_status()
        root = ET.fromstring(response.content)
        articles = [
            {
                "title": item.findtext("title"),
                "description": item.findtext("description") or "",
                "publishedAt": item.findtext("pubDate"),
                "source": {"name": item.findtext("source") or "Google News"},
                "url": item.findtext("link") or "#",
            }
            for item in root.findall("./channel/item")
        ]
        cleaned = _clean_articles(articles, symbol, company_name, limit=20)
        if cleaned:
            return cleaned
    except (requests.RequestException, ET.ParseError, ValueError):
        pass

    key = os.getenv("NEWSAPI_KEY", "")
    if not key:
        try:
            import streamlit as st

            key = st.secrets.get("NEWSAPI_KEY", "")
        except Exception:
            key = ""
    if key:
        try:
            recent_from = (
                (datetime.now(timezone.utc) - timedelta(days=NEWS_MAX_AGE_DAYS))
                .date()
                .isoformat()
            )
            response = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": f'"{symbol}" OR "{company_name}"',
                    "language": "en",
                    "from": recent_from,
                    "sortBy": "publishedAt",
                    "pageSize": 40,
                    "apiKey": key,
                },
                timeout=12,
            )
            response.raise_for_status()
            payload = response.json()
            raw = payload.get("articles", []) if payload.get("status") == "ok" else []
            return _clean_articles(raw, symbol, company_name, limit=20)
        except (requests.RequestException, ValueError):
            pass
    return []
