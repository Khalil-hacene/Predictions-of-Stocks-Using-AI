"""Financial news sentiment with FinBERT and a transparent lexical fallback."""

from datetime import datetime
from datetime import timezone
import html
import math
import os
import re
from difflib import SequenceMatcher
from pathlib import Path
from importlib.util import find_spec
import streamlit as st
from src.i18n import t

_HF_CACHE = Path(__file__).resolve().parent.parent / "data" / "huggingface-cache"
os.environ.setdefault("HF_HOME", str(_HF_CACHE))

_FILLER_HEADLINE = re.compile(
    r"\b(?:etf|exchange.traded.fund|fund)\b.{0,100}\b(?:buys?|purchases?|adds?|acquires?|sells?|sold|shares|stake|holdings?)\b|"
    r"\b(?:vanguard|invesco|proshares|direxion|ishares|blackrock|state.street|spdr|first.trust)\b.{0,120}\b(?:buys?|purchases?|adds?|acquires?|sells?|sold|shares|stake|holdings?)\b|"
    r"\b(?:llc|capital|advisors?|holdings?|trust|management)\b.{0,100}\b(?:buys?|purchases?|adds?|acquires?|sells?|sold|shares|stake|holdings?)\b|"
    r"\bshares?\b.{0,50}\b(?:sold|purchased|acquired|bought|added|lifted)\b|\bstake\b.{0,70}\b(?:lifted|raised|lowered|sold|bought|added|acquired)\b|"
    r"\b(?:buys?|purchases?|adds?|acquires?|sells?|sold)\b.{0,50}\b(?:\d[\d,.]*\s+)?shares?\b",
    re.IGNORECASE,
)


@st.cache_resource(show_spinner=False)
def _model():
    """Load FinBERT once and preserve a useful reason when it cannot load."""
    if find_spec("torch") is None or find_spec("transformers") is None:
        return None, "missing_dependencies"
    try:
        from transformers import (
            AutoModelForSequenceClassification,
            AutoTokenizer,
            pipeline,
        )

        model_id = "ProsusAI/finbert"
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_id, local_files_only=True)
            model = AutoModelForSequenceClassification.from_pretrained(
                model_id, local_files_only=True
            )
        except Exception:
            # If the model is not cached yet, download it on the first use.
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            model = AutoModelForSequenceClassification.from_pretrained(model_id)
        return (
            pipeline(
                "text-classification", model=model, tokenizer=tokenizer, truncation=True
            ),
            "ready",
        )
    except Exception as exc:
        return None, f"load_error:{type(exc).__name__}: {exc}"


POSITIVE = {
    "beat",
    "beats",
    "beating",
    "benefit",
    "beneficiary",
    "best",
    "better",
    "boost",
    "boom",
    "bullish",
    "buy",
    "buys",
    "gain",
    "gains",
    "growth",
    "impress",
    "impressed",
    "impressive",
    "improve",
    "improved",
    "innovation",
    "leader",
    "outperform",
    "positive",
    "profit",
    "profitable",
    "record",
    "rise",
    "rises",
    "rising",
    "robust",
    "solid",
    "strong",
    "surge",
    "upgrade",
    "upside",
    "win",
    "wins",
    "expansion",
    "expanding",
    "demand",
    "momentum",
    "partnership",
    "advantage",
    "hausse",
    "croissance",
    "bénéfice",
    "solide",
    "fort",
    "forte",
    "positif",
    "positive",
    "surperformance",
}
NEGATIVE = {
    "bearish",
    "concern",
    "concerns",
    "decline",
    "declines",
    "declining",
    "drop",
    "drops",
    "fell",
    "fall",
    "weak",
    "weaker",
    "weakness",
    "loss",
    "losses",
    "lawsuit",
    "miss",
    "missed",
    "negative",
    "plunge",
    "plunged",
    "risk",
    "risks",
    "slide",
    "slides",
    "slid",
    "sliding",
    "slump",
    "slumped",
    "underperform",
    "downgrade",
    "downgraded",
    "cut",
    "cuts",
    "lower",
    "lowers",
    "pressure",
    "sell",
    "selling",
    "struggle",
    "struggles",
    "headwind",
    "uncertainty",
    "disappointing",
    "falling",
    "baisse",
    "perte",
    "faible",
    "négatif",
}
NEGATIONS = {
    "no",
    "not",
    "never",
    "without",
    "neither",
    "hardly",
    "pas",
    "aucun",
    "aucune",
    "sans",
}


def _tokens(text):
    clean_text = re.sub(r"<[^>]+>", " ", html.unescape(text))
    words = re.findall(r"[a-zà-ÿ]+", clean_text.lower())
    normalized = []
    for word in words:
        if word.endswith("ies") and len(word) > 5:
            word = word[:-3] + "y"
        elif word.endswith("ing") and len(word) > 5:
            word = word[:-3]
        elif word.endswith("ed") and len(word) > 4:
            word = word[:-2]
        elif word.endswith("s") and len(word) > 4 and not word.endswith("ss"):
            word = word[:-1]
        normalized.append(word)
    # Restore common stems created by the lightweight suffix handling.
    return [
        (
            {
                "ris": "rise",
                "sur": "surge",
                "slid": "slide",
                "beneficiar": "beneficiary",
            }.get(w, w)
        )
        for w in normalized
    ]


def _lexical_score(text, lang="fr"):
    words = _tokens(text)
    positive = negative = 0
    for i, word in enumerate(words):
        sign = 1 if word in POSITIVE else -1 if word in NEGATIVE else 0
        if sign:
            context = words[max(0, i - 3) : i]
            if any(w in NEGATIONS for w in context):
                sign *= -1
            if sign > 0:
                positive += 1
            else:
                negative += 1
    # Bound each headline score so one dramatic word cannot dominate the set.
    score = max(-1.0, min(1.0, (positive - negative) * 0.45))
    label = (
        t(lang, "positive_label")
        if score > 0.15
        else t(lang, "negative_label") if score < -0.15 else t(lang, "neutral_label")
    )
    return score, label


def _score(text, lang="fr"):
    model, status = _model()
    if model is not None:
        try:
            result = model(text[:1500])[0]
            label = result["label"].lower()
            score = float(result["score"]) * (
                1 if label == "positive" else -1 if label == "negative" else 0
            )
            label_local = {
                "positive": t(lang, "positive_label"),
                "negative": t(lang, "negative_label"),
                "neutral": t(lang, "neutral_label"),
            }.get(label, t(lang, "neutral_label"))
            return score, label_local, "FinBERT", "ready"
        except Exception as exc:
            status = f"inference_error:{type(exc).__name__}: {exc}"
    score, label = _lexical_score(text, lang)
    return score, label, "Lexique", status


def _detect_language(text):
    """Return a stable ISO language code, or unknown for very short text."""
    try:
        from langdetect import DetectorFactory, detect

        DetectorFactory.seed = 0
        return detect(text)
    except Exception:
        return "unknown"


def analyze_news(articles, lang="fr"):
    if not articles:
        return {
            "count": 0,
            "score": 0,
            "label": t(lang, "unavailable"),
            "positive": 0,
            "neutral": 0,
            "negative": 0,
            "articles": [],
            "method": t(lang, "unavailable"),
            "message": t(lang, "recent_none"),
            "trend": [],
        }
    out = []
    statuses = set()
    seen_titles = []
    seen_urls = set()
    now = datetime.now(timezone.utc)
    source_quality = {
        "reuters": 1.0,
        "associated press": 1.0,
        "ap news": 1.0,
        "bloomberg": 0.98,
        "financial times": 0.98,
        "wall street journal": 0.95,
        "cnbc": 0.88,
        "yahoo finance": 0.82,
        "google news": 0.70,
    }
    for a in articles:
        title = a.get("title") or "Titre indisponible"
        if _FILLER_HEADLINE.search(title):
            continue
        title_key = re.sub(r"[^a-z0-9]+", " ", title.casefold()).strip()
        url = a.get("url", "#") or "#"
        url_key = url.split("?", 1)[0].rstrip("/").casefold()
        if title_key and (
            title_key in seen_titles
            or any(
                SequenceMatcher(None, title_key, old).ratio() >= 0.94
                for old in seen_titles
            )
        ):
            continue
        if url_key != "#" and url_key in seen_urls:
            continue
        seen_titles.append(title_key)
        if url_key != "#":
            seen_urls.add(url_key)
        content = title + ". " + (a.get("description") or "")
        article_language = _detect_language(title)
        value, label, method, status = _score(content, lang)
        statuses.add(status)
        date = a.get("publishedAt") or "Date indisponible"
        try:
            date = datetime.fromisoformat(date.replace("Z", "+00:00")).strftime(
                "%d/%m/%Y à %H:%M UTC" if lang == "fr" else "%Y-%m-%d %H:%M UTC"
            )
        except (ValueError, AttributeError):
            pass
        source = a.get("source") or {}
        if isinstance(source, str):
            source_name = source
        else:
            source_name = source.get("name", "Source inconnue")
        try:
            published = datetime.fromisoformat(
                str(a.get("publishedAt", "")).replace("Z", "+00:00")
            )
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)
            age_days = max(
                0, (now - published.astimezone(timezone.utc)).total_seconds() / 86400
            )
        except (ValueError, TypeError):
            published = None
            age_days = 30
        source_lower = source_name.casefold()
        quality = next(
            (weight for name, weight in source_quality.items() if name in source_lower),
            0.65,
        )
        language_factor = 0.5 if article_language not in ("en", "unknown") else 1.0
        weight = math.exp(-age_days / 10) * quality * language_factor
        out.append(
            {
                "title": title,
                "date": date,
                "source": source_name,
                "url": url,
                "score": value,
                "label": label,
                "method": method,
                "language": article_language,
                "weight": weight,
                "published": published,
                "quality_weight": quality,
                "language_weight": language_factor,
            }
        )
    if not out:
        return {
            "count": 0,
            "score": 0,
            "label": t(lang, "unavailable"),
            "positive": 0,
            "neutral": 0,
            "negative": 0,
            "articles": [],
            "method": t(lang, "unavailable"),
            "message": t(lang, "recent_none"),
            "trend": [],
        }
    total_weight = sum(a["weight"] for a in out)
    avg = (
        sum(a["score"] * a["weight"] for a in out) / total_weight if total_weight else 0
    )
    for article in out:
        article["impact"] = abs(
            article["score"] * article["weight"] / max(total_weight, 1e-12)
        )
    by_day = {}
    for article in out:
        if article["published"]:
            day = article["published"].date().isoformat()
            by_day.setdefault(day, []).append(article)
    trend = [
        {
            "date": day,
            "score": sum(a["score"] * a["weight"] for a in group)
            / sum(a["weight"] for a in group),
            "articles": len(group),
        }
        for day, group in sorted(by_day.items())
    ]
    methods = {item["method"] for item in out}
    method = (
        "FinBERT"
        if methods == {"FinBERT"}
        else (
            t(lang, "lexicon")
            if methods == {"Lexique"}
            else t(lang, "finbert_fallback")
        )
    )
    issue = next((status for status in statuses if status != "ready"), None)
    return {
        "count": len(out),
        "score": avg,
        "label": (
            t(lang, "positive_label")
            if avg > 0.15
            else t(lang, "negative_label") if avg < -0.15 else t(lang, "neutral_label")
        ),
        "positive": sum(a["label"] == t(lang, "positive_label") for a in out),
        "negative": sum(a["label"] == t(lang, "negative_label") for a in out),
        "neutral": sum(a["label"] == t(lang, "neutral_label") for a in out),
        "articles": out,
        "top_articles": sorted(out, key=lambda item: item["impact"], reverse=True)[:5],
        "trend": trend,
        "method": method,
        "model_status": issue or "ready",
        "non_english_count": sum(a["language"] not in ("en", "unknown") for a in out),
        "message": "",
    }
