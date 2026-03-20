"""
============================================================
nlp_utils.py  –  Text Preprocessing Utilities
============================================================
Provides helper functions for cleaning, tokenizing, and
normalizing user input before it is fed to the ML model.

Uses NLTK for tokenization and lemmatization.
============================================================
"""

import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# ── Ensure required NLTK data is available ────────────────
# These are small, offline-friendly downloads.
for resource in ["punkt", "punkt_tab", "wordnet", "omw-1.4", "stopwords"]:
    try:
        nltk.data.find(f"tokenizers/{resource}" if "punkt" in resource else f"corpora/{resource}")
    except LookupError:
        nltk.download(resource, quiet=True)

# ── Initialize lemmatizer ─────────────────────────────────
lemmatizer = WordNetLemmatizer()


def clean_text(text: str) -> str:
    """
    Remove special characters, convert Tanglish to English,
    and collapse whitespace.
    """
    text = text.lower().strip()
    
    # Tanglish normalization
    tanglish_map = {
        r"\benna\b": "what",
        r"\byaar\b": "who",
        r"\bpathi\b": "",
        r"\bsollu\b": ""
    }
    for t_word, e_word in tanglish_map.items():
        text = re.sub(t_word, e_word, text)
        
    text = re.sub(r"[^a-z0-9\s'?!.,]", "", text)   # keep useful chars
    text = re.sub(r"\s+", " ", text)                 # collapse whitespace
    return text


def tokenize(text: str) -> list:
    """
    Tokenize text into a list of words using NLTK.
    """
    return word_tokenize(text)


def lemmatize_tokens(tokens: list) -> list:
    """
    Reduce each token to its base/root form.
    Example: 'running' → 'running' → 'run'
    """
    return [lemmatizer.lemmatize(token) for token in tokens]


def preprocess(text: str) -> str:
    """
    Full preprocessing pipeline:
      1. Clean the raw text
      2. Tokenize
      3. Remove stopwords
      4. Lemmatize
      5. Rejoin into a single string (for TF-IDF)
    """
    cleaned = clean_text(text)
    tokens = tokenize(cleaned)
    stop_words = set(stopwords.words("english"))
    # Keep some important words that might be stopwords but are useful for intents like "who", "what"
    important = {"who", "what", "how", "why", "where", "when", "is", "are"}
    filtered_tokens = [w for w in tokens if w not in stop_words or w in important]
    lemmatized = lemmatize_tokens(filtered_tokens)
    return " ".join(lemmatized)
