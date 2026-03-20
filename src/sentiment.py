"""
============================================================
sentiment.py  –  Sentiment Analysis Module
============================================================
Uses NLTK's VADER (Valence Aware Dictionary and sEntiment
Reasoner) for rule-based sentiment analysis.

VADER works offline and is lightweight – perfect for a
demo-friendly project.
============================================================
"""

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# ── Ensure VADER lexicon is available ─────────────────────
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon", quiet=True)

# ── Initialize the analyzer once ──────────────────────────
_analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> dict:
    """
    Analyze the sentiment of the given text.

    Returns a dict with:
        label    : 'positive', 'negative', or 'neutral'
        compound : VADER compound score  (-1 to +1)
        scores   : full VADER dict (neg, neu, pos, compound)
    """
    scores = _analyzer.polarity_scores(text)
    compound = scores["compound"]

    # Classify using standard VADER thresholds
    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    return {
        "label": label,
        "compound": compound,
        "scores": scores,
    }


def get_sentiment_label(text: str) -> str:
    """Convenience function – returns just the label string."""
    return analyze_sentiment(text)["label"]


def get_sentiment_emoji(label: str) -> str:
    """Map a sentiment label to an emoji for the UI."""
    mapping = {
        "positive": "😊",
        "negative": "😟",
        "neutral": "😐",
    }
    return mapping.get(label, "")
